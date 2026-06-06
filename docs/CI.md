# CI: Jenkins + Allure TestOps

Репозиторий **trello_mobile** — Appium на эмуляторе (локально) или **BrowserStack** (Jenkins).

## Зависимость от trello_api

```text
TRELLO_API_PATH=${WORKSPACE}/trello_api
```

Нужна для **локальных** тестов с API-bridge. Для `cloud_smoke` на BrowserStack — не обязательна.

## BrowserStack (Jenkins)

```bash
pytest -m cloud_smoke --run-context browserstack --alluredir=allure-results
```

**3 smoke-теста без логина** (`tests/test_smoke_browserstack.py`):

- запуск APK, `com.trello` в foreground;
- экран Welcome / Log in;
- повторный `activate_app`.

Секреты Jenkins:

- `BROWSERSTACK_USERNAME`, `BROWSERSTACK_ACCESS_KEY`
- `BROWSERSTACK_APP=bs://...`

`TRELLO_EMAIL` / `TRELLO_PASSWORD` для `cloud_smoke` **не нужны**.

Публично в shell:

- `RUN_MODE=browserstack` или `--run-context browserstack`

## Local emulator (полные сценарии с логином)

```bash
pytest -m "mobile and not browserstack" --run-context local --alluredir=allure-results
```

Логин, доски, карточки, deep link — только на эмуляторе.

## Allure TestOps

```bash
allurectl upload --endpoint %ALLURE_ENDPOINT% ^
  --token %ALLURE_TOKEN% ^
  --project-id %ALLURE_PROJECT_ID% ^
  --launch-name "trello-mobile-%BUILD_NUMBER%" ^
  allure-results
```
