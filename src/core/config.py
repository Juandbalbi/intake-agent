from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class ConfigError(Exception):
    """Custom exception for configuration errors."""


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    PROMPTLAYER_API_KEY: str


try:
    settings = Config()
except ValueError as e:
    message = f"Invalid configuration: {e}"
    raise ConfigError(message) from e
