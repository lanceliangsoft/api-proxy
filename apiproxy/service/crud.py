import os
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional
from fastapi import Depends
from sqlmodel import Session, select, update, delete, create_engine, Session, SQLModel
from .models import TrafficEntity, MappedServiceEntity
from .config import settings


engine = create_engine(
    str(settings.DATABASE_URL), connect_args={"check_same_thread": False}
)


def get_db() -> Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(bind=engine)
    pass


def select_service(session: Session) -> List[MappedServiceEntity]:
    return session.exec(select(MappedServiceEntity)).all()


def select_service_by_name(
    session: Session, name: str
) -> Optional[MappedServiceEntity]:
    return session.get(MappedServiceEntity, name)


def insert_service(
    session: Session, service: MappedServiceEntity
) -> MappedServiceEntity:
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


def update_service(session: Session, service: MappedServiceEntity) -> None:
    entity = session.get(MappedServiceEntity, service.name)
    if entity is not None:
        entity.port = service.port
        entity.forward_url = service.forward_url
        entity.active = service.active
        session.add(entity)
        session.commit()


def delete_service(session: Session, service_name: str) -> None:
    print(f"deleting service {service_name} from db...")
    entity = session.get(MappedServiceEntity, service_name)
    if entity is not None:
        session.delete(entity)
        session.commit()


def create_traffic(session: Session, traffic: TrafficEntity) -> TrafficEntity:
    session.add(traffic)
    session.commit()
    session.refresh(traffic)
    return traffic


def get_traffic_by_id(session: Session, id: int) -> Optional[TrafficEntity]:
    return session.get(TrafficEntity, id)


def query_traffics(
    session: Session,
    service_name: Optional[str] = None,
    begin_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = 0,
    limit: int = -1,
) -> List[TrafficEntity]:
    query = select(TrafficEntity)
    if service_name:
        query = query.where(TrafficEntity.service_name == service_name)
    if begin_time:
        query = query.where(TrafficEntity.timestamp >= begin_time)
    if end_time:
        query = query.where(TrafficEntity.timestamp <= end_time)
    if offset > 0:
        query = query.offset(offset)
    if limit > 0:
        query = query.limit(limit)

    return session.exec(query).all()
