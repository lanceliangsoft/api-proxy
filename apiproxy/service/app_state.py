import ssl
import asyncio
from typing import Dict, Optional, List, Any
from .models import MappedService, Traffic, TrafficEntity
from .crud import (
    create_traffic,
    get_db,
    get_traffic_by_id,
)


class ForwardHost:
    def __init__(
        self, env: str, url: str, ssl_context: Optional[ssl.SSLContext] = None
    ):
        self.env = env
        self.url = url
        self.ssl_context = ssl_context


class AppState:
    current_env: str = ""
    services: List[MappedService] = []
    servers: Dict[str, asyncio.Server] = {}
    engine: Optional[Any] = None

    @classmethod
    def get_env(cls) -> str:
        return cls.current_env

    @classmethod
    def set_env(cls, env: str) -> None:
        cls.current_env = env

    @classmethod
    def is_service_up(cls, service_name: str) -> bool:
        return service_name == 'console-api' or service_name in cls.servers


    '''
    @classmethod
    def get_services(cls) -> List[MappedService]:
        with next(get_db()) as session:
            return [
                MappedService.model_validate(service)
                for service in list_services(session)
            ]

    @classmethod
    def get_service(cls, service_name: str) -> Optional[MappedService]:
        with next(get_db()) as session:
            service = get_service_by_name(session, service_name)
            return MappedService.model_validate(service) if service else None

    @classmethod
    def add_service(cls, service: MappedService) -> None:
        print(f"adding service {service.name} at {service.port}")
        with next(get_db()) as session:
            if get_service_by_name(session, service.name) is None:
                create_service(session, MappedServiceEntity.model_validate(service))

    @classmethod
    def set_service_active(cls, service_name: str, active: bool) -> None:
        with next(get_db()) as session:
            service = get_service_by_name(session, service_name)
            if service:
                if service.active != active:
                    print(f"updating service={service_name}, active={active}")
                    service.active = active
                    update_service(session, service)

    @classmethod
    def set_service_status(cls, service_name: str, up: bool) -> None:
        with next(get_db()) as session:
            service = get_service_by_name(session, service_name)
            if service:
                service.up = up
                update_service(session, service)
    '''

    @classmethod
    def add_traffic(cls, traffic: Traffic) -> Traffic:
        with next(get_db()) as session:
            new_traffic = create_traffic(session, TrafficEntity.model_validate(traffic))
            return Traffic.model_validate(new_traffic)

    @classmethod
    def get_traffic(cls, id: int) -> Optional[Traffic]:
        with next(get_db()) as session:
            traffic = get_traffic_by_id(session, id)
            return Traffic.model_validate(traffic) if traffic is not None else None
