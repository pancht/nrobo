import pytest

from nrobo.api_wrappers.api_wrapper import ApiWrapper


@pytest.mark.example
def test_api_endpoints(api: ApiWrapper):
    # GET example
    res = api.get("/api/v1/animal/", expected_status=200)

    api.assert_json_key(res, "status")
    api.assert_json_value(res, "status", "success")

    # # POST example
    # payload = {"title": "foo", "body": "bar", "userId": 1}
    # res = api.post("posts", json_data=payload, expected_status=201)
    # assert res.json()["title"] == "foo"
    #
    # # PUT example
    # res = api.put("posts/1", json_data={"title": "updated"}, expected_status=200)
    # assert res.json()["title"] == "updated"
    #
    # # DELETE example
    # res = api.delete("posts/1", expected_status=200)
