import asyncio
from http.client import HTTPException
import os
import ssl
import threading
import socket
from urllib import request
from fastapi import Depends
from typing import Any, Optional, Annotated
from ..handler.http_proxy import run_http_proxy
from ..handler.mapped_service import run_mapped_service
from .app_state import AppState
from .models import MappedService, MappedServiceEntity
from .crud import (
    get_db,
    init_db,
    SessionDep,
    select_service,
    select_service_by_name,
    insert_service,
    update_service,
)


def is_port_available(port: int) -> bool:
    try:
        socket.create_server(("localhost", port)).close()
        return True
    except OSError:
        return False


def start_servers():
    engine: Engine = engine_factory(session=next(get_db()))
    engine.start_service("http-proxy")


class Engine:
    def __init__(self, session: SessionDep):
        self._session = session
        self._init_ssl()
        self._init_data()
        pass

    def _init_data(self):
        init_db(self._session)

        if select_service_by_name(self._session, "console-api") is None:
            insert_service(
                self._session,
                MappedServiceEntity(
                    name="console-api",
                    port=8000,
                    forward_url="",
                    active=True,
                ),
            )
        
        if select_service_by_name(self._session, "http-proxy") is None:
            insert_service(
                self._session,
                MappedServiceEntity(
                    name="http-proxy",
                    port=8001,
                    forward_url="",
                    active=True,
                ),
            )

    def _init_ssl(self):
        certs_dir = os.path.expanduser("~/.apiproxy/certs")
        self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self._ssl_context.load_verify_locations(cafile=f"{certs_dir}/server.crt")
        self._ssl_context.load_cert_chain(
            certfile=f"{certs_dir}/server.crt", keyfile=f"{certs_dir}/server.key"
        )

    def start_service(self, service_name: str):
        service_info: MappedService = self.get_service(service_name)
        run_proc = (
            run_http_proxy if service_name == "http-proxy" else run_mapped_service
        )
        http_proxy_thread = threading.Thread(
            target=run_proc, args=(service_info.port, self._ssl_context), daemon=True
        )
        http_proxy_thread.start()

    async def stop_service(self, service_name: str):
        server = AppState.servers.get(service_name)
        if server:
            print(f"stopping {service_name}...")
            del AppState.servers[service_name]
            server.close()
            await server.wait_closed()
        else:
            print(f"server not found for {service_name}.")

    def get_services(self) -> list[MappedService]:
        services = [
            MappedService.model_validate(service)
            for service in select_service(self._session)
        ]
        for service in services:
            service.up = AppState.is_service_up(service.name)
        return services

    def get_service(self, service_name: str) -> Optional[MappedService]:
        service_entity = select_service_by_name(self._session, service_name)
        if service_entity:
            service = MappedService.model_validate(service_entity)
            service.up = AppState.is_service_up(service.name)
            return service
        else:
            return None

    def create_service(self, service: MappedService) -> MappedService:
        service = MappedServiceEntity.model_validate(service)
        existing_service = select_service_by_name(self._session, service.name)
        if existing_service:
            update_service(self._session, service)
            new_service = select_service_by_name(self._session, service.name)
        else:
            new_service = insert_service(self._session, service)
        print("sending response")
        result = MappedService.model_validate(new_service)
        result.up = AppState.is_service_up(result.name)
        return result

    async def set_service_active(
        self, service_name: str, active: bool
    ) -> Optional[MappedService]:
        print(f">>Switching service {service_name} active: {active}")
        service_entity = select_service_by_name(self._session, service_name)
        if service_entity is None:
            raise HTTPException(status_code=404, detail="Service not found")

        if service_entity.active != active:
            print(f"updating service={service_name}, active={active}")
            service_entity.active = active
            update_service(self._session, service_entity)

            if active:
                # start
                self.start_service(service_name)
            else:
                await self.stop_service(service_name)

        return self.get_service(service_name)
    
    async def update_service(self, service: MappedService) -> MappedService:
        '''
        Update a mapped service in db, start/stop if necessary.
        
        :param self: Description
        :param service: Description
        :type service: MappedService
        :return: Description
        :rtype: MappedService
        '''
        print(">>Updating service..., service=", service)
        existing_service = AppState.get_service(service.name)
        if existing_service is None:
            raise HTTPException(status_code=404, detail="Service not found")

        if (
            existing_service.port != service.port
            or existing_service.active != service.active
        ) and existing_service.active:
            # needs a restart.
            await self.stop_service(service.name)

        entity = MappedServiceEntity.model_validate(request)
        update_service(self._session, entity)
        if (
            existing_service.port != service.port
            or existing_service.active != service.active
        ) and service.active:
            # start
            self.start_service(service.name)
            asyncio.sleep(1)  # wait for server to start

        return self.get_service(service.name)

    def get_next_port(self, start: int, end: int) -> Optional[int]:
        services = self.get_services()
        port = start
        while port <= end:
            if (
                not any(service.port == port for service in services)
            ) and is_port_available(port):
                return port
            port += 1

        return None


def engine_factory(session: SessionDep) -> Engine:
    if AppState.engine is None:
        AppState.engine = Engine(session=session)

    return AppState.engine


EngineDep = Annotated[Engine, Depends(engine_factory)]
