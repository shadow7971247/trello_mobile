"""Экран доски."""

from __future__ import annotations

import time

import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

from screens.resilient_wait import Locator, ResilientWait

_BOARD_LOADED_LOCATORS: tuple[Locator, ...] = (
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Add list")',
    ),
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Добавить список")',
    ),
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Add another list")',
    ),
)


class BoardScreen:
    def __init__(self, driver, resilient: ResilientWait | None = None) -> None:
        self._driver = driver
        self._rw = resilient or ResilientWait.from_config(driver)

    @staticmethod
    def _search_fragment(text: str, *, max_len: int = 24) -> str:
        return (text or "").strip()[:max_len].replace('"', '\\"')

    def _wait_board_loaded(self) -> None:
        self._rw.wait_until_any_visible(
            _BOARD_LOADED_LOCATORS,
            message="Экран доски не загрузился (нет списков)",
        )

    def _scroll_board(self) -> None:
        size = self._driver.get_window_size()
        x = size["width"] // 2
        self._driver.swipe(
            x,
            int(size["height"] * 0.75),
            x,
            int(size["height"] * 0.35),
            500,
        )

    def refresh_board(self) -> BoardScreen:
        with allure.step("Обновить доску (pull-to-refresh)"):
            size = self._driver.get_window_size()
            x = size["width"] // 2
            self._driver.swipe(
                x,
                int(size["height"] * 0.30),
                x,
                int(size["height"] * 0.80),
                700,
            )
            time.sleep(2 if self._rw._is_cloud else 1)
        return self

    def _find_card_element(self, card_name: str):
        fragment = self._search_fragment(card_name)
        locators: tuple[Locator, ...] = (
            (
                AppiumBy.XPATH,
                f'//*[contains(@text,"{fragment}") or contains(@content-desc,"{fragment}")]',
            ),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().textContains("{fragment}")',
            ),
        )

        def _locate():
            for _ in range(8):
                for locator in locators:
                    for el in self._driver.find_elements(*locator):
                        if el.is_displayed():
                            return el
                self._scroll_board()
            raise TimeoutError(f"Карточка «{card_name}» не найдена")

        return self._rw._run_with_reload(
            _locate,
            message=f"Карточка «{card_name}» не найдена на доске",
        )

    def should_have_card(self, card_name: str) -> BoardScreen:
        with allure.step(f"Проверить карточку «{card_name}»"):
            self._wait_board_loaded()
            self._find_card_element(card_name)
        return self

    def should_not_have_card(
        self, card_name: str, board_url: str | None = None
    ) -> BoardScreen:
        with allure.step(f"Проверить отсутствие карточки «{card_name}»"):
            if board_url:
                self._driver.execute_script(
                    "mobile: deepLink",
                    {"url": board_url, "package": self._rw._app_package},
                )
                pause = 4 if self._rw._is_cloud else 2
                time.sleep(pause)
            self._wait_board_loaded()
            fragment = self._search_fragment(card_name)

            def _absent() -> bool:
                elements = self._driver.find_elements(
                    AppiumBy.XPATH,
                    f'//*[contains(@text,"{fragment}") or contains(@content-desc,"{fragment}")]',
                )
                return not any(el.is_displayed() for el in elements)

            for _ in range(5):
                if _absent():
                    return self
                self.refresh_board()

            self._rw.wait_until(
                _absent,
                message=f"Карточка «{card_name}» всё ещё на доске",
            )
        return self

    def open_card(self, card_name: str, card_url: str | None = None) -> BoardScreen:
        with allure.step(f"Открыть карточку «{card_name}»"):
            if card_url:
                self._driver.execute_script(
                    "mobile: deepLink",
                    {"url": card_url, "package": self._rw._app_package},
                )
                time.sleep(4 if self._rw._is_cloud else 2)
                return self
            card = self._find_card_element(card_name)
            card.click()
            time.sleep(1)
        return self

    def add_card_to_first_list(self, card_name: str) -> BoardScreen:
        with allure.step(f"Создать карточку «{card_name}» в первом списке"):
            add_card = self._rw.wait_until_visible(
                (AppiumBy.ACCESSIBILITY_ID, "Add a card"),
                message="Кнопка Add a card не найдена",
                clickable=True,
            )
            add_card.click()
            title_input = self._rw.wait_until_visible(
                (AppiumBy.CLASS_NAME, "android.widget.EditText"),
                message="Поле названия карточки не найдено",
            )
            title_input.send_keys(card_name)
            self._rw.wait_until_visible(
                (AppiumBy.XPATH, "//*[@text='Add' or @content-desc='Add']"),
                message="Кнопка Add не найдена",
                clickable=True,
            ).click()
        return self

    def go_back_to_boards(self) -> BoardScreen:
        with allure.step("Вернуться к списку досок"):
            self._driver.back()
            self._driver.back()
        return self
