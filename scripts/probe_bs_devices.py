"""Подбор устройства BrowserStack: старт сессии без полного pytest."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import env_loader
from appium import webdriver
from appium.options.common import AppiumOptions
from capabilities import build_capabilities, remote_hub_url
from config import get_mobile_config, reset_mobile_config

# Кандидаты: новее Android 12, часто стабильные на BS App Automate
DEVICE_MATRIX: list[tuple[str, str, bool]] = [
    ("Google Pixel 8", "14.0", False),
    ("Samsung Galaxy S24", "14.0", False),
    ("Google Pixel 7", "13.0", False),
    ("Samsung Galaxy S23", "13.0", False),
    ("OnePlus 9", "11.0", True),
    ("Samsung Galaxy S22", "12.0", False),
    ("Google Pixel 6", "12.0", False),
]


def try_device(device: str, version: str, no_reset: bool) -> str:
    os.environ["DEVICE_NAME"] = device
    os.environ["PLATFORM_VERSION"] = version
    os.environ["NO_RESET"] = "true" if no_reset else "false"
    reset_mobile_config()
    cfg = get_mobile_config()
    options = AppiumOptions()
    options.load_capabilities(build_capabilities(cfg, session_name="probe-device"))
    driver = webdriver.Remote(remote_hub_url(cfg), options=options)
    try:
        pkg = driver.current_package or ""
        return f"OK package={pkg!r}"
    finally:
        driver.quit()


if __name__ == "__main__":
    os.environ.setdefault("RUN_MODE", "browserstack")
    os.environ.setdefault("TRELLO_EMAIL", "probe@example.com")
    os.environ.setdefault("TRELLO_PASSWORD", "probe")
    env_loader.reload_env("browserstack")
    reset_mobile_config()
    cfg = get_mobile_config()
    if not cfg.browserstack_username or not cfg.browserstack_access_key:
        print("Задайте BROWSERSTACK_USERNAME и BROWSERSTACK_ACCESS_KEY в .env.browserstack")
        sys.exit(1)
    if not cfg.browserstack_app:
        print("Задайте BROWSERSTACK_APP=bs://...")
        sys.exit(1)

    print(f"App: {cfg.browserstack_app}")
    print(f"Hub user: {cfg.browserstack_username}")
    print("---")

    for device, version, no_reset in DEVICE_MATRIX:
        label = f"{device} / Android {version} / NO_RESET={no_reset}"
        print(f"Trying {label} ...", flush=True)
        try:
            result = try_device(device, version, no_reset)
            print(f"  {result}")
            if "com.trello" in result:
                print(f"\nWINNER: {label}")
                sys.exit(0)
        except Exception as exc:
            msg = str(exc).split("\n")[0][:200]
            print(f"  FAIL: {msg}")

    print("\nNo device launched com.trello — проверьте APK (перезалить в BS) или app id.")
    sys.exit(1)
