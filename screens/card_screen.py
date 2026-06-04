"""Экран карточки."""

from __future__ import annotations

import time

import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class CardScreen:
    def __init__(self, driver, timeout: float = 20) -> None:
        self._driver = driver
        self._wait = WebDriverWait(driver, timeout)

    def rename(self, new_name: str) -> CardScreen:
        with allure.step(f"Переименовать карточку в «{new_name}»"):
            self._tap_title_to_edit()
            field = self._wait.until(
                ec.presence_of_element_located(
                    (AppiumBy.CLASS_NAME, "android.widget.EditText")
                )
            )
            try:
                field.clear()
            except Exception:
                pass
            field.send_keys(new_name)
            try:
                self._driver.hide_keyboard()
            except Exception:
                pass
            time.sleep(2)
        return self

    def _tap_title_to_edit(self) -> None:
        for locator in (
            (AppiumBy.CLASS_NAME, "android.widget.EditText"),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().className("android.widget.EditText")',
            ),
            (
                AppiumBy.XPATH,
                "//android.widget.TextView[string-length(@text) > 0]",
            ),
        ):
            try:
                el = self._driver.find_element(*locator)
                el.click()
                return
            except NoSuchElementException:
                continue

    def delete(self) -> CardScreen:
        with allure.step("Удалить карточку"):
            for locator in (
                (AppiumBy.ACCESSIBILITY_ID, "More options"),
                (
                    AppiumBy.XPATH,
                    "//*[@content-desc='More options' or @content-desc='Ещё' "
                    "or @content-desc='More actions']",
                ),
                (
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().descriptionContains("More")',
                ),
            ):
                try:
                    self._driver.find_element(*locator).click()
                    break
                except NoSuchElementException:
                    continue
            else:
                raise TimeoutError("Кнопка меню карточки не найдена")

            delete_btn = self._wait.until(
                ec.element_to_be_clickable(
                    (
                        AppiumBy.XPATH,
                        "//*[@text='Delete' or @text='Удалить' "
                        "or contains(@text,'Delete') or contains(@text,'Удал')]",
                    )
                )
            )
            delete_btn.click()

            confirm = self._wait.until(
                ec.element_to_be_clickable(
                    (
                        AppiumBy.XPATH,
                        "//*[(contains(@text,'Delete') or contains(@text,'Удал')) "
                        "and @clickable='true']",
                    )
                )
            )
            confirm.click()
            time.sleep(1)
        return self

    def close(self) -> CardScreen:
        with allure.step("Закрыть карточку"):
            self._driver.back()
        return self
