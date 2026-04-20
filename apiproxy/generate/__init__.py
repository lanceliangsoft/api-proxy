from typing import Callable, Dict, Optional
from fastapi import HTTPException
from ..service.app_state import AppState
from ..service.models import GenerateRequest, GenerateResponse, Traffic
from .curl import generate_curl, generate_curl_windows

generators: Dict[str, Callable] = {
    "CURL": generate_curl,
    "CURL_WINDOWS": generate_curl_windows,
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
    generated_code = await generator(traffic)

    return GenerateResponse(generated=generated_code)
