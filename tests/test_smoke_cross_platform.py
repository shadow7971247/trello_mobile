"""Smoke на локальном эмуляторе (логин + API-bridge). BrowserStack — test_smoke_browserstack.py."""

from __future__ import annotations

import allure
import pytest

from api_bridge import TrelloApiClient, board_name, prepare_public_board
from screens.workspace_screen import WorkspaceScreen
from test_run_context import MobileRunContext


@allure.feature("Smoke")
@allure.story("Workspace")
@pytest.mark.mobile
@pytest.mark.smoke
@pytest.mark.local_only
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
