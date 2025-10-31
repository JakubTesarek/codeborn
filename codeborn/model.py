from __future__ import annotations

import inspect
import json
from functools import cached_property
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Self
from uuid import UUID, uuid4
from enum import StrEnum

from configobj import ConfigObj
from tortoise import fields, models
from github.Repository import Repository
from github import Github
from git import Repo

from codeborn.client.messages import MessageType


if TYPE_CHECKING:
    from codeborn.config import UnitConfig, TerrainConfig


def dump_dt(dt: datetime | None) -> str | None:
    """Helper function to dump datetime in iso format or None."""
    return dt.isoformat() if dt else None


def dump_td(td: timedelta | None) -> float | None:
    """Helper function to dump timedelta in seconds or None."""
    return td.total_seconds() if td else None


class BotState(StrEnum):
    """Enumeration of different bot states."""

    running = 'running'
    disabled = 'disabled'
    starting = 'starting'
    restarting = 'restarting'
    unresponsive = 'unresponsive'

    async def dump(self, exclude: list[str] | set[str] | None = None) -> str:
        """Dump the bot state as a string."""
        return self.value


class TerrainType(StrEnum):
    """Enumeration of different terrain types."""

    plains = 'plains'
    forest = 'forest'

    @cached_property
    def config(self) -> TerrainConfig:
        """Get the configuration for this unit type."""
        from codeborn.config import get_config
        return get_config().terrain[self]

    @property
    def movement_cost(self) -> float:
        """Get the movement cost multiplier for this terrain type."""
        return self.config.movement_cost

    async def dump(self, exclude: list[str] | set[str] | None = None) -> str:
        """Dump the terrain type as a string."""
        return self.value


class UnitType(StrEnum):
    """Enumeration of different unit types."""

    light_infantry = 'light_infantry'
    heavy_infantry = 'heavy_infantry'
    spearmen = 'spearmen'
    light_cavalry = 'light_cavalry'
    heavy_cavalry = 'heavy_cavalry'
    archer = 'archer'
    crossbowman = 'crossbowman'

    @cached_property
    def config(self) -> UnitConfig:
        """Get the configuration for this unit type."""
        from codeborn.config import get_config
        return get_config().units[self]

    @property
    def stamina_recovery(self) -> float:
        """Get the stamina recovery rate for this unit type."""
        return self.config.stamina_recovery

    async def dump(self, exclude: list[str] | set[str] | None = None) -> str:
        """Dump the unit type as a string."""
        return self.value


class CodebornModel(models.Model):
    """Base class for all Codeborn models."""

    class Meta:
        abstract = True

    async def dump(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any]:
        """Dump the model as a dictionary."""
        return await self._dump({}, exclude)

    async def _dump(
        self,
        fields: dict[str, Callable[[Self, list[str] | set[str] | None], Awaitable[Any] | Any]],
        exclude: list[str] | set[str] | None = None,
    ) -> dict[str, Any]:
        """Dump the model as a dictionary with recursive exclude support."""
        exclude = exclude or []
        exclude_map: dict[str, set[str]] = {}
        for key in exclude:
            if '__' in key:
                prefix, sub_key = key.split('__', 1)
                exclude_map.setdefault(prefix, set()).add(sub_key)
            else:
                exclude_map.setdefault(key, set())

        result: dict[str, Any] = {}

        for key, getter in fields.items():
            if key in exclude_map and not exclude_map[key]:
                continue

            nested_exclude = exclude_map.get(key)
            value = getter(list(nested_exclude) if nested_exclude else None)  # type: ignore
            result[key] = await value if inspect.isawaitable(value) else value

        return result


class Location(CodebornModel):
    """A location in the system."""

    gid = fields.UUIDField(pk=True, default=uuid4)
    x = fields.IntField()
    y = fields.IntField()
    terrain = fields.CharEnumField(TerrainType, default=TerrainType.plains)

    class Meta:
        unique_together = (('x', 'y'),)

    async def dump(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any]:
        """Dump the location as a dictionary."""
        fields = {
            'gid': lambda e: str(self.gid),
            'terrain': lambda e: self.terrain.dump(e),
            'x': lambda e: self.x,
            'y': lambda e: self.y
        }
        return await self._dump(fields, exclude=exclude)

    def is_adjacent(self, other: Location) -> bool:
        """Check if this location is adjacent to another location."""
        delta_x = abs(self.x - other.x)
        delta_y = abs(self.y - other.y)
        return (delta_x <= 1) and (delta_y <= 1) and (delta_x + delta_y > 0)

    def __eq__(self, other: Location) -> bool:
        """Check if two locations are the same."""
        return self.x == other.x and self.y == other.y


