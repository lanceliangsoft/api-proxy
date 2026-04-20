import os
import sys
from typing import Literal
from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_STR: str = "/api"
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    API_PORT: int = 8000
    HTTP_PROXY_PORT: int = 8001
    FRONTEND_URL: str = f"http://localhost:{API_PORT}"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        if 'pytest' in sys.modules:
            print("Running in test mode")
            return "sqlite:///./test.db"
        
        else:
            db_file = f"{self.get_db_path()}/apiproxy.db"
            print(f"Running in {self.ENVIRONMENT} environment, using SQLite {db_file}")
            return f"sqlite:///{db_file}"

    def get_db_path(self) -> str:

        db_path = os.path.expanduser("~/.apiproxy")
        os.makedirs(db_path, exist_ok=True)
        return db_path


settings = Settings()
