import asyncio
import json
from datetime import datetime
import threading
from typing import Optional

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session

from .app_state import AppState
from .crud import (
    engine as _db_engine,
    get_traffic_by_id,
    query_traffics,
    select_service,
    select_service_by_name,
)

mcp = FastMCP("api-proxy")


def _service_dict(entity) -> dict:
    return {
        "name": entity.name,
        "port": entity.port,
        "forward_url": entity.forward_url,
        "active": entity.active,
        "up": AppState.is_service_up(entity.name),
    }


def _traffic_dict(traffic) -> dict:
    return {
        "id": traffic.id,
        "service_name": traffic.service_name,
        "method": traffic.method,
        "url": traffic.url,
        "req_headers": traffic.req_headers,
        "req_body": traffic.req_body.decode("utf-8", errors="replace")
        if traffic.req_body
        else None,
        "status_code": traffic.status_code,
        "resp_headers": traffic.resp_headers,
        "resp_body": traffic.resp_body.decode("utf-8", errors="replace")
        if traffic.resp_body
        else None,
        "timestamp": traffic.timestamp.isoformat() if traffic.timestamp else None,
        "duration_ms": traffic.duration_ms,
    }


@mcp.tool()
async def list_services() -> str:
    """List all configured proxy services with their running status."""
    with Session(_db_engine) as session:
        return json.dumps([_service_dict(s) for s in select_service(session)])


@mcp.tool()
async def get_service(name: str) -> str:
    """Get a proxy service by name.

    Args:
        name: Service name
    """
    with Session(_db_engine) as session:
        entity = select_service_by_name(session, name)
        if entity is None:
            return json.dumps({"error": f"Service '{name}' not found"})
        return json.dumps(_service_dict(entity))


@mcp.tool()
async def list_traffics(
    service_name: str,
    begin_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 50,
) -> str:
    """Query captured HTTP traffic records for a service.

    Args:
        service_name: Name of the proxy service
        begin_time: ISO 8601 start timestamp, e.g. "2024-01-01T00:00:00"
        end_time: ISO 8601 end timestamp
        limit: Maximum records to return (default 50)
    """
    begin_dt = datetime.fromisoformat(begin_time) if begin_time else None
    end_dt = datetime.fromisoformat(end_time) if end_time else None
    with Session(_db_engine) as session:
        rows = query_traffics(session, service_name, begin_dt, end_dt, limit=limit)
        return json.dumps([_traffic_dict(t) for t in rows])


@mcp.tool()
async def get_traffic(id: int) -> str:
    """Get a single captured traffic record by ID.

    Args:
        id: Traffic record ID
    """
    with Session(_db_engine) as session:
        traffic = get_traffic_by_id(session, id)
        if traffic is None:
            return json.dumps({"error": f"Traffic record {id} not found"})
        return json.dumps(_traffic_dict(traffic))


#TODO fix: currently FastMCP does not support async tool function, so we have to run it in a separate thread to avoid blocking the main thread which runs the REST API server. We should look into properly supporting async functions in FastMCP in the future.    
def run_mcp_server_in_thread(host, port):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(mcp.run())


def run_mcp_server(port: int) -> None:
    print(f"Starting MCP server on port {port}...")
    server_thread = threading.Thread(
        target=run_mcp_server_in_thread, args=("127.0.0.1", port), daemon=True
    )
    server_thread.start()
    print(f"MCP server started on port {port}")
