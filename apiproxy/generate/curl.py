from typing import List
from .consts import excluded_headers
from ..service.models import GeneratedFile, Traffic


async def generate_curl(traffic: Traffic) -> List[GeneratedFile]:
    cmd = "curl"
    if traffic.method != "GET":
        cmd += f" --request {traffic.method}"
    cmd += f' "{traffic.url}"'
    for key, value in traffic.req_headers.items():
        if key.lower() not in excluded_headers:
            cmd += f' \\\n-H "{key}: {value}"'
    if traffic.method == "PUT" or traffic.method == "POST":
        cmd += f" \\\n-d '{encode_body(traffic.req_body)}'"
    return [GeneratedFile(
        file_name="curl",
        content=cmd
    )]


async def generate_curl_windows(traffic: Traffic) -> List[GeneratedFile]:
    cmd = "curl -k"
    if traffic.method != "GET":
        cmd += f" --request {traffic.method}"
    cmd += f' "{traffic.url}"'
    for key, value in traffic.req_headers.items():
        if key.lower() not in excluded_headers:
            cmd += f' ^\n-H "{key}: {value}"'
    if traffic.method == "PUT" or traffic.method == "POST":
        cmd += f' ^\n-d "{encode_body_windows(traffic.req_body)}"'
    return [GeneratedFile(
        file_name="curl",
        content=cmd
    )]


def encode_body(body: bytes) -> str:
    return body.decode().replace("'", "'\\''")


def encode_body_windows(body: bytes) -> str:
    return body.decode().replace("\r", "").replace("\n", "\\n").replace('"', '\\"')
