import pytest
import schemathesis

from nrobo.api_wrappers.api_wrapper import ApiWrapper

# Load the spec
schema = schemathesis.from_path("openapi/api_spec.yaml", validate_schema=True)

#
# @pytest.fixture(scope="session")
# def api() -> ApiWrapper:
#     return ApiWrapper("https://your-api-base-url.com")


@schema.parametrize()
@pytest.mark.skip
def test_api_contract(api: ApiWrapper, case):
    """
    Automated test generated from OpenAPI spec.
    `case` has:
      - method
      - path
      - body
      - headers
    """

    # Create request
    response = api.session.request(
        case.method,
        api.base_url + case.path_format,
        headers=case.headers,
        json=case.body,
    )

    # Assert the expected response status
    case.validate_response(response)

    # Example custom assertion
    if response.status_code == 200:
        body = response.json()
        assert "token" in body
