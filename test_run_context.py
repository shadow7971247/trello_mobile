"""Контекст прогона: маркер @pytest.mark.context + активный RUN_MODE."""

from __future__ import annotations

import os
from dataclasses import dataclass

import pytest

from config import MobileConfig, RunTarget

_CONTEXT_ENV_KEYS: dict[str, tuple[str, str]] = {
    "visible_timeout": ("MOBILE_BS_VISIBLE_TIMEOUT", "MOBILE_LOCAL_VISIBLE_TIMEOUT"),
    "reload_pause": ("MOBILE_BS_RELOAD_PAUSE", "MOBILE_LOCAL_RELOAD_PAUSE"),
}


@dataclass(frozen=True)
class MobileRunContext:
    mode: str
    config: MobileConfig
    allowed_modes: tuple[str, ...] | None

    @property
    def run_target(self) -> RunTarget:
        return RunTarget(mode=self.mode)

    @property
    def label(self) -> str:
        return self.run_target.label

    @property
    def is_local(self) -> bool:
        return self.mode == "local"

    @property
    def is_browserstack(self) -> bool:
        return self.mode == "browserstack"

    @property
    def is_cloud(self) -> bool:
        return self.is_browserstack

    @property
    def visible_timeout_sec(self) -> float:
        return self.config.visible_timeout_sec

    @property
    def reload_pause_sec(self) -> float:
        return self.config.reload_pause_sec

    def require_cloud_app(self) -> None:
        if self.is_browserstack and not self.config.browserstack_app:
            pytest.fail(
                "Для BrowserStack задайте BROWSERSTACK_APP=bs://... "
                "(загрузите APK в BS Dashboard)"
            )

    @classmethod
    def resolve(cls, item: pytest.Item, config: MobileConfig) -> MobileRunContext:
        allowed = _allowed_modes_from_item(item)
        active = config.run_mode
        if allowed is not None and active not in allowed:
            hint = " или ".join(f"--run-context {m}" for m in allowed)
            pytest.skip(
                f"Тест рассчитан на context={allowed}, сейчас {active!r}. "
                f"Запуск: pytest {hint}"
            )
        return cls(mode=active, config=config, allowed_modes=allowed)

    @staticmethod
    def peek_env(name: str, context: str) -> str:
        if name not in _CONTEXT_ENV_KEYS:
            raise KeyError(f"Неизвестный ключ контекста: {name!r}")
        cloud_key, local_key = _CONTEXT_ENV_KEYS[name]
        if context == "browserstack":
            key, default = cloud_key, "90"
        else:
            key, default = local_key, "30"
        if name == "reload_pause":
            default = "8" if context == "browserstack" else "3"
        return os.getenv(key, default)


def _allowed_modes_from_item(item: pytest.Item) -> tuple[str, ...] | None:
    marker = item.get_closest_marker("context")
    if marker and marker.args:
        return tuple(str(arg).lower() for arg in marker.args)
    if item.get_closest_marker("local_only") is not None:
        return ("local",)
    if item.get_closest_marker("browserstack_only") is not None:
        return ("browserstack",)
    return None
