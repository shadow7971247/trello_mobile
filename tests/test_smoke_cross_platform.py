"""Smoke: тест объявляет @pytest.mark.context; run_context подтягивает срез .env."""

from __future__ import annotations

import allure
import pytest

from api_bridge import TrelloApiClient, board_name, prepare_public_board
from screens.workspace_screen import WorkspaceScreen
from test_run_context import MobileRunContext


@allure.feature("Smoke")
@allure.story("Запуск приложения")
@pytest.mark.mobile
@pytest.mark.smoke
@pytest.mark.cloud_smoke
@pytest.mark.browserstack
@pytest.mark.no_home_reset
@pytest.mark.context("local", "browserstack")
def test_trello_package_is_active(run_context: MobileRunContext, driver) -> None:
    """Приложение Trello в foreground (без логина)."""
    with allure.step(f"Цель прогона: {run_context.label}"):
        assert run_context.mode in ("local", "browserstack")
    with allure.step("Проверить package com.trello"):
        package = driver.current_package or ""
        assert package == run_context.config.app_package, (
            f"Ожидали {run_context.config.app_package}, получили {package!r}"
        )


@allure.feature("Smoke")
@allure.story("Workspace")
@pytest.mark.mobile
@pytest.mark.smoke
@pytest.mark.cloud_smoke
@pytest.mark.browserstack
@pytest.mark.context("local", "browserstack")
def test_boards_tab_visible_when_logged_in(
    run_context: MobileRunContext,
    logged_in: None,
    driver,
) -> None:
    """После входа виден экран досок (RU/EN)."""
    with allure.step(
        f"Цель прогона: {run_context.label} (timeout {run_context.visible_timeout_sec}s)"
    ):
        allure.attach(
            run_context.label,
            name="run_context",
            attachment_type=allure.attachment_type.TEXT,
        )
    WorkspaceScreen(driver).assert_boards_workspace_visible()


@allure.feature("Smoke")
@allure.story("Deep link доски")
@pytest.mark.mobile
@pytest.mark.smoke
@pytest.mark.local_only
def test_api_board_opens_via_deep_link(
    run_context: MobileRunContext,
    logged_in: None,
    driver,
    api_client: TrelloApiClient,
) -> None:
    """API создаёт доску — mobile открывает по deep link."""
    name = board_name("Smoke Board")
    board = prepare_public_board(api_client, name=name)

    try:
        with allure.step(f"Открыть доску через deep link ({run_context.label})"):
            WorkspaceScreen(driver).open_board_via_url(board.url)
        with allure.step("API: доска существует"):
            fetched = api_client.get_board(board.id)
            assert fetched.name == name
    finally:
        api_client.delete_board(board.id)
