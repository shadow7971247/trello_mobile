"""BrowserStack CI: smoke без логина Atlassian (полные сценарии — локальный эмулятор)."""

from __future__ import annotations

import time

import allure
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from test_run_context import MobileRunContext

_WELCOME_LOCATORS: tuple[tuple[str, str], ...] = (
    (AppiumBy.XPATH, "//*[@text='Log in' or @text='Войти']"),
    (
        AppiumBy.XPATH,
        "//*[contains(@text,'SIGN IN WITH') or contains(@text,'ВОЙТИ')]",
    ),
    (AppiumBy.ID, "com.trello:id/email"),
)


def _activate_trello(driver, package: str) -> None:
    try:
        driver.activate_app(package)
    except WebDriverException:
        pass
    time.sleep(3)


def _welcome_or_login_visible(driver) -> bool:
    for locator in _WELCOME_LOCATORS:
        try:
            if driver.find_element(*locator).is_displayed():
                return True
        except NoSuchElementException:
            continue
    return False


@allure.feature("Smoke")
@allure.story("BrowserStack")
@pytest.mark.mobile
@pytest.mark.smoke
@pytest.mark.cloud_smoke
@pytest.mark.browserstack_only
@pytest.mark.no_home_reset
def test_trello_package_is_active(run_context: MobileRunContext, driver) -> None:
    """APK Trello в foreground (без логина)."""
    run_context.require_cloud_app()
    with allure.step(f"Цель прогона: {run_context.label}"):
        assert run_context.is_browserstack
    with allure.step("Проверить package com.trello"):
        _activate_trello(driver, run_context.config.app_package)
        package = driver.current_package or ""
        assert package == run_context.config.app_package, (
            f"Ожидали {run_context.config.app_package}, получили {package!r}"
        )


@allure.feature("Smoke")
@allure.story("BrowserStack")
@pytest.mark.mobile
@pytest.mark.smoke
@pytest.mark.cloud_smoke
@pytest.mark.browserstack_only
@pytest.mark.no_home_reset
def test_trello_welcome_screen_visible(run_context: MobileRunContext, driver) -> None:
    """После запуска виден экран входа (Welcome / Log in), без Atlassian OAuth."""
    run_context.require_cloud_app()
    with allure.step("Открыть Trello и проверить Welcome / Log in"):
        _activate_trello(driver, run_context.config.app_package)
        assert _welcome_or_login_visible(driver), (
            "Ожидали экран входа Trello (Log in / SIGN IN WITH EMAIL)"
        )


@allure.feature("Smoke")
@allure.story("BrowserStack")
@pytest.mark.mobile
@pytest.mark.smoke
@pytest.mark.cloud_smoke
@pytest.mark.browserstack_only
@pytest.mark.no_home_reset
def test_trello_reactivate_stays_in_app(run_context: MobileRunContext, driver) -> None:
    """Повторный activate_app не теряет foreground Trello."""
    run_context.require_cloud_app()
    package = run_context.config.app_package
    with allure.step("Дважды activate_app — foreground остаётся Trello"):
        _activate_trello(driver, package)
        _activate_trello(driver, package)
        assert driver.current_package == package, (
            f"Ожидали {package}, получили {driver.current_package!r}"
        )
