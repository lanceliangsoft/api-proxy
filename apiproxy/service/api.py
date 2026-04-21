import threading
from typing import Any, List
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from .crud import (
    SessionDep,
    query_traffics,
    update_service,
)
from .models import (
    GenerateRequest,
    GenerateResponse,
    MappedService,
    MappedServiceEntity,
    SwitchServiceRequest,
    Traffic,
)
from .engine import Engine, EngineDep
from ..generate import generate_code
from .app_state import AppState


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
async def get_traffics(session: SessionDep, service_name: str):
    return {
        "traffics": [
            Traffic.model_validate(traffic)
            for traffic in query_traffics(session, service_name)
        ]
    }


@app.post("/api/generate")
async def post_generate(request: GenerateRequest) -> GenerateResponse:
    return await generate_code(request)


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
