# CI: Jenkins + Allure TestOps

Репозиторий **trello_mobile** — Appium на эмуляторе (локально) или **BrowserStack** (Jenkins).

## Зависимость от trello_api

```text
TRELLO_API_PATH=${WORKSPACE}/trello_api
```

## BrowserStack (Jenkins)

```bash
pytest -m cloud_smoke --run-context browserstack --alluredir=allure-results
```

Секреты Jenkins:

- `BROWSERSTACK_USERNAME`, `BROWSERSTACK_ACCESS_KEY`
- `TRELLO_API_KEY`, `TRELLO_API_TOKEN`
- `TRELLO_EMAIL`, `TRELLO_PASSWORD`
- `ALLURE_TOKEN`

Публично в shell:

- `BROWSERSTACK_APP=bs://...`
- `RUN_MODE=browserstack` или `--run-context browserstack`

**Лимит:** ~100 минут на тарифе — гоняйте только `-m cloud_smoke` (2 теста) до финальной проверки.

## Local emulator (только на своей машине)

```bash
pytest -m "not browserstack" --run-context local --alluredir=allure-results
```

## Allure TestOps

```bash
allurectl upload --endpoint %ALLURE_ENDPOINT% ^
  --token %ALLURE_TOKEN% ^
  --project-id %ALLURE_PROJECT_ID% ^
  --launch-name "trello-mobile-%BUILD_NUMBER%" ^
  allure-results
```
