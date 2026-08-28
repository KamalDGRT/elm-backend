from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_username: str
    database_password: str
    database_name: str
    secret_key: str
    refresh_token_secret_key: str
    # Fernet key (Fernet.generate_key()) used to reversibly encrypt the
    # plaintext password so Root/Admin can view it later.
    password_encryption_key: str
    algorithm: str
    access_token_expire_minutes: int
    deployment_env: str
    cors_origins: str = "http://localhost:3000"
    # user_id of the single Root account. Root is identified by this id, not
    # by role name/id, since there's only ever one.
    root_user_id: Optional[int] = None

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
