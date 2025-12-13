import pytest
import requests
import requests_mock
from requests.adapters import HTTPAdapter

from nrobo.api_wrappers.api_wrapper import ApiWrapper


@pytest.fixture(scope="session")
def base_url():
    return "https://api.test.local"


# ---------------------------------------------------------
# HTTP Method Tests (Basic Connectivity + Status)
# ---------------------------------------------------------
@pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete", "head", "options"])
def test_all_http_methods(base_url, method):
    with requests_mock.Mocker() as m:
        url = f"{base_url}/resource"
        m.register_uri(method.upper(), url, json={"ok": True}, status_code=200)

        wrapper = ApiWrapper(base_url)
        response = getattr(wrapper, method)("resource")

        assert isinstance(response, requests.Response)
        assert response.json() == {"ok": True}
        assert response.status_code == 200


# ---------------------------------------------------------
# Bearer Token Header Injection
# ---------------------------------------------------------
def test_bearer_auth_header(base_url):
    token = "secret-token"  # nosec: B105
    wrapper = ApiWrapper(base_url, bearer_token=token)

    header = wrapper.session.headers.get("Authorization")
    assert header == f"Bearer {token}"


# ---------------------------------------------------------
# Basic Auth Injection
# ---------------------------------------------------------
def test_basic_auth_header(base_url):
    wrapper = ApiWrapper(base_url, basic_auth=("user", "pass"))
    auth = wrapper.session.auth
    assert auth == ("user", "pass")


# ---------------------------------------------------------
# Assertion Helpers
# ---------------------------------------------------------
def test_assert_status_helper():
    class DummyResponse:
        status_code = 201

    ApiWrapper.assert_status(DummyResponse(), 201)


def test_assert_json_key_and_value_helpers():
    class DummyResponse:
        def json(self):
            return {"id": 100, "name": "X"}

    resp = DummyResponse()
    ApiWrapper.assert_json_key(resp, "id")
    ApiWrapper.assert_json_value(resp, "name", "X")


# ---------------------------------------------------------
# OAuth Client Credentials Token Fetch
# ---------------------------------------------------------
def test_fetch_access_token(base_url, monkeypatch):
    token_data = {"access_token": "abc", "refresh_token": "xyz", "expires_in": 60}

    with requests_mock.Mocker() as m:
        m.post(f"{base_url}/oauth", json=token_data)

        wrapper = ApiWrapper(  # nosec: B106
            base_url,
            oauth_token_url=f"{base_url}/oauth",
            oauth_client_id="cid",
            oauth_client_secret="csecret",
        )

        # Should set header based on mock
        assert wrapper.session.headers["Authorization"] == "Bearer abc"
        assert wrapper._access_token == "abc"  # nosec: B105
        assert wrapper._refresh_token == "xyz"  # nosec: B105


# ---------------------------------------------------------
# Auto-refresh on 401 with refresh token
# ---------------------------------------------------------
def test_refresh_on_401(base_url):
    token_data_2 = {"access_token": "new", "refresh_token": "refresh2", "expires_in": 60}

    with requests_mock.Mocker() as m:
        # Only refresh token response is needed
        m.post(f"{base_url}/oauth", json=token_data_2)

        # Simulate 401 first, then 200 after refresh
        m.get(
            f"{base_url}/secure", [{"status_code": 401}, {"json": {"ok": True}, "status_code": 200}]
        )

        wrapper = ApiWrapper(  # nosec: B106
            base_url,
            oauth_token_url=f"{base_url}/oauth",
            oauth_client_id="cid",
            oauth_client_secret="csecret",  # nosec: B106
            oauth_refresh_token="refresh",
        )

        response = wrapper.get("secure")
        assert response.status_code == 200
        assert response.json()["ok"] is True
        assert wrapper.session.headers["Authorization"] == "Bearer new"


# ---------------------------------------------------------
# 401 Without Refresh Token → Should NOT refresh
# ---------------------------------------------------------
def test_401_without_refresh_token_error(base_url):
    with requests_mock.Mocker() as m:
        m.post(f"{base_url}/oauth", json={"access_token": "abc"})
        m.get(f"{base_url}/error", status_code=401)

        wrapper = ApiWrapper(  # nosec: B106
            base_url,
            oauth_token_url=f"{base_url}/oauth",
            oauth_client_id="cid",
            oauth_client_secret="csecret",
        )

        response = wrapper.get("error")
        assert response.status_code == 401


# ---------------------------------------------------------
# _send_request Exception Path
# ---------------------------------------------------------
def test_send_request_raises(monkeypatch, base_url):
    wrapper = ApiWrapper(base_url)

    # Simulate request failure
    def fail(*args, **kwargs):
        raise requests.RequestException("fail")

    monkeypatch.setattr(wrapper.session, "request", fail)

    with pytest.raises(requests.RequestException):
        wrapper.get("anything")


# ---------------------------------------------------------
# Retry Configuration Applied
# ---------------------------------------------------------
def test_configure_retries_applied(base_url):
    wrapper = ApiWrapper(base_url, max_retries=1)
    adapter = wrapper.session.get_adapter("http://")
    assert isinstance(adapter, HTTPAdapter)


# ---------------------------------------------------------
# Allure attachment is noop when Allure not installed
# ---------------------------------------------------------
def test_attach_to_allure_no_allure(monkeypatch, base_url):
    wrapper = ApiWrapper(base_url)
    # doesn't error when allure is None
    wrapper._attach_to_allure("GET", base_url, requests.Response(), {})
