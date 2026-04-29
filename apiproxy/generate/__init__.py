from typing import Callable, Dict, Optional

from fastapi import HTTPException
from ..service.app_state import AppState
from ..service.models import (
    GenerateModelRequest,
    GenerateRequest,
    GenerateResponse,
    Traffic,
)
from .curl import generate_curl, generate_curl_windows
from .spring_boot import (
    generate_spring_boot_web_mvc,
    generate_spring_boot_web_flux,
)
from .dotnet import generate_asp_net_api, generate_cs_models, generate_dot_net_client
from .java_model import generate_java_models
from .golang import generate_go_fiber_api
from .rust import generate_rust_actix_api
from .ts_model import generate_typescript_models
from .py_model import generate_python_models
from .go_model import generate_go_models

generators: Dict[str, Callable] = {
    "CURL": generate_curl,
    "CURL_WINDOWS": generate_curl_windows,
    "SPRING_BOOT_WEB_MVC": generate_spring_boot_web_mvc,
    "SPRINT_BOOT_WEB_FLUX": generate_spring_boot_web_flux,
    "ASP_NET_API": generate_asp_net_api,
    "GO_FIBER_API": generate_go_fiber_api,
    "RUST_ACTIX_API": generate_rust_actix_api,
    "DOT_NET_CLIENT": generate_dot_net_client,
    # TODO: add more generators here
}

model_generators: Dict[str, Callable] = {
    "CS": generate_cs_models,
    "JAVA": generate_java_models,
    "TYPESCRIPT": generate_typescript_models,
    "PYTHON": generate_python_models,
    "GO": generate_go_models,
    # TODO: add more generators here
}


async def generate_code(request: GenerateRequest) -> GenerateResponse:
    generator = generators.get(request.format)
    if generator is None:
        raise HTTPException(
            status_code=400,
        )

    print(f"generating call for traffic id={request.traffic_id}")
    traffic: Optional[Traffic] = AppState.get_traffic(request.traffic_id)
    if traffic is None:
        raise HTTPException(
            status_code=404,
        )
    generated_files = await generator(traffic)

    return GenerateResponse(files=generated_files)


async def generate_model(request: GenerateModelRequest) -> GenerateResponse:
    generator = model_generators.get(request.format)
    if generator is None:
        raise HTTPException(
            status_code=400,
        )

    generated_files = await generator(request.json_payload, request.root_element)

    return GenerateResponse(files=generated_files)