class User(CodebornModel):
    """A user in the system."""

    gid = fields.UUIDField(pk=True, default=uuid4)
    max_bots = fields.IntField(default=1)

    bots: fields.ReverseRelation['Bot']
    github: fields.ReverseRelation['GitHubAccount']

    async def dump(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any]:
        async def dump_bots(self, exclude: list[str] | set[str] | None = None) -> list[dict[str, Any]]:
            return [await bot.dump(exclude) for bot in await self.bots.all()]

        async def dump_github(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any] | None:
            github = await self.github
            return await github.dump(exclude) if github else None

        fields = {
            'gid': lambda e: str(self.gid),
            'github': lambda e: dump_github(self, e),  # type: ignore
            'bots': lambda e: dump_bots(self, e),
        }
        return await self._dump(fields, exclude=exclude)


class GitHubAccount(CodebornModel):
    """A GitHub account linked to a user."""

    gid = fields.UUIDField(pk=True, default=uuid4)
    user = fields.OneToOneField('models.User', related_name='github', on_delete=fields.CASCADE)
    github_id = fields.IntField(unique=True)
    login = fields.CharField(max_length=100)
    access_token = fields.CharField(max_length=200)
    token_type = fields.CharField(max_length=50)
    scope = fields.CharField(max_length=200)
    avatar_url = fields.CharField(max_length=300, null=True)
    last_update = fields.DatetimeField(null=True)

    repos: fields.ReverseRelation['GithubRepo']

    @property
    def gh(self) -> Github:
        """Get a GitHub client for this account."""
        return Github(self.access_token)

    @property
    def gh_user(self) -> Any:
        """Get the GitHub user object."""
        return self.gh.get_user()

    async def dump(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any]:
        """Dump the github account as a dictionary."""
        async def dump_repos(self, exclude: list[str] | set[str] | None = None) -> list[dict[str, Any]]:
            return [await repo.dump(exclude) for repo in await self.repos.all()]

        fields = {
            'gid': lambda e: str(self.gid),
            'github_id': lambda e: self.github_id,
            'login': lambda e: self.login,
            'avatar_url': lambda e: self.avatar_url,
            'last_update': lambda e: dump_dt(self.last_update),
            'repos': lambda e: dump_repos(self, e),
        }
        return await self._dump(fields, exclude=exclude)


class GithubRepo(CodebornModel):
    """A GitHub repository linked to an account."""

    gid = fields.UUIDField(pk=True, default=uuid4)
    github_account = fields.ForeignKeyField('models.GitHubAccount', related_name='repos', on_delete=fields.CASCADE)
    github_id = fields.IntField(unique=True)
    name = fields.CharField(max_length=200)
    full_name = fields.CharField(max_length=200)
    size = fields.IntField()
    clone_url = fields.CharField(max_length=300)
    html_url = fields.CharField(max_length=300)
    remote_version = fields.CharField(max_length=10, null=True)
    remote_sha = fields.CharField(max_length=40, null=True)

    @property
    def gh_repo(self) -> Repository:
        """Get the GitHub repository object."""
        return self.github_account.gh.get_repo(self.full_name)

    @property
    def local_clone_path(self) -> Path:
        """Get the local clone path for this repository."""
        from codeborn.config import get_config
        return Path(f'{get_config().agents.base_dir}/{self.full_name}').expanduser()

    @property
    def is_cloned(self) -> bool:
        """Check if the repository is cloned locally."""
        return self.local_clone_path.exists()

    @property
    def local_repo(self) -> Repo | None:
        """Get the local Git repository object."""
        if self.is_cloned:
            return Repo(self.local_clone_path)

    @property
    def local_version(self) -> str | None:
        """Get the local version from codeborn.ini if available."""
        from codeborn.config import get_config
        ini_path = self.local_clone_path / get_config().agents.version_file

        if not ini_path.exists():
            return None

        ini_config = ConfigObj(ini_path.read_text().splitlines())
        if (version := ini_config.get('version', None)) is not None:
            return str(version)

    @property
    def local_sha(self) -> str | None:
        """Get the local git SHA if the repository is cloned."""
        if local_repo := self.local_repo:
            return local_repo.head.commit.hexsha[:7]

    async def dump(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any]:
        """Dump the GitHub repository as a dictionary."""
        fields = {
            'gid': lambda e: str(self.gid),
            'name': lambda e: self.name,
            'full_name': lambda e: self.full_name,
            'clone_url': lambda e: self.clone_url,
            'html_url': lambda e: self.html_url,
            'size': lambda e: self.size,
            'remote_version': lambda e: self.remote_version,
            'remote_sha': lambda e: self.remote_sha,
            'local_version': lambda e: self.local_version,
            'local_sha': lambda e: self.local_sha,
        }
        return await self._dump(fields, exclude=exclude)


