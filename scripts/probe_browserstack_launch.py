"""Проверка старта BrowserStack-сессии (без полного теста)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import env_loader
from appium import webdriver
from appium.options.common import AppiumOptions
from capabilities import build_capabilities, remote_hub_url
from config import get_mobile_config, reset_mobile_config
from run_context import apply_run_context

if __name__ == "__main__":
    apply_run_context("browserstack")
    env_loader.reload_env("browserstack")
    reset_mobile_config()
    cfg = get_mobile_config()
    cfg.validate()

    print("Hub: hub-cloud.browserstack.com/wd/hub")
    app = cfg.browserstack_app or ""
    print(f"App: {app[:32] or '(не задан BROWSERSTACK_APP)'}...")
    if not app:
        print("Загрузите APK в BrowserStack App Automate → App ID bs://...")
        sys.exit(1)

    options = AppiumOptions()
    options.load_capabilities(build_capabilities(cfg, session_name="probe-bs"))
    driver = webdriver.Remote(remote_hub_url(cfg), options=options)
    try:
        print(f"Package: {driver.current_package}")
        print("OK: сессия BrowserStack запущена")
    finally:
        driver.quit()
