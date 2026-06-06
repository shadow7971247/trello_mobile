"""Экран входа Trello Mobile."""

from __future__ import annotations

import time

import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from screens.resilient_wait import ResilientWait
from mobile_utils.mobile_attach import add_screenshot, add_xml


class LoginScreen:
    NATIVE = "NATIVE_APP"

    def __init__(
        self, driver, timeout: float = 60, resilient: ResilientWait | None = None
    ) -> None:
        self._driver = driver
        self._wait = WebDriverWait(driver, timeout)
        self._rw = resilient or ResilientWait.from_config(driver)

    def login_if_needed(
        self, email: str, password: str, *, otp_code: str = ""
    ) -> LoginScreen:
        with allure.step("Войти в приложение при необходимости"):
            time.sleep(3)
            self._return_to_trello_app()
            if self._is_logged_in():
                self._rw.wait_until(
                    self._is_logged_in,
                    message="Главный экран Trello не загрузился",
                )
                add_screenshot(self._driver, "Уже авторизован")
                return self
            if not self._webview_has_login_form():
                self._open_email_login()
            if self._is_logged_in():
                return self
            if self._webview_has_login_form():
                self._login_via_webview(email, password, otp_code=otp_code)
            elif not self._is_logged_in():
                raise RuntimeError(
                    "Не удалось войти в Trello: нет экрана логина и нет главного экрана."
                )
            self._rw.wait_until(
                self._is_logged_in,
                message="После входа главный экран Trello не загрузился",
            )
            self._return_to_trello_app()
            add_screenshot(self._driver, "Вход в приложение")
        return self

    def _return_to_trello_app(self) -> None:
        """После WebView/Chrome (Atlassian login) вернуть foreground Trello."""
        app_package = "com.trello"
        current = self._driver.current_package or ""
        if current == app_package and self._is_logged_in():
            return
        with allure.step("Активировать приложение Trello"):
            self._to_native()
            try:
                self._driver.activate_app(app_package)
            except WebDriverException:
                pass
            time.sleep(3)
            add_screenshot(self._driver, "activate_app Trello")

    def _is_logged_in(self) -> bool:
        self._to_native()
        if self._on_sign_in_screen():
            return False
        locators = (
            (AppiumBy.ACCESSIBILITY_ID, "Boards"),
            (AppiumBy.ACCESSIBILITY_ID, "Доски"),
            (
                AppiumBy.XPATH,
                "//*[contains(@text,'Boards') or contains(@text,'Доски')]",
            ),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().textContains("My boards")',
            ),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().textContains("Мои доски")',
            ),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().descriptionContains("Home")',
            ),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().textContains("Home")',
            ),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().textContains("Inbox")',
            ),
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().textContains("Create")',
            ),
        )
        for locator in locators:
            try:
                if self._driver.find_element(*locator).is_displayed():
                    return True
            except Exception:
                continue
        return False

    def _on_sign_in_screen(self) -> bool:
        markers = (
            (AppiumBy.ID, "com.trello:id/email"),
            (
                AppiumBy.XPATH,
                "//*[contains(@text,'SIGN IN WITH') or contains(@text,'ВОЙТИ')]",
            ),
            (
                AppiumBy.XPATH,
                "//*[@text='Log in' or @text='Войти']",
            ),
        )
        for locator in markers:
            try:
                el = self._driver.find_element(*locator)
                if el.is_displayed():
                    return True
            except Exception:
                continue
        return False

    def _open_email_login(self) -> None:
        """Welcome → Log in → bottom sheet → SIGN IN WITH EMAIL."""
        self._to_native()
        self._tap_if_found(
            (
                (AppiumBy.XPATH, "//*[@text='Log in' or @text='Войти']"),
                (
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().textContains("Log in")',
                ),
            ),
            timeout=10,
        )
        self._tap_if_found(
            (
                (AppiumBy.ID, "com.trello:id/email"),
                (
                    AppiumBy.XPATH,
                    "//*[@text='SIGN IN WITH EMAIL' or @text='ВОЙТИ С ПОМОЩЬЮ EMAIL' "
                    "or contains(@text,'EMAIL')]",
                ),
            ),
            timeout=8,
            required=False,
        )

    def _tap_if_found(
        self,
        locators: tuple[tuple[str, str], ...],
        *,
        timeout: float = 10,
        required: bool = False,
    ) -> None:
        for locator in locators:
            try:
                el = WebDriverWait(self._driver, timeout).until(
                    ec.element_to_be_clickable(locator)
                )
                el.click()
                return
            except TimeoutException:
                continue
        if required:
            raise TimeoutException(f"element not found: {locators[0]}")

    def _webview_has_login_form(self) -> bool:
        try:
            if not any("WEBVIEW" in ctx for ctx in self._driver.contexts):
                return False
            self._switch_to_webview()
            self._driver.find_element(
                AppiumBy.CSS_SELECTOR,
                'input[data-testid="username"], input#username, input[type="email"]',
            )
            return True
        except Exception:
            self._to_native()
            return False

    def _to_native(self) -> None:
        try:
            self._driver.switch_to.context(self.NATIVE)
        except Exception:
            pass

    def _switch_to_webview(self) -> None:
        def webview_available(driver) -> bool:
            return any("WEBVIEW" in ctx for ctx in driver.contexts)

        self._wait.until(webview_available)
        for ctx in self._driver.contexts:
            if "WEBVIEW" in ctx:
                self._driver.switch_to.context(ctx)
                return
        raise TimeoutException("WEBVIEW context not found")

    def _login_via_webview(
        self, email: str, password: str, *, otp_code: str = ""
    ) -> None:
        try:
            self._switch_to_webview()
            email_input = self._wait.until(
                ec.presence_of_element_located(
                    (
                        AppiumBy.CSS_SELECTOR,
                        'input[data-testid="username"], input#username, '
                        'input[name="username"], input[type="email"]',
                    )
                )
            )
            self._fill_input(email_input, email)

            continue_btn = self._wait.until(
                ec.element_to_be_clickable(
                    (
                        AppiumBy.CSS_SELECTOR,
                        'button[data-testid="login-submit"], '
                        'button#login-submit, input[type="submit"]',
                    )
                )
            )
            continue_btn.click()

            password_input = self._wait.until(
                ec.presence_of_element_located(
                    (
                        AppiumBy.CSS_SELECTOR,
                        'input[data-testid="password"], input#password, '
                        'input[name="password"], input[type="password"]',
                    )
                )
            )
            self._fill_input(password_input, password)
            self._check_remember_device()

            submit = self._wait.until(
                ec.element_to_be_clickable(
                    (
                        AppiumBy.CSS_SELECTOR,
                        'button[data-testid="login-submit"], '
                        'button#login-submit, input[type="submit"]',
                    )
                )
            )
            submit.click()

            self._to_native()
            self._handle_step_up_verification(otp_code)
            self._return_to_trello_app()
            self._wait.until(
                lambda _: self._is_logged_in(),
                message="boards screen after login",
            )
        except Exception:
            self._attach_debug()
            raise

    def _check_remember_device(self) -> None:
        for selector in (
            'input[data-testid="remember-me"]',
            'input#remember-me',
            'input[name="rememberMe"]',
        ):
            try:
                box = self._driver.find_element(AppiumBy.CSS_SELECTOR, selector)
                if not box.is_selected():
                    box.click()
            except Exception:
                continue

    def _handle_step_up_verification(self, otp_code: str) -> None:
        """Проверка входа с нового устройства (код на email) — не то же самое, что 2FA."""
        if not self._otp_screen_visible():
            return
        code = otp_code.strip()
        if not code:
            raise RuntimeError(
                "Atlassian запросил одноразовый код на email (вход с нового устройства, "
                "часто в облаке BrowserStack). Задайте TRELLO_OTP в trello_ui/.env "
                "или один раз войдите вручную на устройстве с NO_RESET=true."
            )
        with allure.step("Ввести код подтверждения из email"):
            self._submit_otp(code)

    def _otp_screen_visible(self) -> bool:
        try:
            source = self._driver.page_source.lower()
        except Exception:
            return False
        return any(
            m in source
            for m in ("emailed you a code", "отправили код", "otp-submit")
        )

    def _submit_otp(self, code: str) -> None:
        digits = [c for c in code if c.isdigit()]
        if len(digits) < 6:
            raise ValueError("TRELLO_OTP должен содержать 6 цифр из письма Atlassian")
        digits = digits[:6]

        self._to_native()
        fields = [
            el
            for el in self._driver.find_elements(
                AppiumBy.CLASS_NAME, "android.widget.EditText"
            )
            if el.is_displayed()
        ]
        if len(fields) >= 6:
            for field, digit in zip(fields[:6], digits, strict=True):
                field.click()
                field.send_keys(digit)
            self._driver.find_element(AppiumBy.ID, "otp-submit").click()
            return

        self._switch_to_webview()
        otp_input = self._wait.until(
            ec.presence_of_element_located(
                (
                    AppiumBy.CSS_SELECTOR,
                    "#otp-input, input[name='otp'], input[data-testid='otp']",
                )
            )
        )
        self._fill_input(otp_input, "".join(digits))
        self._driver.find_element(
            AppiumBy.CSS_SELECTOR, "#otp-submit, button#otp-submit"
        ).click()
        self._to_native()

    def _fill_input(self, element, value: str) -> None:
        try:
            element.click()
        except Exception:
            pass
        try:
            element.clear()
        except Exception:
            self._driver.execute_script(
                "arguments[0].value = '';", element
            )
        element.send_keys(value)

    def _attach_debug(self) -> None:
        add_xml(self._driver, "login_page_source")
        try:
            allure.attach(
                ", ".join(self._driver.contexts),
                name="contexts",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:
            pass
        add_screenshot(self._driver, "Экран входа — ошибка")