class Bot(CodebornModel):
    """A bot account linked to a user."""

    gid = fields.UUIDField(pk=True, default=uuid4)
    name = fields.CharField(max_length=50)
    user = fields.ForeignKeyField('models.User', related_name='bots', on_delete=fields.CASCADE)
    entry_point = fields.CharField(max_length=100, null=True)
    restart_requested = fields.BooleanField(default=False)
    last_heartbeat = fields.DatetimeField(null=True)
    start_at = fields.DatetimeField(null=True)
    enabled = fields.BooleanField(default=True)

    armies: fields.ReverseRelation['Army']
    messages: fields.ReverseRelation['Message']

    class Meta:
        unique_together = (('user_id', 'name'),)

    @property
    def heartbeat_age(self) -> timedelta | None:
        """Get the age of the last heartbeat."""
        if self.last_heartbeat is not None:
            return datetime.now(timezone.utc) - self.last_heartbeat

    @property
    def uptime(self) -> timedelta | None:
        """Get the uptime of the bot."""
        if self.start_at:
            return datetime.now(timezone.utc) - self.start_at

    @property
    def entry_point_path(self) -> Path:
        """Get the local entry point path for this bot."""
        from codeborn.config import get_config
        return Path(f'{get_config().agents.base_dir}/{self.entry_point}').expanduser()

    @property
    def state(self) -> BotState:
        """Get the current state of the bot."""
        if not self.enabled:
            return BotState.disabled

        if self.last_heartbeat is None:
            return BotState.starting

        if self.restart_requested:
            return BotState.restarting

        from codeborn.config import get_config
        heartbeat_timeout = get_config().lifecycle.heartbeat.timeout
        if self.heartbeat_age and self.heartbeat_age.total_seconds() > heartbeat_timeout:  # type: ignore
            return BotState.unresponsive

        return BotState.running

    async def dump(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any]:
        """Dump the bot as a dictionary."""
        async def dump_armies(self, exclude: list[str] | set[str] | None = None) -> list[dict[str, Any]]:
            return [await army.dump(exclude) for army in await self.armies.all()]

        fields = {
            'gid': lambda e: str(self.gid),
            'name': lambda e: self.name,
            'armies': lambda e: dump_armies(self, e),
            'entry_point': lambda e: self.entry_point,
            'restart_requested': lambda e: self.restart_requested,
            'last_heartbeat': lambda e: dump_dt(self.last_heartbeat),
            'start_at': lambda e: dump_dt(self.start_at),
            'enabled': lambda e: self.enabled,
            'state': lambda e: self.state.dump(e),
            'heartbeat_age_sec': lambda e: dump_td(self.heartbeat_age),
            'uptime_sec': lambda e: dump_td(self.uptime),
        }

        return await self._dump(fields, exclude=exclude)


class Army(CodebornModel):
    """An army belonging to a user."""

    gid = fields.UUIDField(pk=True, default=uuid4)
    bot = fields.ForeignKeyField('models.Bot', related_name='armies', on_delete=fields.CASCADE)
    location = fields.ForeignKeyField('models.Location', related_name='armies', on_delete=fields.CASCADE)

    units: fields.ReverseRelation['Unit']

    async def dump(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any]:
        """"Dump the army as a dictionary."""
        async def dump_units(self, exclude: list[str] | set[str] | None = None) -> list[dict[str, Any]]:
            return [await unit.dump(exclude) for unit in await self.units.all()]

        async def dump_location(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any]:
            location = await self.location
            return await location.dump(exclude)

        fields = {
            'gid': lambda e: str(self.gid),
            'bot_gid': lambda e: str(self.bot_id),  # type: ignore
            'location': lambda e: dump_location(self, e),
            'units': lambda e: dump_units(self, e),
        }
        return await self._dump(fields, exclude=exclude)


