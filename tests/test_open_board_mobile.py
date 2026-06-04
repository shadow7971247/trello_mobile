"""API создаёт доску — mobile открывает и проверяет."""

from __future__ import annotations

import allure
import pytest

from api_bridge import TrelloApiClient, board_name, prepare_board
from screens.board_screen import BoardScreen
from screens.workspace_screen import WorkspaceScreen


@allure.feature("Доски")
@allure.story("Открытие доски")
@pytest.mark.mobile
@pytest.mark.smoke
@pytest.mark.local_only
def test_open_board_created_via_api(
    logged_in: None,
    driver,
    api_client: TrelloApiClient,
) -> None:
    name = board_name("Mobile Board")
    board = prepare_board(api_client, name=name)

    try:
        with allure.step("Mobile: открыть доску из списка"):
            WorkspaceScreen(driver).should_have_board(name, board.url).open_board(
                name, board.url
            )
            BoardScreen(driver)
    finally:
        api_client.delete_board(board.id)
