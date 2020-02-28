from starlette.testclient import TestClient
from intro import app

client = TestClient(app)

def test_read_hello():
    response = client.get('/?strings=a&integer=1')
    expect = {
        "text": "hello, world",
        "aux": 1,
        "strings": "a"
    }
    assert response.status_code == 200
    assert response.json() == expect


def test_read_declare_request_body():
    response = client.post(
        "/post",
        json={
            "string": "foo",
            "default_none": "bar",
            "lists": [1, 2]
        }
    )
    expect = {
        "text": "hello, foo, bar, [1, 2]"
    }
    assert response.status_code == 200
    assert response.json() == expect
