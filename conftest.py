"""Pytest-фикстуры mobile: локальный эмулятор и BrowserStack."""

from __future__ import annotations

import time
from collections.abc import Generator

import allure
import env_loader
import pytest
from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.common.exceptions import WebDriverException

from api_bridge import ApiConfig, TrelloApiClient
from capabilities import build_capabilities, remote_hub_url
from config import MobileConfig, RunTarget, get_mobile_config, reset_mobile_config
from run_context import RUN_CONTEXT_NAMES, get_active_run_context, resolve_and_apply_run_context
from screens.login_screen import LoginScreen
from screens.workspace_screen import WorkspaceScreen
from test_run_context import MobileRunContext

from pytest_markers import apply_local_browserstack_markers


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    apply_local_browserstack_markers(items)


resolve_and_apply_run_context()
env_loader.reload_env()
reset_mobile_config()

_CLOUD_SESSION_RETRIES = 3
_CLOUD_RETRY_DELAY_SEC = 20


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-context",
        "-C",
        action="store",
        choices=list(RUN_CONTEXT_NAMES),
        default=None,
        metavar="NAME",
        help=(
            "Профиль без правки .env: "
            + ", ".join(RUN_CONTEXT_NAMES)
            + " (или MOBILE_RUN_CONTEXT)"
        ),
    )


@pytest.fixture(scope="session")
def run_context_name() -> str | None:
    return get_active_run_context()


@pytest.fixture(scope="session")
def mobile_config() -> MobileConfig:
    cfg = get_mobile_config()
    cfg.validate()
    return cfg


@pytest.fixture
def run_context(request: pytest.FixtureRequest, mobile_config: MobileConfig) -> MobileRunContext:
    ctx = MobileRunContext.resolve(request.node, mobile_config)
    allure.dynamic.parameter("run_context", ctx.mode)
    return ctx


@pytest.fixture(scope="session")
def run_target(mobile_config: MobileConfig) -> RunTarget:
    return RunTarget(mode=mobile_config.run_mode)


@pytest.fixture(scope="session")
def api_client(mobile_config: MobileConfig) -> TrelloApiClient:
    api_config = ApiConfig(
        base_url=mobile_config.trello_api_base_url,
        api_key=mobile_config.trello_api_key,
        api_token=mobile_config.trello_api_token,
    )
    api_config.validate()
    return TrelloApiClient(api_config)


def _create_appium_driver(
    mobile_config: MobileConfig, *, session_name: str
) -> webdriver.Remote:
    last_error: Exception | None = None
    retries = _CLOUD_SESSION_RETRIES if mobile_config.is_cloud else 1
    for attempt in range(1, retries + 1):
        options = AppiumOptions()
        options.load_capabilities(
            build_capabilities(mobile_config, session_name=session_name)
        )
        try:
            client = webdriver.Remote(
                remote_hub_url(mobile_config), options=options
            )
            if client.current_package:
                return client
            client.quit()
            last_error = RuntimeError("empty current_package after session start")
        except WebDriverException as exc:
            last_error = exc
            if not mobile_config.is_cloud or "app launch" not in str(exc).lower():
                if attempt == 1:
                    raise
        if attempt < retries:
            time.sleep(_CLOUD_RETRY_DELAY_SEC)
    raise last_error or RuntimeError("failed to start Appium session")


@pytest.fixture(scope="session")
def driver_session(
    mobile_config: MobileConfig,
) -> Generator[webdriver.Remote | None, None, None]:
    if not mobile_config.is_cloud:
        yield None
        return
    client = _create_appium_driver(
        mobile_config, session_name="trello-mobile-cloud-session"
    )
    yield client
    try:
        client.quit()
    except Exception:
        pass


@pytest.fixture
def driver(
    mobile_config: MobileConfig,
    driver_session: webdriver.Remote | None,
) -> Generator[webdriver.Remote, None, None]:
    if mobile_config.is_cloud:
        assert driver_session is not None
        yield driver_session
        return
    client = _create_appium_driver(
        mobile_config, session_name="trello-mobile-local"
    )
    yield client
    try:
        client.quit()
    except Exception:
        pass


@pytest.fixture(scope="session")
def logged_in_session(
    driver_session: webdriver.Remote | None, mobile_config: MobileConfig
) -> None:
    if mobile_config.is_cloud and driver_session is not None:
        LoginScreen(driver_session).login_if_needed(
            mobile_config.email,
            mobile_config.password,
            otp_code=mobile_config.otp_code,
        )


@pytest.fixture
def logged_in(
    driver: webdriver.Remote,
    mobile_config: MobileConfig,
    logged_in_session: None,
) -> None:
    if mobile_config.is_cloud:
        return
    LoginScreen(driver).login_if_needed(
        mobile_config.email,
        mobile_config.password,
        otp_code=mobile_config.otp_code,
    )


@pytest.fixture(autouse=True)
def mobile_reset_home(
    request: pytest.FixtureRequest, driver: webdriver.Remote
) -> None:
    if request.node.get_closest_marker("mobile") is None:
        return
    if request.node.get_closest_marker("no_home_reset") is not None:
        return
    if "logged_in" not in request.fixturenames:
        return
    WorkspaceScreen(driver).go_home()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item) -> Generator[None, None, None]:
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    test_driver = item.funcargs.get("driver")
    if test_driver is None:
        return
    try:
        png = test_driver.get_screenshot_as_png()
        allure.attach(png, name="screenshot", attachment_type=allure.attachment_type.PNG)
    except Exception:
        pass