class Unit(CodebornModel):
    """A unit in an army."""

    gid = fields.UUIDField(pk=True, default=uuid4)
    army = fields.ForeignKeyField('models.Army', related_name='units', on_delete=fields.CASCADE)
    type = fields.CharEnumField(UnitType)
    stamina_snapshot = fields.FloatField(default=1.0)
    count = fields.IntField()
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        unique_together = (('type', 'army'),)

    @property
    def stamina(self) -> float:
        """Dynamically computed stamina."""
        if not self.updated_at:
            return self.stamina_snapshot
        update_age = (datetime.now(timezone.utc) - self.updated_at).total_seconds()
        recovered_stamina = update_age * self.type.stamina_recovery
        return max(0.0, min(1.0, self.stamina_snapshot + recovered_stamina))

    @stamina.setter
    def stamina(self, value: float) -> None:
        """Persist new stamina and update timestamp."""
        self.stamina_snapshot = value
        self.updated_at = datetime.now(timezone.utc)

    async def snapshot_stamina(self) -> None:
        """Snapshot the current stamina into stamina_snapshot."""
        self.stamina_snapshot = self.stamina
        self.updated_at = datetime.now(timezone.utc)
        await self.save(update_fields=['stamina'])

    async def save(self, *args, update_fields: list[str] | None = None, **kwargs) -> None:
        """Ensure updated_at is included when stamina is updated."""
        if update_fields:  # only if specific fields are being updated
            if 'stamina' in update_fields:
                update_fields.remove('stamina')  # stamina is computed, not stored
                update_fields.append('stamina_snapshot')

            if 'stamina_snapshot' in update_fields and 'updated_at' not in update_fields:
                update_fields.append('updated_at')
                self.updated_at = datetime.now(timezone.utc)

        await super().save(*args, update_fields=update_fields, **kwargs)

    async def dump(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any]:
        """Dump the unit as a dictionary."""
        fields = {
            'gid': lambda e: str(self.gid),
            'type': lambda e: self.type.dump(e),
            'stamina': lambda e: self.stamina,
            'count': lambda e: self.count,
        }
        return await self._dump(fields, exclude=exclude)


class Message(CodebornModel):
    """A message associated with a user."""

    gid = fields.UUIDField(pk=True, default=uuid4)
    bot = fields.ForeignKeyField('models.Bot', related_name='messages', on_delete=fields.CASCADE)
    type = fields.CharEnumField(MessageType)
    datetime = fields.DatetimeField(default_factory=lambda: datetime.now(timezone.utc))
    response_to = fields.UUIDField(null=True)
    payload = fields.JSONField(default=dict)

    def __init__(self, *args, **kwargs) -> None:
        if 'datetime' not in kwargs:
            kwargs['datetime'] = datetime.now(timezone.utc)
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        """Custom representation showing type and gid."""
        return f'<Message {self.type.value}: {self.gid}>'

    @classmethod
    def from_bytes(cls, bot_id: UUID, raw: bytes) -> Self:
        """Create an unsaved Message instance from JSON bytes (newline-safe)."""
        data = json.loads(raw.strip().decode())
        gid = UUID(data['gid']) if 'gid' in data else uuid4()

        return cls(
            gid=gid,
            bot_id=bot_id,
            type=data['type'],
            payload=data.get('payload', {}),
            datetime=datetime.fromisoformat(data['datetime']),
        )

    def to_bytes(self) -> bytes:
        """Serialize this Message instance into newline-terminated JSON bytes."""
        data = {
            'gid': str(self.gid),
            'bot_id': str(self.bot_id),  # type: ignore
            'type': self.type,
            'datetime': self.datetime.isoformat(),
            'response_to': str(self.response_to) if self.response_to else None,
            'payload': self.payload,
        }
        return json.dumps(data, ensure_ascii=False).encode() + b'\n'

    async def dump(self, exclude: list[str] | set[str] | None = None) -> dict[str, Any]:
        """Dump the message as a dictionary."""
        fields = {
            'gid': lambda e: str(self.gid),
            'bot_gid': lambda e: str(self.bot_id),  # type: ignore
            'type': lambda e: self.type.value,
            'datetime': lambda e: dump_dt(self.datetime),
            'payload': lambda e: self.payload,
        }
        return await self._dump(fields, exclude=exclude)
