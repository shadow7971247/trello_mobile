"""Ожидания с одной повторной попыткой после перезагрузки приложения."""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from typing import Any

import allure
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from config import get_mobile_config

Locator = tuple[str, str]


class ResilientWait:
    """waitUntilVisible + одна перезагрузка приложения при таймауте."""

    def __init__(
        self,
        driver: WebDriver,
        *,
        is_cloud: bool,
        app_package: str,
        app_activity: str,
        visible_timeout: float,
        reload_pause_sec: float,
    ) -> None:
        self._driver = driver
        self._is_cloud = is_cloud
        self._app_package = app_package
        self._app_activity = app_activity
        self._visible_timeout = visible_timeout
        self._reload_pause_sec = reload_pause_sec

    @classmethod
    def from_config(cls, driver: WebDriver) -> ResilientWait:
        cfg = get_mobile_config()
        return cls(
            driver,
            is_cloud=cfg.is_cloud,
            app_package=cfg.app_package,
            app_activity=cfg.app_activity,
            visible_timeout=cfg.visible_timeout_sec,
            reload_pause_sec=cfg.reload_pause_sec,
        )

    def reload_app(self) -> None:
        """Перезапуск Trello: terminate + HomeActivity."""
        with allure.step("Перезагрузить приложение Trello"):
            try:
                self._driver.terminate_app(self._app_package)
            except WebDriverException:
                pass
            time.sleep(2 if self._is_cloud else 1)
            try:
                self._driver.activate_app(self._app_package)
            except WebDriverException:
                pass
            self._launch_home_activity()
            time.sleep(self._reload_pause_sec)

    def _launch_home_activity(self) -> None:
        if hasattr(self._driver, "start_activity"):
            try:
                self._driver.start_activity(self._app_package, self._app_activity)
                return
            except WebDriverException:
                pass
        try:
            self._driver.execute_script(
                "mobile: startActivity",
                {
                    "component": f"{self._app_package}/{self._app_activity}",
                    "stop": True,
                },
            )
        except WebDriverException:
            pass

    def wait_until_visible(
        self,
        locator: Locator,
        *,
        message: str,
        clickable: bool = False,
    ) -> Any:
        return self._run_with_reload(
            lambda: self._wait_once(locator, clickable=clickable),
            message=message,
        )

    def wait_until_any_visible(
        self,
        locators: Sequence[Locator],
        *,
        message: str,
        clickable: bool = False,
    ) -> Any:
        def _attempt() -> Any:
            last_error: Exception | None = None
            for locator in locators:
                try:
                    return self._wait_once(locator, clickable=clickable)
                except TimeoutException as exc:
                    last_error = exc
            raise TimeoutException(message) from last_error

        return self._run_with_reload(_attempt, message=message)

    def wait_until(
        self,
        predicate: Callable[[], bool],
        *,
        message: str,
    ) -> None:
        def _attempt() -> None:
            deadline = time.time() + self._visible_timeout
            while time.time() < deadline:
                try:
                    if predicate():
                        return
                except WebDriverException:
                    pass
                time.sleep(1.5 if self._is_cloud else 0.8)
            raise TimeoutException(message)

        self._run_with_reload(_attempt, message=message)

    def _wait_once(self, locator: Locator, *, clickable: bool) -> Any:
        condition = (
            ec.element_to_be_clickable(locator)
            if clickable
            else ec.visibility_of_element_located(locator)
        )
        return WebDriverWait(self._driver, self._visible_timeout).until(condition)

    def _run_with_reload(
        self,
        attempt: Callable[[], Any],
        *,
        message: str,
    ) -> Any:
        try:
            return attempt()
        except (TimeoutException, AssertionError, TimeoutError) as first_error:
            retry_label = (
                "повтор ожидания (BrowserStack)"
                if self._is_cloud
                else "повтор после перезагрузки"
            )
            with allure.step(f"{message}: {retry_label}"):
                allure.attach(
                    str(first_error),
                    name="first_attempt_error",
                    attachment_type=allure.attachment_type.TEXT,
                )
                if self._is_cloud:
                    time.sleep(self._reload_pause_sec)
                else:
                    self.reload_app()
                try:
                    return attempt()
                except (TimeoutException, AssertionError, TimeoutError) as second_error:
                    suffix = (
                        " (повтор на BrowserStack)"
                        if self._is_cloud
                        else " (после перезагрузки приложения)"
                    )
                    raise AssertionError(f"{message}{suffix}: {second_error}") from second_error
