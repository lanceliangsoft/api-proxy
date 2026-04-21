# Mapping a remote REST service at a local port.
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib3
import time
from datetime import datetime, timezone
import ssl
from typing import Optional, Tuple, Dict, Any
from ..service.app_state import AppState
from ..service.models import MappedService, Traffic
from .http_util import exclude_headers


def run_mapped_service(
    service: MappedService, ssl_context: Optional[ssl.SSLContext] = None
) -> None:
    with ProxyHTTPServer(
        ("0.0.0.0", service.port),
        ProxyHTTPRequestHandler,
        service_info=service,
        ssl_context=ssl_context,
    ) as httpd:
        print(f"Mapped service running on port {service.port}...")
        httpd.serve_forever()


def read_props(props_file: str) -> Dict[str, str]:
    props = {}
    with open(props_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                props[key.strip()] = value.strip()
    return props


def brief(data: bytes, max_length: int = 20) -> str:
    text = (
        data.decode("utf-8", errors="replace").replace("\n", " ").replace("\r", " ")
        if data
        else ""
    )
    return text[:max_length] + ("..." if len(text) > max_length else "")


def to_dict(headers) -> Dict[str, str]:
    return {k.lower(): v for k, v in headers.items()}


class ProxyHTTPServer(HTTPServer):
    service_info: MappedService
    ssl_context: Optional[ssl.SSLContext]

    def __init__(
        self, server_address, RequestHandlerClass, service_info=None, ssl_context=None
    ):
        super().__init__(server_address, RequestHandlerClass)
        self.ssl_context = ssl_context
        self.service_info = service_info
        print(f"Initialized ProxyHTTPServer for service {service_info.name} on {server_address}")


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_locally(self, _method: str) -> Tuple[bool, int, Dict[str, str], bytes]:
        return False, 200, {}, b""

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def do_PUT(self):
        self._handle_request("PUT")

    def do_DELETE(self):
        self._handle_request("DELETE")

    def do_PATCH(self):
        self._handle_request("PATCH")

    def _handle_request(self, method: str):
        print(f"Received {method} request for {self.path} on service server={self.server} {self.server.service_info.name if self.server.service_info else 'Unknown'}...")
        content_length = int(self.headers.get("Content-Length", 0))
        self.req_body = self.rfile.read(content_length) if content_length > 0 else b""

        handle_locally, status, headers, body = self.handle_locally(method)
        if handle_locally:
            self._send_response(status, headers, body)
        else:
            resp = self._retrieve(method)
            status, headers, body = self.process_response(resp)
            self._send_response(status, headers, body)

    def _retrieve(self, method: str) -> Any:
        start_time = time.time()

        headers = {}
        for key in self.headers:
            if key.lower() not in exclude_headers:
                headers[key] = self.headers[key]

        forward_url = self.server.service_info.forward_url
        assert forward_url, (
            f"No forward URL configured for service {self.server.service_info.name}"
        )
        url = forward_url + self.path
        print(f"Forwarding to {method} {url}, headers: {headers}")

        http = urllib3.PoolManager(cert_reqs=ssl.CERT_NONE)
        resp = http.request(
            method,
            url,
            headers=headers,
            body=self.req_body,
            #context=self.server.ssl_context,  # type: ignore
        )
        resp_headers = to_dict(resp.headers)
        self._log_traffic(
            method,
            url,
            headers,
            self.req_body,
            resp.status,
            resp_headers,
            resp.data,
            time.time() - start_time,
        )
        return resp

    def _log_traffic(
        self,
        method: str,
        url: str,
        req_headers: Dict[str, str],
        req_body: bytes,
        resp_status: int,
        resp_headers: Dict[str, str],
        resp_body: bytes,
        duration: float,
    ):
        AppState.add_traffic(
            traffic=Traffic(
                service_name=self.server.service_info.name,
                method=method,
                url=url,
                req_headers=req_headers,
                req_body=req_body,
                status_code=resp_status,
                resp_headers=resp_headers,
                resp_body=resp_body,
                timestamp=datetime.now(timezone.utc),
                duration_ms=int(duration * 1000),
            )
        )

    def process_response(self, resp) -> Tuple[int, Dict[str, str], bytes]:
        status = resp.status
        headers = resp.getheaders()
        body = resp.data if status == 200 else b""
        return status, headers, body

    def _send_response(self, status: int, headers: Dict[str, str], body: bytes):
        self.send_response(status)
        for key, value in headers.items():
            if key.lower() not in exclude_headers:
                self.send_header(key, value)
        self.end_headers()
        if body:
            self.wfile.write(body)
