"""Shared test setup: read DSNs from environment variables (CI) or .streamlit/secrets.toml (local)."""

import os
import tomllib
from pathlib import Path

import pytest

SECRETS_FILE = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"


def _secret(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    if SECRETS_FILE.exists():
        value = tomllib.loads(SECRETS_FILE.read_text()).get(name)
        if value:
            return value
    pytest.fail(f"{name} is not set (environment variable or .streamlit/secrets.toml)")


@pytest.fixture(scope="session")
def runner_dsn() -> str:
    return _secret("RUNNER_DSN")


@pytest.fixture(scope="session")
def app_dsn() -> str:
    return _secret("APP_DSN")
