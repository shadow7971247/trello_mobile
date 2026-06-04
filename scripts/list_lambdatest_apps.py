"""Список APK/IPA, загруженных в LambdaTest → LAMBDATEST_APP=lt://..."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import env_loader


def main() -> int:
    env_loader.reload_env("lambdatest")
    user = os.getenv("LAMBDATEST_USERNAME") or os.getenv("LT_USERNAME", "")
    key = os.getenv("LAMBDATEST_ACCESS_KEY") or os.getenv("LT_ACCESS_KEY", "")
    if not user or not key:
        print("Задайте LAMBDATEST_USERNAME и LAMBDATEST_ACCESS_KEY в .env.lambdatest")
        return 1

    for app_type in ("android", "ios"):
        response = requests.get(
            "https://manual-api.lambdatest.com/app/data",
            params={"type": app_type, "level": "user"},
            auth=(user, key),
            timeout=60,
        )
        print(f"\n=== {app_type} (HTTP {response.status_code}) ===")
        if response.status_code >= 400:
            print(response.text[:400])
            continue
        payload = response.json()
        apps = payload.get("data") or []
        if not apps:
            print("  (нет загруженных приложений)")
            continue
        for app in apps:
            app_id = app.get("app_id", "")
            lt_url = f"lt://{app_id}" if app_id and not str(app_id).startswith("lt://") else app_id
            print(f"  {app.get('name', '?')}")
            print(f"    LAMBDATEST_APP={lt_url}")
    print(
        "\nИнтеграция Trello в LT (Integrations) — для багов в Trello, "
        "не заменяет LAMBDATEST_APP для Appium."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
