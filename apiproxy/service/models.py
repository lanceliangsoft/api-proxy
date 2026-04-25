from typing import Dict, List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, LargeBinary, DateTime, JSON


class HttpRequest:
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[bytearray]

    def __init__(self, method: str, path: str, headers: dict):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = None


class HttpResponse:
    status_code: int
    message: str
    headers: Dict[str, str]
    body: Optional[bytearray]

    def __init__(
        self,
        status_code: int,
        message: str,
        headers: Dict[str, str],
        body: Optional[bytearray],
    ):
        self.status_code = status_code
        self.message = message
        self.headers = headers
        self.body = body


# rest
class SwitchServiceRequest(SQLModel):
    name: str
    active: bool


class GenerateRequest(SQLModel):
    trafficId: int
    format: str


class GeneratedFile(SQLModel):
    file_name: str
    content: str


class GenerateResponse(SQLModel):
    files: List[GeneratedFile]


# db
class MappedServiceBase(SQLModel):
    name: str = Field(primary_key=True, max_length=255)
    port: int
    forward_url: str = Field(max_length=2048)
    active: bool = True


class MappedServiceEntity(MappedServiceBase, table=True):
    __tablename__ = "mapped_service"
    pass


class MappedService(MappedServiceBase):
    up: bool = False
    pass


class TrafficBase(SQLModel):
    id: int | None = Field(primary_key=True, default=None)
    service_name: str = Field(index=True, max_length=255)
    method: str = Field(max_length=10)
    url: str = Field(max_length=2048)
    req_headers: Dict[str, str] = Field(sa_column=Column(JSON))
    req_body: Optional[bytes] = Field(sa_column=Column(LargeBinary))
    status_code: int
    resp_headers: Dict[str, str] = Field(sa_column=Column(JSON))
    resp_body: Optional[bytes] = Field(sa_column=Column(LargeBinary))
    timestamp: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    duration_ms: int


class TrafficEntity(TrafficBase, table=True):
    __tablename__ = "traffic"
    pass


class Traffic(TrafficBase):
    pass
