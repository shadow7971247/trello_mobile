"""Загрузка APK в LambdaTest → LAMBDATEST_APP=lt://..."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import env_loader  # noqa: F401


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload APK to LambdaTest")
    parser.add_argument("apk", type=Path, help="Path to trello.apk")
    parser.add_argument("--name", default="TrelloQA", help="Custom app name")
    args = parser.parse_args()

    user = os.getenv("LAMBDATEST_USERNAME") or os.getenv("LT_USERNAME", "")
    key = os.getenv("LAMBDATEST_ACCESS_KEY") or os.getenv("LT_ACCESS_KEY", "")
    if not user or not key:
        print("Задайте LAMBDATEST_USERNAME и LAMBDATEST_ACCESS_KEY в .env.lambdatest")
        return 1
    if not args.apk.is_file():
        print(f"Файл не найден: {args.apk}")
        return 1

    url = "https://manual-api.lambdatest.com/app/upload/realDevice"
    with args.apk.open("rb") as apk_file:
        response = requests.post(
            url,
            auth=(user, key),
            files={"appFile": (args.apk.name, apk_file, "application/vnd.android.package-archive")},
            data={"name": args.name},
            timeout=300,
        )
    print(response.status_code, response.text[:500])
    if response.status_code >= 400:
        return 1
    try:
        payload = response.json()
    except json.JSONDecodeError:
        payload = {"raw": response.text}
    app_id = payload.get("app_id") or payload.get("app_url") or payload.get("data")
    if isinstance(app_id, dict):
        app_id = app_id.get("app_id") or app_id.get("app_url")
    if app_id:
        print(f"\nДобавьте в .env.lambdatest:\nLAMBDATEST_APP={app_id}")
    else:
        print("Ответ:", json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
