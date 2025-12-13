import json
import time
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from nrobo.helpers.logging_helper import get_logger

try:
    import allure
except ImportError:
    allure = None

logger = get_logger("nRobo:API")


class ApiWrapper:
    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        max_retries: int = 2,
        bearer_token: Optional[str] = None,
        basic_auth: Optional[tuple] = None,
        oauth_token_url: Optional[str] = None,
        oauth_client_id: Optional[str] = None,
        oauth_client_secret: Optional[str] = None,
        oauth_refresh_token: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self._configure_retries(max_retries)

        # OAuth data
        self.oauth_token_url = oauth_token_url
        self.oauth_client_id = oauth_client_id
        self.oauth_client_secret = oauth_client_secret
        self.oauth_refresh_token = oauth_refresh_token

        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = oauth_refresh_token
        self._token_expiry: Optional[float] = None

        # Authentication setup
        if bearer_token:
            self.session.headers.update({"Authorization": f"Bearer {bearer_token}"})
        elif basic_auth:
            self.session.auth = basic_auth
        elif oauth_token_url and oauth_client_id and oauth_client_secret:
            # If refresh token passed, use that; otherwise fetch token directly
            if self.oauth_refresh_token:
                self._refresh_access_token()
            else:
                self._fetch_access_token()

        logger.info(f"API client initialized for {self.base_url}")

    # -------------------------------------------------------------------------
    # HTTP Methods
    # -------------------------------------------------------------------------
    def get(self, endpoint: str, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs):
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs):
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)

    def head(self, endpoint: str, **kwargs):
        return self._request("HEAD", endpoint, **kwargs)

    def options(self, endpoint: str, **kwargs):
        return self._request("OPTIONS", endpoint, **kwargs)

    # -------------------------------------------------------------------------
    # Core request logic (handles refresh automatically)
    # -------------------------------------------------------------------------
    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        attempt = 0

        expected_status = kwargs.pop("expected_status", None)  # <- extract custom param

        while True:
            response = self._send_request(method, url, **kwargs)

            # Auto-refresh on 401 or expired token
            if response.status_code == 401 and self.oauth_refresh_token and attempt == 0:
                logger.info("401 detected — attempting refresh token request...")
                self._refresh_access_token()
                attempt += 1
                continue

            if expected_status is not None:
                self.assert_status(response, expected_status)  # <- custom validation

            return response

    def _send_request(self, method: str, url: str, **kwargs):
        start_time = time.time()
        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

        duration = round(time.time() - start_time, 3)
        logger.info(f"[{method}] {url} => {response.status_code} ({duration}s)")

        self._attach_to_allure(method, url, response, kwargs)
        return response

    # -------------------------------------------------------------------------
    # OAuth Management
    # -------------------------------------------------------------------------
    def _fetch_access_token(self):
        """Fetch a new access token using client credentials."""
        logger.info("Fetching OAuth token via client credentials…")
        data = {
            "grant_type": "client_credentials",
            "client_id": self.oauth_client_id,
            "client_secret": self.oauth_client_secret,
        }
        self._perform_token_fetch(data)

    def _refresh_access_token(self):
        """Refresh access token using an existing refresh token."""
        if not self.oauth_refresh_token:  # pragma: no cover
            raise RuntimeError("Refresh token not configured for OAuth")  # pragma: no cover

        logger.info("Fetching OAuth token via refresh token…")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.oauth_refresh_token,
            "client_id": self.oauth_client_id,
            "client_secret": self.oauth_client_secret,
        }
        self._perform_token_fetch(data)

    def _perform_token_fetch(self, data: Dict[str, str]):
        """Internal method to perform the token request and update headers."""
        response = requests.post(self.oauth_token_url, data=data, timeout=self.timeout)
        response.raise_for_status()

        token_body = response.json()
        access_token = token_body.get("access_token")
        refresh_token = token_body.get("refresh_token")
        expires_in = token_body.get("expires_in", 0)

        if not access_token:  # pragma: no cover
            raise RuntimeError("OAuth access token not found in response!")  # pragma: no cover

        # Update token + refresh token
        self._access_token = access_token
        if refresh_token:
            self._refresh_token = refresh_token

        # Precompute expiry time (optional)
        self._token_expiry = time.time() + expires_in

        # Update session header
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})

        logger.info("OAuth token stored & Authorization header updated successfully.")

    # -------------------------------------------------------------------------
    # Retry and Session Helpers
    # -------------------------------------------------------------------------
    def _configure_retries(self, max_retries: int):
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "PUT", "DELETE", "POST", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    # -------------------------------------------------------------------------
    # Allure Attachments (optional)
    # -------------------------------------------------------------------------
    def _attach_to_allure(self, method, url, response, kwargs):
        if not allure:  # pragma: no cover
            return  # pragma: no cover
        with allure.step(f"{method} {url}"):
            details = {**kwargs}
            allure.attach(
                json.dumps(details, indent=2), "Request data", allure.attachment_type.JSON
            )
            allure.attach(
                f"Status: {response.status_code}\n\n{response.text[:1500]}",
                "Response body",
                allure.attachment_type.TEXT,
            )

    # -------------------------------------------------------------------------
    # JSON Assertion Helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def assert_status(response, expected_code: int):
        assert (
            response.status_code == expected_code
        ), f"Expected {expected_code}, got {response.status_code}"

    @staticmethod
    def assert_json_key(response, key: str):
        body = response.json()
        assert key in body, f"JSON key '{key}' not found"

    @staticmethod
    def assert_json_value(response, key: str, expected: Any):
        body = response.json()
        assert body.get(key) == expected, f"Expected {expected}, got {body.get(key)}"
