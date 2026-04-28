import uvicorn
import json
from datetime import datetime
from typing import Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import logging
from .crud import (
    SessionDep,
    delete_traffic_by_id,
    query_traffics,
    update_service,
)
from .models import (
    GenerateModelRequest,
    GenerateRequest,
    GenerateResponse,
    MappedService,
    MappedServiceEntity,
    SwitchServiceRequest,
    Traffic,
)
from .str_util import parse_datetime
from .engine import Engine, EngineDep
from ..generate import generate_code, generate_model
from .app_state import AppState

logger = logging.getLogger(__name__)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200/", "*"],
    allow_methods=["GET", "OPTIONS", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.mount("/console", StaticFiles(directory="static/browser", html=True), name="static")


@app.get("/")
async def home() -> RedirectResponse:
    return RedirectResponse("/console/")


@app.get("/api/services")
async def get_services(engine: EngineDep) -> dict[str, List[MappedService]]:
    return {"services": engine.get_services()}


@app.post("/api/services", response_model=MappedService)
async def post_service(engine: EngineDep, service: MappedService) -> MappedService:
    print(">>Creating service..., service=", service)
    new_service = engine.create_service(service)
    print("sending response")
    return new_service


@app.put("/api/services", response_model=MappedService)
async def put_service(engine: EngineDep, request: MappedService) -> MappedService:
    return await engine.update_service(request)


@app.post("/api/services/switch", response_model=MappedService)
async def switch_service(
    engine: EngineDep, request: SwitchServiceRequest
) -> MappedService:
    return await engine.set_service_active(request.name, request.active)


@app.delete("/api/services/{service_name}")
async def delete_service(engine: EngineDep, service_name: str):
    print(f">>Received request to delete service {service_name}...")
    await engine.remove_service(service_name)
    return {"service_name": service_name, "status": "deleted"}


@app.get("/api/traffics/{service_name}")
async def get_traffics(
    session: SessionDep,
    service_name: str,
    begin_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> dict:
    begin_time = parse_datetime(begin_time)
    end_time = parse_datetime(end_time)
    logger.info(
        f"get_traffics service={service_name} begin_time={begin_time} end_time={end_time}"
    )
    return {
        "traffics": [
            Traffic.model_validate(traffic)
            for traffic in query_traffics(session, service_name, begin_time, end_time)
        ]
    }


@app.delete("/api/traffics/{id}")
async def remove_traffic(session: SessionDep, id: int) -> dict:
    deleted = delete_traffic_by_id(session, id)
    print(("deleted" if deleted else "not deleted") + f" traffic {id}")
    return {"deleted": deleted}


@app.post("/api/generate/call")
async def post_generate_call(request: GenerateRequest) -> GenerateResponse:
    print(f"post_generate_call request={request.traffic_id}")
    return await generate_code(request)


@app.post("/api/generate/model")
async def post_generate_model(request: GenerateModelRequest) -> GenerateResponse:
    print(f"post_generate_model format={request.format} elem={request.root_element} payload={request.json_payload}")
    return await generate_model(request)


@app.get("/api/next-port")
async def get_next_port(
    engine: EngineDep, start: int = 8000, end: int = 9000
) -> dict[str, Any]:
    # Placeholder implementation - replace with actual port allocation logic
    port = engine.get_next_port(start, end)
    if port is None:
        raise HTTPException(status_code=503, detail="No available ports")
    return {"port": port}


def run_fastapi(port: int) -> None:
    uvicorn.run(app, host="0.0.0.0", port=port)
