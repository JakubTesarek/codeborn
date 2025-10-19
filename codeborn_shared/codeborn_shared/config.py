from __future__ import annotations

import os
import importlib
from functools import cache
from pathlib import Path
from typing import Any, Callable, Self, get_origin, get_args

from dotenv import load_dotenv
import msgspec
import msgspec.toml

from codeborn_shared import to_abs_path, DEFAULT_CONFIG_PATH
from codeborn_shared.model import TerrainType, UnitType

from codeborn_engine.agents import BotAgent


load_dotenv()


def decoder_hook(expected_type: type, obj: Any) -> Any:
    """Custom decoder hook to resolve Path and type fields."""
    if expected_type is Path:
        return to_abs_path(obj)

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if (expected_type is type or origin is type) and isinstance(obj, str):
        module_name, _, class_name = obj.rpartition('.')
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)

        if origin is type and args:
            base = args[0]
            try:
                if not issubclass(cls, base):
                    raise TypeError(f'"{cls}" is not a subclass of "{base.__name__}"')
            except TypeError:
                pass

        return cls

    return obj


def env_var[T](var_name: str, default: Any = None, t: type[T] = str) -> Callable[[], T]:
    """Helper to get environment variable or default value."""

    def get_env() -> T:
        if var_name in os.environ:
            return t(os.environ[var_name])  # type: ignore
        if default is not None:
            return default
        raise ValueError(f'Environment variable "{var_name}" is not set and no default value provided.')

    return get_env


class LoggingConfig(msgspec.Struct):
    """Logging configuration."""

    level: str


class AgentsHeartbeatConfig(msgspec.Struct):
    """Agent heartbeat configuration."""

    interval: float
    timeout: float


class AgentsRestartConfig(msgspec.Struct):
    """Agent restart configuration."""

    interval: float


class StateUpdateConfig(msgspec.Struct):
    """State update configuration."""

    interval: float


class LifecycleConfig(msgspec.Struct):
    """Lifecycle management configuration."""

    restart: AgentsRestartConfig
    heartbeat: AgentsHeartbeatConfig
    state_update: StateUpdateConfig


class AgentsConfig(msgspec.Struct):
    """Agents configuration."""

    runtime_class: type[BotAgent]
    base_dir: Path
    container_image: str
    version_file: str

    def get_bot_dir(self, name: str) -> Path:
        """Get the directory for a specific bot by name."""
        return self.base_dir / name


class DatabaseConfig(msgspec.Struct):
    """Database configuration."""

    init_schema: bool = False
    name: str = msgspec.field(default_factory=env_var('CODEBORN_DB_NAME'))
    user: str = msgspec.field(default_factory=env_var('CODEBORN_DB_USER'))
    password: str = msgspec.field(default_factory=env_var('CODEBORN_DB_PASSWORD'))
    host: str = msgspec.field(default_factory=env_var('CODEBORN_DB_HOST'))
    port: int = msgspec.field(default_factory=env_var('CODEBORN_DB_PORT', 5432, int))
    pool_min_size: int = 1
    pool_max_size: int = 10
    timeout: float = 30.0
    command_timeout: float = 30.0
    models: list[str] = []

    @property
    def tortoise_config(self) -> dict[str, Any]:
        """Get the Tortoise ORM configuration dictionary."""
        return {
            'connections': {
                'default': {
                    'engine': 'tortoise.backends.asyncpg',
                    'credentials': {
                        'database': self.name,
                        'host': self.host,
                        'port': self.port,
                        'user': self.user,
                        'password': self.password,
                        'min_size': self.pool_min_size,
                        'max_size': self.pool_max_size,
                        'timeout': self.timeout,
                        'command_timeout': self.command_timeout,
                    }
                }
            },
            'apps': {
                'models': {
                    'models': self.models,
                    'default_connection': 'default',
                }
            }
        }


class GithubConfig(msgspec.Struct):
    """GitHub OAuth configuration."""

    redirect_url: str
    access_token_url: str
    authorize_url: str
    api_base_url: str
    scope: list[str]

    client_id: str = msgspec.field(default_factory=env_var('CODEBORN_GH_CLIENT_ID'))
    client_secret: str = msgspec.field(default_factory=env_var('CODEBORN_GH_CLIENT_SECRET'))


class JwtConfig(msgspec.Struct):
    """JWT configuration."""

    algorithm: str
    ttl: int
    secret: str = msgspec.field(default_factory=env_var('CODEBORN_JWT_SECRET'))


class TerrainConfig(msgspec.Struct):
    """Configuration for a terrain type."""

    movement_cost: float


class UnitConfig(msgspec.Struct):
    """Configuration for a unit type."""

    stamina_recovery: float


class MapGeneratorConfig(msgspec.Struct):
    """Configuration for the map generator."""

    width: int
    height: int


class GeneratorsConfig(msgspec.Struct):
    """Configuration for generators."""

    map: MapGeneratorConfig


class ApiConfig(msgspec.Struct):
    host: str
    port: int
    frontend_url: str
    app_name: str
    auto_reload: bool = False


class CodebornConfig(msgspec.Struct):
    """Configuration for the engine."""

    api: ApiConfig
    logging: LoggingConfig
    agents: AgentsConfig
    lifecycle: LifecycleConfig
    database: DatabaseConfig
    github: GithubConfig
    jwt: JwtConfig
    units: dict[UnitType, UnitConfig]
    terrain: dict[TerrainType, TerrainConfig]
    generators: GeneratorsConfig
    encryption_key: str = msgspec.field(default_factory=env_var('CODEBORN_ENCRYPTION_KEY'))

    @classmethod
    def load(cls, path: Path = DEFAULT_CONFIG_PATH) -> Self:
        """Load configuration from a TOML file."""
        path = to_abs_path(path)
        cfg = msgspec.toml.decode(path.read_bytes(), type=cls, dec_hook=decoder_hook)

        return cfg


@cache
def get_config() -> CodebornConfig:
    """Get the engine configuration from a TOML file."""
    return CodebornConfig.load()


if __name__ == '__main__':
    print(get_config())
