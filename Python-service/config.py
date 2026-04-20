from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 6000
    backend_url: str = "http://localhost:5007"
    backend_email: str = "admin@school-admin.com"
    backend_password: str = "3OU4zn3q6Zh9"

    class Config:
        env_file = ".env"

settings = Settings()