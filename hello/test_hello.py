import json

import pytest

from hello import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        yield app.test_client()


def test_health_check(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"