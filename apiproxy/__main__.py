from .service.engine import start_servers
from .service.api import run_fastapi

if __name__ == "__main__":
    start_servers()
    # print("Starting REST API on port 8000")
    run_fastapi(8000)
