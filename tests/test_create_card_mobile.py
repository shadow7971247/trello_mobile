"""API создаёт карточку — mobile проверяет на доске."""

from __future__ import annotations

import allure
import pytest

from api_bridge import (
    TrelloApiClient,
    card_name,
    prepare_board,
    prepare_card,
    prepare_list,
)
from screens.board_screen import BoardScreen
from screens.workspace_screen import WorkspaceScreen


@allure.feature("Карточки")
@allure.story("Создание карточки")
@pytest.mark.mobile
@pytest.mark.local_only
def test_card_from_api_visible_on_board(
    logged_in: None,
    driver,
    api_client: TrelloApiClient,
) -> None:
    board = prepare_board(api_client)
    trello_list = prepare_list(api_client, board.id)
    card = prepare_card(api_client, trello_list.id, name=card_name("Mobile Card"))

    try:
        with allure.step("Mobile: открыть доску и найти карточку"):
            WorkspaceScreen(driver).open_board(board.name, board.url)
            BoardScreen(driver).should_have_card(card.name)
    finally:
        api_client.delete_board(board.id)
