"""Доска создана через API отображается в мобильном приложении."""

from __future__ import annotations

import allure
import pytest

from api_bridge import TrelloApiClient, board_name, prepare_board
from screens.workspace_screen import WorkspaceScreen


@allure.feature("Доски")
@allure.story("Создание доски")
@pytest.mark.mobile
@pytest.mark.local_only
def test_board_from_api_visible_on_mobile(
    logged_in: None,
    driver,
    api_client: TrelloApiClient,
) -> None:
    name = board_name("API Mobile Board")
    board = prepare_board(api_client, name=name)

    try:
        with allure.step("Mobile: доска видна в workspace"):
            WorkspaceScreen(driver).should_have_board(name, board.url)
    finally:
        api_client.delete_board(board.id)
