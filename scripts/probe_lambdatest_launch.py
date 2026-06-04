"""Проверка старта LambdaTest-сессии (без полного теста)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import env_loader
from appium import webdriver
from appium.options.common import AppiumOptions

from capabilities import build_capabilities, remote_hub_url
from config import get_mobile_config, reset_mobile_config
from run_context import apply_run_context

# Virtual emulators (free tier); real devices — LAMBDATEST_IS_REAL_MOBILE=true
CANDIDATES: list[tuple[str, str]] = [
    ("Galaxy A33 5G", "13"),
    ("Galaxy Tab S4", "10"),
    ("Pixel 7", "13"),
]


def try_session(
    device: str, platform_version: str, *, no_reset: bool | None = None
) -> tuple[bool, str]:
    base = get_mobile_config()
    cfg = base.model_copy(
        update={
            "platform_version": platform_version,
            "device_name": device,
            "no_reset": base.no_reset if no_reset is None else no_reset,
        }
    )
    options = AppiumOptions()
    options.load_capabilities(build_capabilities(cfg, session_name="probe-lt"))
    driver = None
    try:
        driver = webdriver.Remote(remote_hub_url(cfg), options=options)
        pkg = driver.current_package
        if not pkg:
            return False, "empty current_package"
        return True, f"session started, package={pkg}"
    except Exception as exc:
        return False, str(exc).split("\n")[0][:240]
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass


def main() -> int:
    apply_run_context("lambdatest")
    env_loader.reload_env("lambdatest")
    reset_mobile_config()
    cfg0 = get_mobile_config()
    print("Hub: mobile-hub.lambdatest.com/wd/hub")
    app = cfg0.lambdatest_app or ""
    print(f"App: {app[:24] or '(не задан LAMBDATEST_APP)'}...")
    print(f"isRealMobile: {cfg0.lambdatest_is_real_mobile}")
    if not app:
        print("Загрузите APK: scripts/upload_lambdatest_app.py path\\to\\trello.apk")
        return 1
    print("-" * 60)
    only = os.getenv("PROBE_DEVICE"), os.getenv("PROBE_OS")
    pairs = [(only[0], only[1])] if only[0] and only[1] else CANDIDATES
    for device, os_ver in pairs:
        for attempt, nr in enumerate((True, False), start=1):
            print(f"Trying {device} / Android {os_ver} (noReset={nr}, try {attempt}) ...", flush=True)
            ok, detail = try_session(device, os_ver, no_reset=nr)
            print(f"  [{'OK' if ok else 'FAIL'}] {detail}")
            if ok:
                print(
                    f"\n>>> WORKING: DEVICE_NAME={device!r} "
                    f"PLATFORM_VERSION={os_ver!r} NO_RESET={str(nr).lower()}"
                )
                return 0
    print("\nNo working device/OS in this batch.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
