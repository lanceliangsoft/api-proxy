from fastapi.testclient import TestClient
from sqlmodel import Session
from apiproxy.service.api import app
from apiproxy.service.models import MappedService, Traffic

client = TestClient(app)


def test_get_services():
    response = client.get("/api/services")
    assert response.status_code == 200
    assert "services" in response.json()
    # print("Services:", response.json()["services"])
    assert len(response.json()["services"]) > 0


def test_create_update_service():
    # new_service = '{"name": "Service C", "port": 8003, "forward_url": "http://localhost:8003", "active": true, "up": true}'
    new_service = {
        "name": "Service C",
        "port": 8003,
        "forward_url": "http://localhost:8003",
        "active": True,
        "up": True,
    }
    response = client.post("/api/services", json=new_service)
    assert response.status_code == 200
    print(f"--response.service={response.json()}")
    assert response.json()["name"] == "Service C"
    assert response.json()["up"]

    new_service["up"] = False
    response = client.put("/api/services", json=new_service)
    assert response.status_code == 200

"""
def test_get_traffics():
    response = client.get("/api/traffics")
    assert response.status_code == 200
    assert "traffics" in response.json()
    assert isinstance(response.json()["traffics"], list)
"""
