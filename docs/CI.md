# CI: Jenkins + Allure TestOps

Репозиторий **trello_mobile** — Appium на эмуляторе или в облаке.

## Зависимость от trello_api

```text
TRELLO_API_PATH=${WORKSPACE}/trello_api
```

## BrowserStack (рекомендуется для Jenkins)

```bash
pytest -m lambdatest_smoke --run-context browserstack --alluredir=allure-results
```

Секреты Jenkins:

- `BROWSERSTACK_USERNAME`, `BROWSERSTACK_ACCESS_KEY`
- `TRELLO_API_KEY`, `TRELLO_API_TOKEN`
- `TRELLO_EMAIL`, `TRELLO_PASSWORD` (логин в приложении)
- `ALLURE_TOKEN`

Публично в shell:

- `BROWSERSTACK_APP=bs://...` (App ID после загрузки APK)
- `RUN_MODE=browserstack` или `--run-context browserstack`

**Лимит:** ~100 минут на тарифе — гоняйте только `-m lambdatest_smoke` (2 теста) до финальной проверки.

## LambdaTest (альтернатива)

```bash
pytest -m lambdatest_smoke --run-context lambdatest --alluredir=allure-results
```

## Local emulator

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
