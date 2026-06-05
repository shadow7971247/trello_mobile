"""Проверка launch: activity + доп. bstack:options."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import env_loader
from appium import webdriver
from appium.options.common import AppiumOptions
from config import get_mobile_config, reset_mobile_config

VARIANTS: list[tuple[str, dict[str, object]]] = [
    (
        "Pixel 8 / 14 + default caps",
        {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": "Google Pixel 8",
            "appium:platformVersion": "14.0",
            "appium:autoGrantPermissions": True,
            "appium:newCommandTimeout": 300,
        },
    ),
    (
        "Pixel 8 / 14 + explicit package/activity (home)",
        {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": "Google Pixel 8",
            "appium:platformVersion": "14.0",
            "appium:appPackage": "com.trello",
            "appium:appActivity": "com.trello.home.HomeActivity",
            "appium:autoGrantPermissions": True,
            "appium:newCommandTimeout": 300,
        },
    ),
    (
        "Pixel 8 / 14 + explicit package/activity (app.activity)",
        {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": "Google Pixel 8",
            "appium:platformVersion": "14.0",
            "appium:appPackage": "com.trello",
            "appium:appActivity": "com.trello.app.activity.HomeActivity",
            "appium:autoGrantPermissions": True,
            "appium:newCommandTimeout": 300,
        },
    ),
]


def hub_url(user: str, key: str) -> str:
    from urllib.parse import quote

    return (
        f"https://{quote(user, safe='')}:{quote(key, safe='')}"
        "@hub-cloud.browserstack.com/wd/hub"
    )


if __name__ == "__main__":
    os.environ.setdefault("RUN_MODE", "browserstack")
    env_loader.reload_env("browserstack")
    reset_mobile_config()
    cfg = get_mobile_config()
    app = cfg.browserstack_app
    if not cfg.browserstack_username or not cfg.browserstack_access_key or not app:
        print("Нужны BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY, BROWSERSTACK_APP")
        sys.exit(1)

    print(f"App: {app} (version from BS upload: 2026.10.2.x)")
    for label, caps in VARIANTS:
        full = {
            **caps,
            "appium:app": app,
            "appium:noReset": False,
            "bstack:options": {
                "userName": cfg.browserstack_username,
                "accessKey": cfg.browserstack_access_key,
                "projectName": "Trello Probe",
                "buildName": "launch-variants",
                "sessionName": label[:40],
                "appiumVersion": "2.0.1",
                "deviceLogs": True,
                "networkLogs": True,
            },
        }
        print(f"\n--- {label} ---", flush=True)
        options = AppiumOptions()
        options.load_capabilities(full)
        try:
            driver = webdriver.Remote(hub_url(cfg.browserstack_username, cfg.browserstack_access_key), options=options)
            try:
                print(f"OK package={driver.current_package!r}")
                if driver.current_package == "com.trello":
                    sys.exit(0)
            finally:
                driver.quit()
        except Exception as exc:
            print(f"FAIL: {str(exc).split(chr(10))[0][:220]}")

    print("\nВсе варианты упали — вероятно APK 2026.10.x не стартует на BS (нужен older APK).")
    sys.exit(1)
