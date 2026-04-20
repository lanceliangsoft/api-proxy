import asyncio
from asyncio import CancelledError, Server, StreamReader, StreamWriter
from typing import Optional
import ssl
from ..service.app_state import AppState
from ..service.models import MappedService, HttpRequest
from .http_util import parse_request, read_block_till, read_block_of_len


class BaseConnection:
    def __init__(
        self,
        reader: StreamReader,
        writer: StreamWriter,
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        self._reader = reader
        self._writer = writer
        self._ssl_context = ssl_context
        self._buffer = bytearray()

    async def serve(self) -> None:
        pass

    async def read_data(self, delimiter: bytes) -> Optional[bytearray]:
        while True:
            data = await self._reader.read(4096)
            if not data or len(data) == 0:
                return None
            print(f"Received {len(data)}: {data.decode()}")
            self._buffer.extend(data)

            return read_block_till(self._buffer, delimiter)

    async def read_data_of_len(self, length: int) -> Optional[bytearray]:
        while True:
            data = await self._reader.read(4096)
            if not data or len(data) == 0:
                return None
            print(f"Received {len(data)}: {data.decode()}")
            self._buffer.extend(data)

            return read_block_of_len(self._buffer, length)

    async def read_data_till_close(self) -> Optional[bytearray]:
        while True:
            data = await self._reader.read(4096)
            if not data or len(data) == 0:
                break

            print(f"Received {len(data)}: {data.decode()}")
            self._buffer.extend(data)

        return read_block_of_len(self._buffer, len(self._buffer))


class HttpConnection(BaseConnection):
    def __init__(
        self,
        reader: StreamReader,
        writer: StreamWriter,
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        super().__init__(reader, writer, ssl_context)

    async def serve(self) -> None:
        print("started to serve...")
        if self._ssl_context:
            print("Starting SSL handshake...")
            await self._writer.start_tls(self._ssl_context)
            print("SSL handshake completed")

        request_headers = await self.read_data(b"\r\n\r\n")
        if request_headers is not None:
            request = parse_request(request_headers.decode("utf8"))
            print(f"Received request: {request.method} {request.path}")

            await self.do_service(request)
            await self._writer.drain()
            print("Sent response, closing connection")

        self._writer.close()
        print("Connection closed")

    async def do_service(self, request: HttpRequest):
        payload = "Hello world!"
        self.write_status(200)
        self.write_header("Content-Type", "text/plain")
        self.write_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.write(payload.encode("utf8"))

    def write_status(self, status_code: int, status_message: str = None):
        status_line = f"HTTP/1.1 {status_code} {status_message or ('OK' if status_code == 200 else 'Error')}\r\n"
        self._writer.write(status_line.encode("utf8"))

    def write_header(self, key: str, value: str):
        header_line = f"{key}: {value}\r\n"
        self._writer.write(header_line.encode("utf8"))

    def end_headers(self):
        self._writer.write(b"\r\n")

    def write(self, data: bytes):
        self._writer.write(data)


class TcpServer:
    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        ssl_context=None,
    ):
        self._name = name
        self._host = host
        self._port = port
        self._ssl_context = ssl_context

        AppState.engine.create_service(
            service=MappedService(
                name=name, port=port, forward_url="", active=True, up=False
            )
        )

    async def start(self):
        try:
            server = await asyncio.start_server(
                self._handle_connection, self._host, self._port
            )
            AppState.servers[self._name] = server
            print(f"server {self._name} listens on {self._host}:{self._port}...")

            async with server:
                await server.serve_forever()
        except CancelledError as e:
            print(e)

        print(f"service {self._name} stops.")

    async def _handle_connection(self, reader: StreamReader, writer: StreamWriter):
        print(f"connection from {writer.get_extra_info('peername')}")
        connection = self.create_connection(reader, writer, self._ssl_context)
        await connection.serve()

    def create_connection(
        self, reader: StreamReader, writer: StreamWriter, ssl_context
    ) -> BaseConnection:
        return BaseConnection(reader, writer, ssl_context)


class HttpServer(TcpServer):
    def __init__(
        self,
        host: str,
        port: int,
        ssl_context=None,
    ):
        super().__init__("http", host, port, ssl_context)

    def create_connection(
        self, reader: StreamReader, writer: StreamWriter, ssl_context
    ) -> BaseConnection:
        return HttpConnection(reader, writer, ssl_context)
