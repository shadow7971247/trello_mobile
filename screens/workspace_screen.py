"""Экран списка досок."""

from __future__ import annotations

import time

import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from screens.resilient_wait import Locator, ResilientWait
from mobile_utils.mobile_attach import add_screenshot

_BOARDS_TAB_LOCATORS: tuple[Locator, ...] = (
    (AppiumBy.XPATH, "//*[@text='Boards' or @text='Доски']"),
    (AppiumBy.ACCESSIBILITY_ID, "Boards"),
    (AppiumBy.ACCESSIBILITY_ID, "Доски"),
)

_BOARDS_LIST_LOCATORS: tuple[Locator, ...] = (
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Boards")',
    ),
    (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().textContains("Доски")',
    ),
    (AppiumBy.ACCESSIBILITY_ID, "Boards"),
)

_BOARD_VIEW_TEXTS = (
    "Add list",
    "Добавить список",
    "Add another list",
    "Добавить ещё один список",
)


class WorkspaceScreen:
    def __init__(self, driver, resilient: ResilientWait | None = None) -> None:
        self._driver = driver
        self._rw = resilient or ResilientWait.from_config(driver)

    @staticmethod
    def _capture(driver, step_name: str) -> None:
        add_screenshot(driver, step_name)

    def assert_boards_workspace_visible(self) -> WorkspaceScreen:
        step = "Проверить экран досок (Boards / Доски)"
        with allure.step(step):
            self._ensure_boards_tab()
            self._rw.wait_until(
                self._on_boards_list,
                message="Экран списка досок (Boards / Доски) не загрузился",
            )
            self._capture(self._driver, step)
        return self

    def go_home(self) -> WorkspaceScreen:
        step = "Вернуться на экран досок"
        with allure.step(step):
            try:
                self._driver.activate_app(self._rw._app_package)
            except WebDriverException:
                return self

            def _home_ready() -> bool:
                if self._on_boards_list():
                    return True
                try:
                    self._driver.press_keycode(4)
                except WebDriverException:
                    pass
                self._ensure_boards_tab()
                return self._on_boards_list()

            self._rw.wait_until(
                _home_ready,
                message="Не удалось вернуться на экран досок",
            )
            self._capture(self._driver, step)
        return self

    def _on_boards_list(self) -> bool:
        if self._on_board_view():
            return False
        for locator in _BOARDS_LIST_LOCATORS:
            try:
                if self._driver.find_element(*locator).is_displayed():
                    return True
            except NoSuchElementException:
                continue
        return False

    def _on_board_view(self) -> bool:
        for text in _BOARD_VIEW_TEXTS:
            try:
                self._driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().textContains("{text}")',
                )
                return True
            except NoSuchElementException:
                continue
        return False

    def open_board(
        self, board_name: str, board_url: str | None = None
    ) -> WorkspaceScreen:
        step = f"Открыть доску «{board_name}»"
        with allure.step(step):
            if board_url:
                result = self.open_board_via_url(board_url)
                self._capture(self._driver, step)
                return result
            self.go_home()
            self._refresh_boards_list()
            board = self._find_board(board_name, clickable=True)
            board.click()
            self._wait_board_open(board_name)
            self._capture(self._driver, step)
        return self

    def open_board_via_url(self, board_url: str) -> WorkspaceScreen:
        step = "Открыть доску по ссылке API"
        with allure.step(step):
            self._driver.execute_script(
                "mobile: deepLink",
                {"url": board_url, "package": self._rw._app_package},
            )
            pause = 5 if self._rw._is_cloud else 2
            time.sleep(pause)
            self._wait_board_open()
            self._capture(self._driver, step)
        return self

    def _wait_board_open(self, board_name: str | None = None) -> None:
        fragment = (board_name or "")[:24].replace('"', '\\"')

        def _board_visible() -> bool:
            if self._on_board_view():
                return True
            if not fragment:
                return False
            try:
                self._driver.find_element(
                    AppiumBy.XPATH,
                    f'//*[contains(@text,"{fragment}") or contains(@content-desc,"{fragment}")]',
                )
                return True
            except NoSuchElementException:
                return False

        self._rw.wait_until(
            _board_visible,
            message="Доска не открылась после deep link / навигации",
        )

    def should_have_board(
        self, board_name: str, board_url: str | None = None
    ) -> WorkspaceScreen:
        step = f"Проверить доску «{board_name}»"
        with allure.step(step):
            self.go_home()
            self._refresh_boards_list()
            try:
                self._find_board(board_name)
            except AssertionError:
                if not board_url:
                    raise
                self.open_board_via_url(board_url)
                self._wait_board_open(board_name)
            self._capture(self._driver, step)
        return self

    def _ensure_boards_tab(self) -> None:
        try:
            tab = self._rw.wait_until_any_visible(
                _BOARDS_TAB_LOCATORS,
                message="Вкладка Boards / Доски не найдена",
                clickable=True,
            )
            tab.click()
        except AssertionError:
            for locator in _BOARDS_TAB_LOCATORS:
                try:
                    self._driver.find_element(*locator).click()
                    return
                except (NoSuchElementException, WebDriverException):
                    continue

    def _refresh_boards_list(self) -> None:
        size = self._driver.get_window_size()
        x = size["width"] // 2
        y_top = int(size["height"] * 0.25)
        y_bottom = int(size["height"] * 0.75)
        self._driver.swipe(x, y_top, x, y_bottom, 600)

    def _scroll_down(self) -> None:
        size = self._driver.get_window_size()
        x = size["width"] // 2
        self._driver.swipe(
            x,
            int(size["height"] * 0.75),
            x,
            int(size["height"] * 0.35),
            500,
        )

    def _find_board(self, board_name: str, *, clickable: bool = False):
        fragment = board_name[:24].replace('"', '\\"')
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
                    try:
                        el = self._driver.find_element(*locator)
                        if clickable:
                            if el.is_displayed() and el.is_enabled():
                                return el
                        elif el.is_displayed():
                            return el
                    except NoSuchElementException:
                        continue
                self._scroll_down()
            raise TimeoutError(f"Доска «{board_name}» не найдена")

        return self._rw._run_with_reload(
            _locate,
            message=f"Доска «{board_name}» не найдена на экране досок",
        )
