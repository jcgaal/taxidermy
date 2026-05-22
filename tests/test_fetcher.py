import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.fetcher import fetch_url


def _mock_response(status_code=200, text="<html>ok</html>"):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.text = text
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        http_err = requests.exceptions.HTTPError(response=resp)
        resp.raise_for_status.side_effect = http_err
    return resp


def test_successful_fetch():
    with patch("requests.get", return_value=_mock_response(200)) as mock_get:
        response = fetch_url("https://example.com/", max_retries=1)
        assert response.status_code == 200
        mock_get.assert_called_once()


def test_404_raises_immediately():
    with patch("requests.get", return_value=_mock_response(404)) as mock_get:
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_url("https://example.com/missing", max_retries=3)
        # Should NOT retry on 404
        assert mock_get.call_count == 1


def test_403_raises_immediately():
    with patch("requests.get", return_value=_mock_response(403)) as mock_get:
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_url("https://example.com/forbidden", max_retries=3)
        assert mock_get.call_count == 1


def test_network_error_retries():
    with patch(
        "requests.get",
        side_effect=requests.exceptions.ConnectionError("timeout"),
    ) as mock_get:
        with pytest.raises(requests.exceptions.ConnectionError):
            fetch_url("https://example.com/", max_retries=3, timeout=1)
        assert mock_get.call_count == 3


def test_500_retries_and_raises():
    with patch("requests.get", return_value=_mock_response(500)) as mock_get:
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_url("https://example.com/", max_retries=2)
        assert mock_get.call_count == 2
