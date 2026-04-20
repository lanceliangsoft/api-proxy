from datetime import datetime
from typing import Optional
from asyncio import StreamWriter
import httpx
from ..service.models import HttpRequest, HttpResponse

exclude_headers = [
    "content-length",
    "transfer-encoding",
    "content-encoding",
    "connection",
    "set-cookie",
    "host",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "upgrade",
]


def read_block_till(buffer: bytearray, delimiter: bytes) -> Optional[bytearray]:
    if delimiter in buffer:
        index = buffer.find(delimiter)
        end_index = index + len(delimiter)
        result = buffer[:index]
        del buffer[:end_index]
        return result
    else:
        return None


def read_block_of_len(buffer: bytearray, length: int) -> Optional[bytearray]:
    if length <= len(buffer):
        result = buffer[:length]
        del buffer[:length]
        return result
    else:
        return None


def parse_request(request_headers: str) -> HttpRequest:
    lines = request_headers.split("\r\n")
    method, path, _ = lines[0].split()
    headers = {}
    for line in lines[1:]:
        if ": " in line:
            key, value = line.split(": ", maxsplit=1)
            headers[key.strip()] = value.strip()

    return HttpRequest(method=method, path=path, headers=headers)


def parse_response(response_headers: str) -> HttpResponse:
    lines = response_headers.split("\r\n")
    _http_ver, status_code, message = lines[0].split()
    headers = {}
    for line in lines[1:]:
        if ": " in line:
            key, value = line.split(": ", maxsplit=1)
            headers[key.strip()] = value.strip()

    return HttpResponse(
        status_code=status_code, message=message, headers=headers, body=None
    )


def diff_ms(t2: datetime, t1: datetime) -> int:
    dt = t2 - t1
    return int(86400000 * dt.days + 1000 * dt.seconds + (dt.microseconds / 1000))


async def send_request(writer: StreamWriter, response: httpx.Response) -> None:
    s = f"HTTP/1.1 {response.status_code} {response.reason_phrase}\r\n"

    for key, value in response.headers.items():
        s += f"{key}: {value}\r\n"
    s += "\r\n"
    writer.write(s.encode())
    writer.write(response.content)

    await writer.drain()
