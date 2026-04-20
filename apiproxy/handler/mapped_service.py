# Mapping a remote REST service at a local port.
from http.server import BaseHTTPRequestHandler
import urllib3
import time
import ssl
from typing import Optional, Tuple, Dict, Any
from ..service.app_state import AppState
from .http_util import exclude_headers


def run_mapped_service(port: int, ssl_context: Optional[ssl.SSLContext] = None) -> None:
    pass


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


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, service_name: str, *args, **kwargs):
        self._service_name = service_name
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

    def _retrieve(self, method: str) -> Any:
        start_time = time.time()

        headers = {}
        for key in self.headers:
            if key.lower() not in exclude_headers:
                headers[key] = self.headers[key]

        forward_host = AppState.get_forward_host(self._service_name)
        assert forward_host, (
            f"No forward host configured for service {self._service_name}"
        )
        url = forward_host.url + self.path
        print(f"Forwarding to {method} {url}, headers: {headers}")

        http = urllib3.PoolManager(cert_reqs=ssl.CERT_NONE)
        resp = http.request(
            method,
            url,
            headers=headers,
            body=self.req_body,
            context=forward_host.get_context(),
        )
        self._log_traffic(
            method,
            url,
            headers,
            self.req_body,
            resp.status,
            resp.headers,
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
        AppState.get_traffics_of_service(self._service_name).append(
            {
                "method": method,
                "url": url,
                "req_headers": req_headers,
                "req_body": brief(req_body),
                "resp_status": resp_status,
                "resp_headers": resp_headers,
                "resp_body": brief(resp_body),
                "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "duration": duration,
            }
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
