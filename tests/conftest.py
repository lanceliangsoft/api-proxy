from collections.abc import Generator
import pytest
from sqlmodel import Session, select, delete
from apiproxy.service.models import TrafficEntity, MappedServiceEntity
from apiproxy.service.crud import init_db, engine


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        init_test_data(session)
        yield session
        session.execute(delete(TrafficEntity))
        session.execute(delete(MappedServiceEntity))
        session.commit()


def init_test_data(session: Session) -> None:
    service_a = MappedServiceEntity(
        name="Service A",
        port=8001,
        forward_url="http://localhost:8001",
        active=True,
        up=True,
    )
    service_b = MappedServiceEntity(
        name="Service B",
        port=8002,
        forward_url="http://localhost:8002",
        active=True,
        up=True,
    )
    session.add(service_a)
    session.add(service_b)
    session.commit()
