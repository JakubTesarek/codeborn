from __future__ import annotations

import enum
import importlib
import os
from functools import cache
from pathlib import Path
from typing import Any, Self, TYPE_CHECKING

import tomli
import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings import PydanticBaseSettingsSource
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from ansible.parsing.vault import VaultLib, VaultSecret

from codeborn.model import TerrainType, UnitType

if TYPE_CHECKING:
    from codeborn.engine.agents import BotAgent


ENV_PREFIX = 'CODEBORN_'
ENV_DELIMITER = '__'


class AppMode(enum.StrEnum):
    """Application mode."""

    development = 'development'
    production = 'production'

    @classmethod
    def from_env(cls) -> Self:
        """Load application mode from env variable"""
        app_mode = os.environ[f'{ENV_PREFIX}APP_MODE']
        return cls(app_mode)


def load_env_vars():
    """Load environment variables from .env and mode-based .env"""
    load_dotenv(dotenv_path='.env')
    if app_mode := os.environ.get(f'{ENV_PREFIX}APP_MODE'):
        load_dotenv(dotenv_path=f'.{app_mode}.env')


def get_vault_password() -> str:
    """Get Ansible vault password from a file or env variable"""
    if vault_pass := os.environ.get(f'{ENV_PREFIX}VAULT_PASS'):
        return vault_pass
    if pass_file := os.environ.get(f'{ENV_PREFIX}VAULT_PASS_FILE'):
        return Path(pass_file).expanduser().read_text().strip()
    raise ValueError('Ansible vault password missing')


class TomlSettingsSource(PydanticBaseSettingsSource):
    """Setting source reading variables from a toml file."""

    def __init__(self, settings_cls: type[BaseSettings], app_mode: AppMode) -> None:
        super().__init__(settings_cls)
        self._values = self._load_toml_file(app_mode)

    def _load_toml_file(self, app_mode: AppMode) -> dict[str, Any]:
        """Load toml file as a dict."""
        toml_file = Path(f'.{app_mode}.config.toml')

        if toml_file.is_file():
            with toml_file.open('rb') as f:
                return tomli.load(f)
        return {}

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        """Get a value of settings field"""
        field_value = self._values.get(field_name)
        return field_value, field_name, False

    def __call__(self) -> dict[str, Any]:
        """Get all configuration values."""
        state: dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            if field_value is not None:
                state[field_key] = field_value

        return state


class AnsibleVaultSettingsSource(PydanticBaseSettingsSource):
    """Setting source reading variables from a Ansible vault file."""

    def __init__(self, settings_cls: type[BaseSettings], app_mode: AppMode, vault_password: str) -> None:
        super().__init__(settings_cls)
        self._values = self._load_vault_file(app_mode, vault_password)

    def _load_vault_file(self, app_mode: AppMode, vault_password) -> dict[str, Any]:
        """Load vault file as a dict."""
        vault_file = Path(f'.{app_mode}.secrets.yml')
        vault_secret = VaultSecret(vault_password.encode())
        vault = VaultLib([('default', vault_secret)])
        decrypted_data = vault.decrypt(vault_file.read_bytes())
        return yaml.safe_load(decrypted_data) or {}

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        """Get a value of settings field"""
        field_value = self._values.get(field_name)
        return field_value, field_name, False

    def __call__(self) -> dict[str, Any]:
        """Get all configuration values."""
        state: dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            if field_value is not None:
                state[field_key] = field_value

        return state


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str


class AgentsHeartbeatConfig(BaseModel):
    """Agents heartbeat configuration."""

    interval: float
    timeout: float


class AgentsRestartConfig(BaseModel):
    """Agent restart policy configuration."""

    interval: float


class StateUpdateConfig(BaseModel):
    """Agents state update policy configuration."""

    interval: float


class MemoryUpdateConfig(BaseModel):
    """Agents memory update policy configuration."""

    interval: float
    max_size: int


class LifecycleConfig(BaseModel):
    """Game engine lifecycle configuration."""

    restart: AgentsRestartConfig
    heartbeat: AgentsHeartbeatConfig
    state_update: StateUpdateConfig
    memory_update: MemoryUpdateConfig


class AgentsConfig(BaseModel):
    """Game agent configuration."""

    runtime_class_name: str
    base_dir: Path
    container_image: str
    version_file: str

    @property
    def runtime_class(self) -> type[BotAgent]:
        """Get a class object for an agent."""
        module_name, class_name = self.runtime_class_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)


class DatabaseConfig(BaseModel):
    """Database configuration."""

    init_schema: bool = False
    name: str
    user: str
    password: str
    host: str
    port: int
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


class GithubConfig(BaseModel):
    """Github configuration."""

    redirect_url: str
    access_token_url: str
    authorize_url: str
    api_base_url: str
    scope: list[str]
    client_id: str
    client_secret: str


class JwtConfig(BaseModel):
    """JWT configuration."""

    algorithm: str
    ttl: int
    secret: str


class TerrainConfig(BaseModel):
    """Terrain configuration."""

    movement_cost: float


class UnitConfig(BaseModel):
    """Unit configuration."""

    stamina_recovery: float


class MapGeneratorConfig(BaseModel):
    """Map generator configuration."""

    width: int
    height: int


class GeneratorsConfig(BaseModel):
    """Generators configuration."""

    map: MapGeneratorConfig


class AuthConfig(BaseModel):
    """Authentication configuration."""

    cookie_domain: str
    secure_cookie: bool
    jwt: JwtConfig


class ApiConfig(BaseModel):
    """API configuration."""

    host: str
    port: int
    frontend_url: str
    app_name: str
    auto_reload: bool = False
    session_key: str


class CodebornConfig(BaseSettings):
    """Main application configuration."""

    api: ApiConfig
    logging: LoggingConfig
    agents: AgentsConfig
    lifecycle: LifecycleConfig
    database: DatabaseConfig
    github: GithubConfig
    auth: AuthConfig
    units: dict[UnitType, UnitConfig]
    terrain: dict[TerrainType, TerrainConfig]
    generators: GeneratorsConfig

    model_config = SettingsConfigDict(
        arbitrary_types_allowed=True,
        env_prefix=ENV_PREFIX,
        env_nested_delimiter=ENV_DELIMITER
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        *args, **kwargs
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize order and type of configuration sources."""
        app_mode = AppMode.from_env()

        return (
            env_settings,
            TomlSettingsSource(settings_cls, app_mode),
            AnsibleVaultSettingsSource(settings_cls, app_mode, get_vault_password()),
            init_settings,
        )


@cache
def get_config() -> CodebornConfig:
    """Get application configuration."""
    load_env_vars()
    return CodebornConfig()  # type: ignore


if __name__ == '__main__':
    cfg = get_config()
    print(cfg.model_dump())
