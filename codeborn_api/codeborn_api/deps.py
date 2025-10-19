from fastapi import Request
from authlib.integrations.starlette_client import OAuth

from codeborn_shared.config import CodebornConfig


def get_oauth(request: Request) -> OAuth:
    """Get the OAuth instance from the request."""
    return request.app.state.oauth


def get_config(request: Request) -> CodebornConfig:
    """Get the application configuration from the request."""
    return request.app.state.config
