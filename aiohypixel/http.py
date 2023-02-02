"""
MIT License

Copyright (c) 2023-Present JacobMonck

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from asyncio import AbstractEventLoop
from json import JSONDecodeError
from typing import Any, ClassVar, Literal, Optional, Union, get_args

from aiohttp import ClientResponse, ClientSession

import aiohypixel

from .errors import (
    DataInvalid,
    DataMissing,
    Forbidden,
    HTTPException,
    HypixelServerError,
    TooManyRequests,
)
from .ratelimiter import RateLimiter

ResponseFormat = Literal["raw", "text", "json", "auto", "response"]


class HTTPClient:
    BASE_URL: ClassVar[str] = "https://api.hypixel.net"
    ERRORS: ClassVar[dict[Union[int, str], Exception]] = {
        "_": HTTPException,
        400: DataMissing,
        403: Forbidden,
        422: DataInvalid,
        429: TooManyRequests,
    }

    def __init__(
        self,
        token: str,
        loop: AbstractEventLoop,
        session: Optional[ClientSession] = None,
        retry_attempts: int = 3,
    ) -> None:
        """An HTTP client for making requests to the Hypixel API.

        Parameters
        ----------
        token : str
            The API token you want the client to use.
        loop : AbstractEventLoop
            The event loop the client will use.
        session : Optional[ClientSession]
            The ClientSession the library will use, if none is provided it will use
            create one.
        retry_attempts : int = 3
            The amount of attempts the client will attempt to make if it fails to
            make a request.
        """

        self.session = session or ClientSession(loop=loop)
        self.retry_attempts = retry_attempts

        self.headers = {
            "API-Key": token,
            "User-Agent": f"aiohypixel-py client, version: {aiohypixel.__version__}",
        }

        self.ratelimiter = RateLimiter(loop)

    @staticmethod
    async def response_as(
        response: ClientResponse, response_format: ResponseFormat = "json"
    ) -> Union[bytes, str, dict, ClientResponse]:
        """Allows for a variety of different response formats.

        Parameters
        ----------
        response : ClientResponse
            The API's response.
        response_format : ResponseFormat
            The type of format you want to receive from the API.

        Returns
        -------
        Union[bytes, str, dict, ClientResponse]
        """

        if response_format == "raw":
            return await response.read()
        elif response_format == "text":
            return await response.text()
        elif response_format == "json":
            return await response.json()
        elif response_format == "auto":
            try:
                return await response.json()
            except JSONDecodeError:
                return await response.text()
        elif response_format == "response":
            return response
        else:
            raise ValueError(
                f"Format must be one of the following: {get_args(ResponseFormat)}"
            )

    async def request(
        self,
        endpoint: str,
        *,
        response_format: Optional[ResponseFormat] = "json",
        **params,
    ) -> Any:
        """Makes an API request to Hypixel's API

        Parameters
        ----------
        endpoint : str
            The endpoint the request is made to.
        **params : dict[str, Any]
            Query parameters.

        Other Parameters
        ----------------
        response_format : Optional[ResponseFormat] = "json"
            The response format you want the request to be returned in.

        Returns
        -------
        Any
            This could be an exception or a response object.
        """

        status: Optional[int] = None
        response: Optional[ClientResponse] = None

        for attempt in range(self.retry_attempts):
            await self.ratelimiter.acquire()

            response = await self.session.get(
                self.BASE_URL + endpoint, params=params, headers=self.headers
            )

            status = response.status
            headers = response.headers
            print(response)

            rl_remaining_requests = int(headers.get("ratelimit-remaining", 0))  # type: ignore
            rl_reset_after = int(
                headers.get("ratelimit-reset", headers.get("retry-after"))
            )
            rl_sleep_for = 0

            if rl_remaining_requests == 0 and status != 429:
                rl_sleep_for = rl_reset_after

            if 200 <= status < 300:
                self.ratelimiter.release(rl_sleep_for)
                return await self.response_as(response, response_format)

            if status == 429:
                rl_unlock_after = int(headers.get("retry-after"))
                self.ratelimiter.release(rl_unlock_after)
            elif status >= 500:
                # Increases back-off time for every request attempt.
                rl_sleep_for = 1 + attempt * 2
            else:
                self.ratelimiter.release(rl_sleep_for)
                raise self.ERRORS.get(status, self.ERRORS["_"])(response)

            if attempt == self.retry_attempts - 1:
                self.ratelimiter.release(rl_sleep_for)
                continue

        self.ratelimiter.release()

        if status >= 500:
            raise HypixelServerError()

        raise self.ERRORS.get(status, self.ERRORS["_"])(response)

    async def close(self) -> None:
        """Closes the client gracefully."""

        await self.session.close()
