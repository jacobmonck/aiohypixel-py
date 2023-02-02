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


class AIOHypixelException(Exception):
    """Base exception class for aiohypixel-py

    Use this if you want to catch any exception raised by the library, not
    recommended though.
    """

    pass


class HTTPException(AIOHypixelException):
    """Base exception raised when an HTTP request fails."""

    pass


class DataMissing(HTTPException):
    """Raised when a 400 status code occurs."""

    pass


class DataInvalid(HTTPException):
    """Raised when a 422 status code occurs."""

    pass


class TooManyRequests(HTTPException):
    """Raised when a 429 status code occurs."""


class Forbidden(HTTPException):
    """Raised when a 403 status code occurs."""

    pass


class HypixelServerError(HTTPException):
    """Raised when a 500 server error occurs"""

    pass
