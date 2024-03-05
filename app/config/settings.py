from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
import os


BASE_DIR = Path(__file__).parent.parent.parent


class DbSettings(BaseSettings):
    user: str = Field(alias="DB_USER")
    password: str = Field(alias="DB_PASSWORD")
    host: str = Field(alias="DB_HOST")
    port: str = Field(alias="DB_PORT")
    dbname: str = Field(alias="DB_NAME")

    @property
    def url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"

    # echo: bool = False
    echo: bool = True


class AuthJWT(BaseSettings):
    jwt_alg: str = "RS256"
    access_private_path: Path = BASE_DIR / "certs" / "access-private.pem"
    access_public_path: Path = BASE_DIR / "certs" / "access-public.pem"
    access_token_expire: int = 5  # minutes

    refresh_private_path: Path = BASE_DIR / "certs" / "refresh-private.pem"
    refresh_public_path: Path = BASE_DIR / "certs" / "refresh-public.pem"
    refresh_token_expire: int = 60 * 24 * 21  # minutes (21 days)

    secure_cookies: bool = True


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"

    db: DbSettings = DbSettings()

    auth_config: AuthJWT = AuthJWT()


settings = Settings()
