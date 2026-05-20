from .service.engine import start_servers
from .service.api import run_fastapi
from .service.mcp_server import run_mcp_server

if __name__ == "__main__":
    start_servers()
    run_mcp_server(9000)

    # print("Starting REST API on port 8000")
    run_fastapi(8000)
