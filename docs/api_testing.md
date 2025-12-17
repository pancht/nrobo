# 🔌 API Testing Support
`nrobo` now supports API testing out-of-the-box using the powerful `ApiWrapper` utility.

## ✅ Features

- Built-in support for `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, etc.

- Retry strategy with exponential backoff

- OAuth2 support (client credentials & refresh token flow)

- Bearer token and Basic Auth support

- Token auto-refresh on `401 Unauthorized`

- Optional Allure report integration

- Static helpers for JSON key/value assertions

## 🧪 Example Usage
```python
def test_example(api):
    response = api.get("/v1/resource/")
    api.assert_status(response, 200)
    api.assert_json_key(response, "data")
```

## 🔐 Authentication

You can configure API authentication using environment variables:

```python
### For Bearer Token
export NROBO_API_AUTH_METHOD=bearer
export NROBO_BEARER_TOKEN=your-token

### For Basic Auth
export NROBO_API_AUTH_METHOD=basic
export NROBO_BASIC_AUTH=username:password

### For OAuth2 with Refresh
export NROBO_API_AUTH_METHOD=oauth
export NROBO_OAUTH2_CLIENT_ID=your-client-id
export NROBO_OAUTH2_CLIENT_SECRET=your-client-secret
export NROBO_OAUTH2_REFRESH_TOKEN=your-refresh-token
```

## 🧰 Fixture

Use the api fixture in your tests — it automatically initializes ApiWrapper based on the configured auth method.
