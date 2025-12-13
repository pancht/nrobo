import json
import time
from typing import Any, Dict, Optional, Union

import requests
from requests.adapters import HTTPAdapter, Retry

from nrobo.helpers.logging_helper import get_logger

try:
    import allure
except ImportError:
    allure = None  # Allure optional

logger = get_logger("nRobo:API")


class ApiWrapper:
    """
    A full-featured API testing helper for nRoBo.
    Provides request handling, retries, logging, Allure attachments, and validation utilities.
    """

    def __init__(self, base_url: str, timeout: int = 10, max_retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self._configure_retries(max_retries)
        logger.info(f"API client initialized for {self.base_url}")

    # -------------------------------------------------------------------------
    # Public HTTP methods
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
    # Core request handler
    # -------------------------------------------------------------------------
    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        expected_status: Optional[int] = None,
        retries: int = 0,
        **kwargs,
    ) -> requests.Response:
        """Send HTTP request with robust logging, Allure attachment, and optional validation."""

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()

        try:
            logger.info(f"[{method}] {url}")
            logger.debug(f"Params={params}, JSON={json_data}, Data={data}")

            response = self.session.request(
                method,
                url,
                params=params,
                json=json_data,
                data=data,
                files=files,
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )

        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            if retries > 0:
                return self._request(method, endpoint, retries=retries - 1, **kwargs)
            raise

        duration = round(time.time() - start_time, 3)
        logger.info(f"Response: {response.status_code} ({duration}s)")

        self._attach_to_allure(method, url, response, params, json_data, data)

        if expected_status:
            assert (
                response.status_code == expected_status
            ), f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}"

        return response

    # -------------------------------------------------------------------------
    # Retry + Logging + Helpers
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

    def _attach_to_allure(self, method, url, response, params, json_data, data):
        """Attach request and response to Allure if available."""
        if not allure:
            return

        with allure.step(f"{method} {url}"):
            allure.attach(json.dumps(params or {}, indent=2), "Params", allure.attachment_type.JSON)
            if json_data:
                allure.attach(
                    json.dumps(json_data, indent=2), "Payload", allure.attachment_type.JSON
                )
            elif data:
                allure.attach(str(data), "Data", allure.attachment_type.TEXT)
            allure.attach(
                f"Status: {response.status_code}\n\n{response.text[:1000]}",
                "Response",
                allure.attachment_type.TEXT,
            )

    # -------------------------------------------------------------------------
    # Assertion helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def assert_json_key(response: requests.Response, key: str):
        """Assert that a key exists in the JSON body."""
        try:
            body = response.json()
        except Exception:
            raise AssertionError("Response is not valid JSON")
        assert key in body, f"Key '{key}' not found in JSON response"

    @staticmethod
    def assert_json_value(response: requests.Response, key: str, expected_value: Any):
        """Assert that a JSON key equals an expected value."""
        ApiWrapper.assert_json_key(response, key)
        actual = response.json()[key]
        assert actual == expected_value, f"For key '{key}', expected {expected_value}, got {actual}"

    @staticmethod
    def assert_status(response: requests.Response, expected_code: int):
        """Validate response status."""
        assert (
            response.status_code == expected_code
        ), f"Expected HTTP {expected_code}, got {response.status_code}: {response.text[:200]}"

    @staticmethod
    def extract_json(response: requests.Response) -> Union[Dict[str, Any], list]:
        """Return parsed JSON or raise error."""
        try:
            return response.json()
        except ValueError as e:
            raise AssertionError(f"Invalid JSON response: {e}")
