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

from asyncio import AbstractEventLoop, get_event_loop
from typing import Optional

from aiohttp import ClientSession

from .http import HTTPClient
from .types import Key

BASE_URL = "https://api.hypixel.net"


class AIOHypixelClient:
    """A client that makes HTTP requests to Hypixel's API.

    Attributes
    ----------
    token : str
        The API key you want to use to make requests.
    loop : Optional[AbstractEventLoop]
        The AsyncIO event loop you would like to client to use, if none is
        provided the client will call get_event_loop().
    session : Optional[ClientSession]
        The AIOHTTP ClientSession you would like to use, if none is provided
        the client will create a session for you.
    """

    def __init__(
        self,
        token: str,
        *,
        loop: Optional[AbstractEventLoop] = None,
        session: Optional[ClientSession] = None
    ) -> None:
        self.token = token
        self.loop = loop or get_event_loop()
        self._session = session or ClientSession()

        self.http = HTTPClient(token, self.loop, self._session)

    async def get_key_info(self) -> Key:
        """Get current status of your API token. Look at the Key object see what
        data is returned.

        Link to Hypixel's API docs for this endpoint.
        https://api.hypixel.net/#tag/API/paths/~1key/get

        Returns
        -------
        Key
            The API's key object.
        """
        response: dict = await self.http.request("/key")

        data = response["record"]

        return Key(
            data["key"],
            data["owner"],
            data["limit"],
            data["queriesInPastMin"],
            data["totalQueries"],
        )
