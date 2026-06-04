# CI: Jenkins + Allure TestOps

Репозиторий **trello_mobile** — Appium (локальный эмулятор или LambdaTest).

## Зависимости

- **trello_api** — рядом или `TRELLO_API_PATH`
- Учётные данные Trello/API — `.env` (можно скопировать из **trello_ui**)

## Jenkins: локальный эмулятор

Агент с Android SDK + AVD + Appium:

```bash
pip install -r requirements.txt
pytest -m "not browserstack" --run-context local --alluredir=allure-results
```

Перед прогоном: `adb devices`, Appium на `4723`.

## Jenkins: LambdaTest

Секреты: `LAMBDATEST_USERNAME`, `LAMBDATEST_ACCESS_KEY`, `LAMBDATEST_APP` (`lt://...`).

```bash
pytest -m lambdatest_smoke --run-context lambdatest --alluredir=allure-results
```

Бесплатный тариф: `LAMBDATEST_IS_REAL_MOBILE=false` (virtual emulator). Подробности — [README.md](../README.md).

## Allure TestOps

```bash
allurectl upload --endpoint %ALLURE_ENDPOINT% ^
  --token %ALLURE_TOKEN% ^
  --project-id %ALLURE_PROJECT_ID% ^
  --launch-name "trello-mobile-%BUILD_NUMBER%" ^
  allure-results
```
