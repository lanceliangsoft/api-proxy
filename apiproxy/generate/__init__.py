from typing import Callable, Dict, Optional

from fastapi import HTTPException
from ..service.app_state import AppState
from ..service.models import GenerateRequest, GenerateResponse, Traffic
from .curl import generate_curl, generate_curl_windows
from .spring_boot import (
    generate_spring_boot_web_mvc,
    generate_spring_boot_web_flux,
)
from .dotnet import generate_asp_net_api
from .golang import generate_go_fiber_api
from .rust import generate_rust_actix_api

generators: Dict[str, Callable] = {
    "CURL": generate_curl,
    "CURL_WINDOWS": generate_curl_windows,
    "SPRING_BOOT_WEB_MVC": generate_spring_boot_web_mvc,
    "SPRINT_BOOT_WEB_FLUX": generate_spring_boot_web_flux,
    "ASP_NET_API": generate_asp_net_api,
    "GO_FIBER_API": generate_go_fiber_api,
    "RUST_ACTIX_API": generate_rust_actix_api,
    # TODO: add more generators here
}


async def generate_code(request: GenerateRequest) -> GenerateResponse:
    generator = generators.get(request.format)
    if generator is None:
        raise HTTPException(
            status_code=400,
        )

    traffic: Optional[Traffic] = AppState.get_traffic(request.trafficId)
    if traffic is None:
        raise HTTPException(
            status_code=404,
        )
    generated_files = await generator(traffic)

    return GenerateResponse(files=generated_files)
