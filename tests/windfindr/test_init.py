"""Tests for windfindr"""

import unittest
from unittest import mock

from src.windfindr import Windfindr

# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):  # pylint: disable=unused-argument
    """mocked_requests_get"""

    class MockResponse:  # pylint: disable=too-few-public-methods
        """MockResponse"""

        def __init__(self, text, status_code):
            """init"""

            self.text = text
            self.status_code = status_code

        def json(self):
            """json"""

            return self.text

    if args[0] == 'https://api.windfinder.com/v2/spots/br854/tides/':
        return MockResponse([{"dtl":"2022-01-01T00:00:00-03:00","th":0.5,"tp":"low"}], 200)
    if args[0] == 'https://api.windfinder.com/v2/spots/70933/tides/':
        return MockResponse([{"dtl":"2022-01-01T12:00:00-03:00","th":1.5,"tp":"high"}], 200)
    if args[0] == 'https://www.windfinder.com':
        return MockResponse("<script>window.API_TOKEN = 'token';</script>", 200)

    return MockResponse(None, 404)

def mocked_httpx_client(*args, **kwargs):  # pylint: disable=unused-argument
    """mocked_httpx_get"""

    class MockClient:  # pylint: disable=too-few-public-methods
        """MockClient"""

        async def get(self, *args, **kwargs):
            """get"""
            return mocked_requests_get(*args, **kwargs)

    return MockClient()

class WindfindrTestCase(unittest.IsolatedAsyncioTestCase):
    """WindfindrTestCase"""

    def test_default_parameters(self):  # pylint: disable=bad-option-value, useless-option-value, no-self-use
        """Test default parameters"""
        api = Windfindr()

        assert api._attr_version == "1.0"  # pylint: disable=protected-access
        assert api._attr_customer == "wfweb"  # pylint: disable=protected-access
        assert api._attr_token is None  # pylint: disable=protected-access

    @mock.patch('src.windfindr.request.AsyncClient', side_effect=mocked_httpx_client)
    async def test_tides_with_default_parameters_same_token(self, mock_get):  # pylint: disable=unused-argument, bad-option-value, useless-option-value, no-self-use
        """Test tides with default parameters"""
        api = Windfindr()

        token = api._attr_token  # pylint: disable=protected-access
        assert token is None

        result1 = await api.tides("br854")

        token = api._attr_token  # pylint: disable=protected-access
        assert not token is None
        assert result1["available"] is True

        result2 = await api.tides("70933")

        assert token == api._attr_token  # pylint: disable=protected-access
        assert result2["available"] is True

        result2 = await api.tides("br854")

        assert token == api._attr_token  # pylint: disable=protected-access
        assert result2["available"] is True
        assert result1 == result2

if __name__ == '__main__':
    unittest.main()
