"""API удаляет карточку — mobile проверяет, что её нет на доске."""



from __future__ import annotations



import allure

import pytest



from api_bridge import Endpoints, TrelloApiClient, prepare_board, prepare_card, prepare_list

from screens.board_screen import BoardScreen

from screens.workspace_screen import WorkspaceScreen





@allure.feature("Карточки")

@allure.story("Удаление карточки")

@pytest.mark.mobile
@pytest.mark.local_only
def test_delete_card_on_mobile_verified_by_api(

    logged_in: None,

    driver,

    api_client: TrelloApiClient,

) -> None:

    board = prepare_board(api_client)

    trello_list = prepare_list(api_client, board.id)

    card = prepare_card(api_client, trello_list.id)



    try:

        with allure.step("Mobile: карточка видна на доске"):

            WorkspaceScreen(driver).open_board(board.name, board.url)

            BoardScreen(driver).should_have_card(card.name)



        with allure.step("API: удалить карточку"):

            api_client.delete_card(card.id)



        with allure.step("Mobile: карточки нет на доске"):

            WorkspaceScreen(driver).open_board_via_url(board.url)

            BoardScreen(driver).should_not_have_card(card.name, board.url)



        with allure.step("API: карточка удалена"):

            response = api_client.raw_request(

                "GET",

                Endpoints.CARD_BY_ID.format(card_id=card.id),

                validate=False,

            )

            assert response.status_code in (404, 410)

    finally:

        api_client.delete_board(board.id)

