import asyncio
from asyncio import StreamReader, StreamWriter
import httpx
import ssl
from datetime import datetime
from typing import Optional
from .base_server import BaseConnection, HttpRequest, TcpServer, parse_request
from ..service.models import Traffic, HttpRequest, HttpResponse
from ..service.app_state import AppState
from .http_util import (
    read_block_till,
    parse_response,
    diff_ms,
    exclude_headers,
    send_request,
)


def run_http_proxy(port: int, ssl_context: Optional[ssl.SSLContext] = None) -> None:
    http_proxy_server = HttpProxyServer("0.0.0.0", port, ssl_context=ssl_context)
    asyncio.run(http_proxy_server.start())


class HttpProxyServer(TcpServer):
    def __init__(self, host: str, port: int, ssl_context=None):
        super().__init__("http-proxy", host, port, ssl_context)

    def create_connection(
        self, reader: StreamReader, writer: StreamWriter, ssl_context
    ) -> BaseConnection:
        conn = HttpProxyConnection(reader, writer, ssl_context)
        return conn


class HttpProxyConnection(BaseConnection):
    def __init__(
        self,
        reader: StreamReader,
        writer: StreamWriter,
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        super().__init__(reader, writer, ssl_context)
        self._req_buffer = bytearray()
        self._resp_buffer = bytearray()
        self._req_len = 0
        self._target_host = ""
        self._resp_len = 0
        self._resp_chunked = False
        self._traffic: Optional[Traffic] = None

    async def serve(self) -> None:
        print("started to serve...")
        has_next = True
        while has_next:
            request_headers = await self.read_data(b"\r\n\r\n")
            if request_headers is not None:
                request: HttpRequest = parse_request(request_headers.decode("utf8"))
                print(
                    f"Received request: {request.method} {request.path} {request.headers}"
                )
                if request.method == "CONNECT":
                    print(f"Handling CONNECT request to {request.path}")
                    await self.handle_connect(request)
                    has_next = False
                elif request.path.startswith("http://"):
                    has_next = await self.handle_http_forward(request)
                else:
                    print(f"Unexpected HTTP request: {request.method} {request.path}")
                    self._writer.close()
                    print("Connection closed")
                    has_next = False

    async def handle_http_forward(self, request: HttpRequest) -> bool:
        req_body: bytearray | None = None
        if request.method == "PUT" or request.method == "POST":
            if "Content-Length" in request.headers:
                req_body = await self.read_data_of_len(
                    int(request.headers["Content-Length"])
                )
            elif request.headers.get("Connection", "").lower() == "close":
                req_body = await self.read_data_till_close()
            else:
                print(f"Can't read request body: {request.method} {request.path}")
                self._writer.close()
                print("Connection closed")
                return False

        headers = {
            key: request.headers[key]
            for key in request.headers
            if key.lower() not in exclude_headers
        }

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method, url=request.path, headers=headers, content=req_body or b""
            )
            await send_request(self._writer, response)
            print(f"Forwarded response: {response.status_code}")

        return True

    async def handle_connect(self, request: HttpRequest) -> None:
        host, port = request.path.split(":")
        port = int(port)
        print(f"CONNECT to {host}:{port}")

        self._outbound_reader, self._outbound_writer = await asyncio.open_connection(
            host, port
        )
        print(f"connected to {host}:{port}.")
        if port == 443:
            self._target_host = f"https://{host}"
            print("Starting SSL handshake with target server...")
            client_ssl_context = ssl.create_default_context()
            # ssl.SSLContext(ssl.PROTOCOL_TLS)
            # client_ssl_context.set_ciphers("AES256-GCM-SHA384")
            # set_ciphers('@SECLEVEL=2:ECDH+AESGCM:ECDH+CHACHA20:ECDH+AES:DHE+AES:AESGCM:!aNULL:!eNULL:!aDSS:!SHA1:!AESCCM:!PSK')
            # client_ssl_context.verify_flags &= ~ssl.VERIFY_X509_STRICT
            # client_ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            client_ssl_context.check_hostname = False
            client_ssl_context.verify_mode = ssl.CERT_NONE

            await self._outbound_writer.start_tls(
                client_ssl_context, server_hostname=host
            )
            print("SSL handshake with target server completed")

        elif port == 80:
            self._target_host = f"http://{host}"
        else:
            self._target_host = f"http://{host}:{port}"

        self._writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        await self._writer.drain()

        if self._ssl_context:
            print("Starting SSL handshake with client...")
            await self._writer.start_tls(self._ssl_context)
            print("SSL handshake with client completed")

        print("Starting to relay data between client and target server...")
        loop = asyncio.get_event_loop()
        loop.create_task(self.relay(self._reader, self._outbound_writer, ">>"))
        await self.relay(self._outbound_reader, self._writer, "<<")
        print("Finished handling CONNECT request")

    async def relay(
        self, reader: StreamReader, writer: StreamWriter, desc: str
    ) -> None:
        try:
            while True:
                data = await reader.read(10240)
                if not data or len(data) == 0:
                    break
                print(f"{desc} {len(data)} bytes: {data[:100]!r}...")
                self._analyze_http(data, desc)
                writer.write(data)
                await writer.drain()
        except Exception as e:
            print(f"Error during relay {desc}: {e}")
        finally:
            writer.close()
            print(f"Relay connection {desc} closed")

    def _analyze_http(self, data: bytearray, desc: str) -> None:
        if desc == ">>":
            self._req_buffer.extend(data)
            if self._req_len > 0:
                if self._req_len <= len(self._req_buffer):
                    if self._traffic is not None:
                        self._traffic.req_body = (
                            self._traffic.req_body + self._req_buffer[: self._req_len]
                        )

                    self._req_buffer = self._req_buffer[self._req_len :]
                    self._req_len = 0
                else:
                    if self._traffic is not None:
                        self._traffic.req_body = (
                            self._traffic.req_body + elf._req_buffer
                        )
                    self._req_len = self._req_len - len(self._req_buffer)
                    self._req_buffer = bytearray()

            while b"\r\n\r\n" in self._req_buffer:
                req_str = read_block_till(self._req_buffer, b"\r\n\r\n").decode()

                request: HttpRequest = parse_request(req_str)
                print(f"http request {request.method} {request.path}.")
                self._traffic = Traffic(
                    service_name="http-proxy",
                    method=request.method,
                    url=self._target_host + request.path,
                    req_headers=request.headers,
                    req_body=b"",
                    status_code=0,
                    resp_headers={},
                    resp_body=b"",
                    timestamp=datetime.now(),
                    duration_ms=0,
                )
                print("created traffic object.")
                self._req_len = int(request.headers.get("Content-Length", "0"))
                if self._req_len > 0:
                    print(
                        f"request content-length={self._req_len} buf_len={len(self._req_buffer)}"
                    )
                    if self._req_len <= len(self._req_buffer):
                        self._traffic.req_body = (
                            self._traffic.req_body + self._req_buffer[: self._req_len]
                        )
                        self._req_buffer = self._req_buffer[self._req_len :]
                        self._req_len = 0
                    else:
                        self._req_len = self._req_len - len(self._req_buffer)
                        self._req_buffer = bytearray()
                pass

        else:
            self._resp_buffer.extend(data)
            if self._resp_chunked:
                return self._handle_chunked_response()

            if self._resp_len > 0:
                if self._resp_len <= len(self._resp_buffer):
                    if self._traffic is not None:
                        self._traffic.resp_body = (
                            self._traffic.resp_body
                            + self._resp_buffer[: self._resp_len]
                        )

                    self._resp_buffer = self._resp_buffer[self._resp_len :]
                    self._resp_len = 0
                    self._finish_response()
                else:
                    if self._traffic is not None:
                        self._traffic.resp_body = (
                            self._traffic.resp_body + self._resp_buffer
                        )
                    self._resp_len = self._resp_len - len(self._resp_buffer)
                    self._resp_buffer = bytearray()

            while b"\r\n\r\n" in self._resp_buffer:
                resp_str = read_block_till(self._resp_buffer, b"\r\n\r\n").decode()

                response = parse_response(resp_str)
                if self._traffic:
                    self._traffic.status_code = response.status_code
                    self._traffic.resp_headers = response.headers
                    print(
                        f"-- parsed resp {self._traffic.status_code} {len(self._traffic.resp_headers)} headers --"
                    )

                self._resp_len = int(response.headers.get("Content-Length", "0"))
                print(f"content-length={self._resp_len}")
                if self._resp_len > 0:
                    print(
                        f"response content-length={self._resp_len} buf_len={len(self._resp_buffer)}"
                    )
                    if self._resp_len <= len(self._resp_buffer):
                        self._traffic.resp_body = (
                            self._traffic.resp_body
                            + self._resp_buffer[: self._resp_len]
                        )
                        self._resp_buffer = self._resp_buffer[self._resp_len :]
                        self._resp_len = 0
                        self._finish_response()
                    else:
                        self._resp_len = self._resp_len - len(self._resp_buffer)
                        self._resp_buffer = bytearray()

                elif response.headers.get("Transfer-Encoding") == "chunked":
                    self._start_chunked_response()
                    self._handle_chunked_response()

    def _start_chunked_response(self) -> None:
        print("start chunked response")
        self._resp_chunked = True
        self._resp_len = -1

    def _handle_chunked_response(self) -> bool:
        while self._handle_a_chunk():
            pass

    def _handle_a_chunk(self) -> bool:
        if self._resp_len == -1:
            length_line = read_block_till(self._resp_buffer, b"\r\n")
            if length_line is None:
                return False
            self._resp_len = int(length_line.decode().strip(), 16)
            print(
                f"found a chuck size={self._resp_len} remaining: {self._resp_buffer[:50]!r}..."
            )

        if self._resp_len > 0:
            if self._resp_len + 2 <= len(self._resp_buffer):
                self._traffic.resp_body = (
                    self._traffic.resp_body + self._resp_buffer[: self._resp_len]
                )
                # next 2 bytes should be new line.
                if self._resp_buffer[self._resp_len : self._resp_len + 2] != b"\r\n":
                    print(f"left over: {self._resp_buffer[self._resp_len :]}")
                    raise IOError("Bad chunked data, should end with new line")
                del self._resp_buffer[: self._resp_len + 2]
                self._resp_len = -1
                return True
            else:
                # chunk not complete
                return False
        else:
            # end of chunked response.
            del self._resp_buffer[:2]
            self._resp_len = -1
            self._finish_response()
            return False

    def _finish_response(self) -> None:
        self._traffic.duration_ms = diff_ms(datetime.now(), self._traffic.timestamp)
        print(f"saving a traffic {self._traffic.method} {self._traffic.url}")
        AppState.add_traffic(self._traffic)
        self._traffic = None
