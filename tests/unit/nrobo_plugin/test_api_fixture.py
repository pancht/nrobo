import pytest

from nrobo.api_wrappers.api_wrapper import ApiWrapper

pytestmark = [pytest.mark.api]


def test_api_fixture_available(api):
    """
    Ensure that the `api` fixture is correctly initialized.
    """
    assert api is not None, "API fixture should not be None"
    assert hasattr(api, "get"), "API fixture should have `.get()` method"
    assert callable(api.get), "API `.get()` method should be callable"


@pytest.mark.parametrize("auth_type", ["bearer", "basic", "oauth", "none"])
def test_api_fixture_config_variants(monkeypatch, auth_type, api):
    """
    Test that the `api` fixture returns an ApiWrapper instance based on auth type.
    """

    # Set environment variables depending on auth type
    monkeypatch.setenv("NROBO_API_AUTH_METHOD", auth_type)

    if auth_type == "bearer":
        monkeypatch.setenv("NROBO_BEARER_TOKEN", "mock-token")

    elif auth_type == "basic":
        monkeypatch.setenv("NROBO_BASIC_AUTH", "username:password")

    elif auth_type == "oauth":
        monkeypatch.setenv("NROBO_OAUTH2_CLIENT_ID", "client123")
        monkeypatch.setenv("NROBO_OAUTH2_CLIENT_SECRET", "secret123")

    # The `api` fixture is automatically provided by pytest
    assert isinstance(api, ApiWrapper), f"{auth_type} config should return ApiWrapper"
