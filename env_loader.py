"""Загрузка .env: trello_ui (учётка) + профиль .env.local / .env.browserstack."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent
_SHARED_UI_ENV = _PROJECT_ROOT.parent / "trello_ui" / ".env"
_LEGACY_ENV = _PROJECT_ROOT / ".env"


def reload_env(run_mode: str | None = None) -> str:
    """
    trello_ui/.env → .env.{local|browserstack}; для local ещё .env (legacy).
    Возвращает активный режим.
    """
    load_dotenv(_SHARED_UI_ENV)
    mode = (run_mode or os.getenv("RUN_MODE") or "local").strip().lower()
    profile = _PROJECT_ROOT / f".env.{mode}"
    if profile.is_file():
        load_dotenv(profile, override=True)
    if mode == "local" and _LEGACY_ENV.is_file():
        load_dotenv(_LEGACY_ENV, override=True)
    os.environ["RUN_MODE"] = mode
    return mode


reload_env()
