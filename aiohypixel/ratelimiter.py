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

from asyncio import AbstractEventLoop, Event


class RateLimiter:
    """A ratelimit handler for API requests to avoid 429's.

    Attributes
    ----------
    loop : AbstractEventLoop
        The asyncio event loop the rate limiter will use.
    """

    def __init__(
        self,
        loop: AbstractEventLoop,
    ) -> None:
        self.loop = loop

        self.lock = Event()
        self.lock.set()

    async def acquire(self) -> None:
        """Acquires the rate limit lock."""

        await self.lock.wait()

    def release(self, after: int = 0) -> None:
        """Releases the lock after the given delay."""

        self.lock.clear()
        self.loop.call_later(after, self.lock.set)
