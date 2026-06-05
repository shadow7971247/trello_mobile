"""Профили запуска mobile без правки .env (CLI или MOBILE_RUN_CONTEXT)."""

from __future__ import annotations

import os
import sys
from typing import Final

RUN_CONTEXT_NAMES: Final[tuple[str, ...]] = ("local", "browserstack")

_PROFILES: Final[dict[str, dict[str, str]]] = {
    "local": {
        "RUN_MODE": "local",
        "APPIUM_SERVER_URL": "http://127.0.0.1:4723",
        "NO_RESET": "true",
    },
    "browserstack": {
        "RUN_MODE": "browserstack",
        "APPIUM_SERVER_URL": "https://hub-cloud.browserstack.com/wd/hub",
        "DEVICE_NAME": "Samsung Galaxy S22",
        "PLATFORM_VERSION": "12.0",
        "NO_RESET": "false",
    },
}

_active_context: str | None = None


def get_active_run_context() -> str | None:
    return _active_context


def apply_run_context(name: str) -> str:
    global _active_context
    key = name.strip().lower()
    if key not in _PROFILES:
        known = ", ".join(RUN_CONTEXT_NAMES)
        raise ValueError(f"Неизвестный run context {name!r}. Доступны: {known}")
    for env_key, value in _PROFILES[key].items():
        os.environ[env_key] = value
    _active_context = key
    return key


def _parse_cli_context(argv: list[str]) -> str | None:
    for index, arg in enumerate(argv):
        if arg in ("--run-context", "-C") and index + 1 < len(argv):
            return argv[index + 1].strip().lower()
        if arg.startswith("--run-context="):
            return arg.split("=", 1)[1].strip().lower()
    return None


def resolve_and_apply_run_context(argv: list[str] | None = None) -> str | None:
    cli = _parse_cli_context(argv if argv is not None else sys.argv)
    env_ctx = os.getenv("MOBILE_RUN_CONTEXT", "").strip().lower()
    name = cli or env_ctx or None
    if not name:
        return None
    return apply_run_context(name)
