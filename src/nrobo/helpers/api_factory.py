# helpers/api_factory.py
import os

from nrobo.api_wrappers.api_wrapper import ApiWrapper
from nrobo.core import settings


def get_api_wrapper():
    auth_method = os.getenv("NROBO_API_AUTH_METHOD", "").lower()
    base_url = settings.API_BASE_URL

    auth_config = {
        "bearer": lambda: ApiWrapper(base_url, bearer_token=os.getenv("NROBO_BEARER_TOKEN")),
        "basic": lambda: ApiWrapper(base_url, basic_auth=os.getenv("NROBO_BASIC_AUTH")),
        "oauth": lambda: ApiWrapper(
            base_url,
            oauth_client_id=os.getenv("NROBO_OAUTH2_CLIENT_ID"),
            oauth_client_secret=os.getenv("NROBO_OAUTH2_CLIENT_SECRET"),
        ),
    }

    return auth_config.get(auth_method, lambda: ApiWrapper(base_url))()
