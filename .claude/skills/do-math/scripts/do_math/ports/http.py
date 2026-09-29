"""HTTP port: send one prepared external request and return its status and exact body.

A redirect is refused (ValueError); an error status is returned, not raised.
"""
from typing import Protocol


class Http(Protocol):
    def request(self, request: dict, header: list, timeout: int) -> dict:
        """``{"http_status": int, "body": bytes}`` for ``request`` sent with extra ``header`` pairs."""
