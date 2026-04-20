import pytest
from datetime import datetime
from sqlmodel import Session
from apiproxy.service import crud
from apiproxy.service.crud import engine, get_traffic_by_id
from apiproxy.service.models import TrafficEntity, Traffic
from apiproxy.service.app_state import AppState


def test_create_get_traffic(db: Session) -> None:
    traffic_in = TrafficEntity(
        service_name="test_service",
        method="GET",
        url="https://www.google.com",
        req_headers={"User-Agent": "test-agent"},
        req_body=None,
        status_code=200,
        resp_headers={"Content-Type": "text/html"},
        resp_body=b'{"message": "Hello, World!"}',
        timestamp=datetime.now(),
        duration_ms=123,
    )
    traffic = crud.create_traffic(session=db, traffic=traffic_in)
    assert traffic.id is not None
    print(f"id={traffic.id}")

    traffic_from_db = get_traffic_by_id(session=db, id=traffic.id)
    assert traffic_from_db is not None
    assert traffic_from_db.id == traffic.id
    assert traffic_from_db.service_name == traffic_in.service_name
    assert traffic_from_db.method == traffic_in.method
    assert traffic_from_db.url == traffic_in.url
    assert traffic_from_db.req_headers == traffic_in.req_headers
    assert traffic_from_db.req_headers['User-Agent'] == "test-agent"
    assert traffic_from_db.req_body == traffic_in.req_body
    assert traffic_from_db.status_code == traffic_in.status_code
    assert traffic_from_db.resp_headers == traffic_in.resp_headers
    assert traffic_from_db.resp_headers['Content-Type'] == "text/html"
    assert traffic_from_db.resp_body == traffic_in.resp_body
    assert traffic_from_db.timestamp == traffic_in.timestamp
    assert traffic_from_db.duration_ms == traffic_in.duration_ms


def test_app_state_traffics() -> None:
    traffic_in = Traffic(
        service_name="test_service",
        method="GET",
        url="https://www.google.com",
        req_headers={"User-Agent": "test-agent"},
        req_body=None,
        status_code=200,
        resp_headers={"Content-Type": "text/html"},
        resp_body=b'{"message": "Hello, World!"}',
        timestamp=datetime.now(),
        duration_ms=123,
    )
    traffic = AppState.add_traffic(traffic_in)
    with Session(engine) as session:
        traffic_from_db = get_traffic_by_id(session, traffic.id)
        assert traffic_from_db is not None
        assert traffic_from_db.id == traffic.id
        assert traffic_from_db.service_name == traffic_in.service_name
        assert traffic_from_db.method == traffic_in.method
        assert traffic_from_db.url == traffic_in.url
        assert traffic_from_db.req_headers == traffic_in.req_headers
        assert traffic_from_db.req_headers['User-Agent'] == "test-agent"
        assert traffic_from_db.req_body == traffic_in.req_body
        assert traffic_from_db.status_code == traffic_in.status_code
        assert traffic_from_db.resp_headers == traffic_in.resp_headers
        assert traffic_from_db.resp_headers['Content-Type'] == "text/html"
        assert traffic_from_db.resp_body == traffic_in.resp_body
        assert traffic_from_db.timestamp == traffic_in.timestamp
        assert traffic_from_db.duration_ms == traffic_in.duration_ms


def test_query_traffics(db: Session) -> None:
    traffic_1 = TrafficEntity(
        service_name="test_service",
        method="POST",
        url="https://www.example.com/api",
        req_headers={"User-Agent": "test-agent"},
        req_body=b'{"key": "value"}',
        status_code=200,
        resp_headers={"Content-Type": "application/json"},
        resp_body=b'{"message": "Created"}',
        timestamp=datetime(2020, 1, 1, 12, 0, 0),
        duration_ms=456,
    )
    crud.create_traffic(session=db, traffic=traffic_1)
    
    traffic_2 = TrafficEntity(
        service_name="test_service_2",
        method="GET",
        url="https://www.example.com/api2",
        req_headers={"User-Agent": "test-agent"},
        status_code=200,
        resp_headers={"Content-Type": "application/json"},
        resp_body=b'{"message": "Created"}',
        timestamp=datetime(2020, 1, 2, 14, 0, 0),
        duration_ms=789,
    )
    crud.create_traffic(session=db, traffic=traffic_2)

    traffics = crud.query_traffics(
        session=db,
        service_name="test_service",
        begin_time=datetime(2020, 1, 1),
        end_time=datetime(2020, 1, 2),
    )
    assert len(traffics) == 1
    assert traffics[0].service_name == "test_service"
    assert traffics[0].method == "POST"
    assert traffics[0].url == "https://www.example.com/api"
    assert traffics[0].req_headers == {"User-Agent": "test-agent"}
    assert traffics[0].req_body == b'{"key": "value"}'
    assert traffics[0].status_code == 200
    assert traffics[0].timestamp == datetime(2020, 1, 1, 12, 0, 0)
    assert traffics[0].duration_ms == 456

