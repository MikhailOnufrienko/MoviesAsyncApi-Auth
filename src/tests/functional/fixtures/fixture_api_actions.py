import aiohttp
import pytest

from tests.functional.utils import models


@pytest.fixture
def make_get_request(session_client: aiohttp.ClientSession) -> callable:
    """Send get request to api endpoint and return the response."""

    async def inner(url: str, params: dict = {}) -> models.HTTPResponse:
        """Function logic."""

        async with session_client.get(url=url, params=params) as response:
            if response.content_type == 'application/json':
                body = await response.json()
            else:
                body = await response.text()
            status = response.status

            return models.HTTPResponse(
                body=body, status=status
            )

    return inner
