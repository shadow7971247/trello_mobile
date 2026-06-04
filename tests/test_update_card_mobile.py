"""API создаёт карточку — mobile видит переименование (API update + проверка на доске)."""



from __future__ import annotations



import allure

import pytest



from api.assertions import assert_card_name

from api_bridge import (

    TrelloApiClient,

    card_name,

    prepare_board,

    prepare_card,

    prepare_list,

)

from models.request.update_card import UpdateCardRequest

from screens.board_screen import BoardScreen

from screens.workspace_screen import WorkspaceScreen





@allure.feature("Карточки")

@allure.story("Обновление карточки")

@pytest.mark.mobile
@pytest.mark.local_only
def test_rename_card_on_mobile_verified_by_api(

    logged_in: None,

    driver,

    api_client: TrelloApiClient,

) -> None:

    board = prepare_board(api_client)

    trello_list = prepare_list(api_client, board.id)

    card = prepare_card(api_client, trello_list.id)

    new_name = card_name("Mobile Renamed")



    try:

        with allure.step("Mobile: карточка видна на доске"):

            WorkspaceScreen(driver).open_board(board.name, board.url)

            BoardScreen(driver).should_have_card(card.name)



        with allure.step("API: переименовать карточку"):

            api_client.update_card(card.id, UpdateCardRequest(name=new_name))



        with allure.step("Mobile: новое имя на доске"):

            WorkspaceScreen(driver).open_board_via_url(board.url)

            BoardScreen(driver).should_have_card(new_name)



        with allure.step("API: проверить имя"):

            updated = api_client.get_card(card.id)

            assert_card_name(updated, new_name)

    finally:

        api_client.delete_board(board.id)

