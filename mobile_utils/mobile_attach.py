"""Allure-вложения для mobile-отчёта (скриншоты, XML, видео BrowserStack)."""

from __future__ import annotations

import allure
import requests
from selenium.webdriver.remote.webdriver import WebDriver


def add_screenshot(driver: WebDriver | None, name: str) -> None:
    if driver is None:
        return
    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass


def add_xml(driver: WebDriver | None, name: str = "UI hierarchy") -> None:
    if driver is None:
        return
    try:
        allure.attach(
            driver.page_source,
            name=name,
            attachment_type=allure.attachment_type.XML,
        )
    except Exception:
        pass


def add_browserstack_video(
    session_id: str | None,
    username: str,
    access_key: str,
    *,
    name: str = "BrowserStack video",
) -> None:
    if not session_id or not username or not access_key:
        return

    video_url: str | None = None
    for url in (
        f"https://api-cloud.browserstack.com/app-automate/sessions/{session_id}.json",
        f"https://api.browserstack.com/app-automate/sessions/{session_id}.json",
    ):
        try:
            response = requests.get(url, auth=(username, access_key), timeout=30)
            response.raise_for_status()
            data = response.json()
            session = data.get("automation_session") or data.get("session") or data
            video_url = session.get("video_url") if isinstance(session, dict) else None
            if video_url:
                break
        except Exception:
            continue

    if not video_url:
        return

    allure.attach(
        (
            "<html><body>"
            '<video width="100%" height="100%" controls autoplay>'
            f'<source src="{video_url}" type="video/mp4">'
            "</video>"
            "</body></html>"
        ),
        name=name,
        attachment_type=allure.attachment_type.HTML,
    )
