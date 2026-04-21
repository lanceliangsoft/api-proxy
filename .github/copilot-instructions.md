# AI Coding Agent Instructions for api-proxy

## Project Overview
This is an API proxy tool that traces, simulates, and analyzes REST API calls. It consists of:
- Python FastAPI backend for REST API management
- Angular 21 UI for management console
- HTTP proxy server that intercepts and logs traffic
- Mapped service forwarders that proxy requests to remote APIs
- SQLite database for configuration and traffic storage

## Architecture
- **Backend**: FastAPI app running on port 8000 with endpoints under `/api/`
- **UI**: Angular app served from `/console/` route, built to `static/browser/`
- **Proxy**: HTTP proxy on port 8001 that logs all traffic
- **Mapped Services**: User-configurable services on custom ports that forward to remote URLs
- **Database**: SQLite at `~/.apiproxy/apiproxy.db` using SQLModel ORM
- **State Management**: Global `AppState` singleton for runtime state

## Key Components
- `apiproxy/service/engine.py`: Service lifecycle management (start/stop servers)
- `apiproxy/service/api.py`: FastAPI endpoints for CRUD operations
- `apiproxy/handler/http_proxy.py`: Async HTTP proxy with traffic logging
- `apiproxy/handler/mapped_service.py`: Synchronous service forwarder
- `apiproxy/service/models.py`: SQLModel entities (MappedService, Traffic)
- `apiproxy/service/crud.py`: Database operations
- `apiproxy/service/app_state.py`: Global state and traffic storage

## Development Workflow
1. **Setup**: `python -m venv .venv && .venv\Scripts\activate && uv sync`
2. **Certificates**: `python make_cert.py` (creates `~/.apiproxy/certs/`)
3. **Run**: `python -m apiproxy` (starts backend + UI on port 8000)
4. **UI Access**: http://localhost:8000/console
5. **API Access**: http://localhost:8000/api/services

## Coding Patterns
- **Dependency Injection**: Use `EngineDep = Annotated[Engine, Depends(engine_factory)]`
- **Database**: Use `SessionDep` for SQLModel sessions
- **Threading**: Services run in daemon threads via `threading.Thread`
- **Async**: Use asyncio for server management, synchronous handlers for requests
- **Models**: Separate `Entity` (table) and response models
- **Traffic Logging**: Store request/response with timestamps and durations
- **SSL**: Load certs from `~/.apiproxy/certs/` for HTTPS support

## Service Management
- Services are identified by name (e.g., "console-api", "http-proxy")
- Each service has port, forward_url, active status, and up status
- Active services start automatically on app launch
- Switching active status starts/stops the service thread

## Traffic Analysis
- All HTTP traffic logged to `Traffic` table with full req/resp details
- Used for generating curl commands and code snippets
- Accessible via `/api/traffics/{service_name}`

## UI Integration
- Angular services in `apiproxy-ui/src/app/services/`
- CORS enabled for localhost:4200 (dev) and all origins (prod)
- Build output goes to `../static` relative to UI directory

## Testing
- Python: `pytest` in `tests/` directory
- Angular: `ng test` with Vitest
- Run tests after changes to ensure functionality

## File Structure Conventions
- `apiproxy/` root package
- `service/` for backend logic and data models
- `handler/` for HTTP server implementations
- `generate/` for code generation from traffic
- `apiproxy-ui/` for Angular frontend
- `static/` for built UI assets

## Common Tasks
- Adding new service types: Extend `Engine.start_service()` and add handler
- New API endpoints: Add to `api.py` with proper dependencies
- UI features: Create components in `apiproxy-ui/src/app/components/`
- Database changes: Update models in `models.py` and run migrations if needed</content>
<parameter name="filePath">.github/copilot-instructions.md