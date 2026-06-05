# trello-mobile-tests

Mobile-автотесты Trello (Appium). **API-first** + проверка в приложении на **локальном эмуляторе** или **BrowserStack**.

Экосистема: **trello_api** → **trello_ui** → **trello_mobile**. CI: [docs/CI.md](docs/CI.md)

## Конфигурация

- `config.py` — Pydantic-профили **`LocalMobileConfig`** и **`BrowserStackMobileConfig`**
- `.env` с Trello/API (или общий `.env` из **trello_ui**)
- `.env.local` — эмулятор
- `.env.browserstack` — BrowserStack App Automate

```bash
copy .env.local.example .env.local
copy .env.browserstack.example .env.browserstack
```

## BrowserStack

1. Загрузите APK в [BrowserStack App Automate](https://app-automate.browserstack.com/) → **App ID** (`bs://...`).
2. Заполните `.env.browserstack` (username, access key, `BROWSERSTACK_APP`).
3. Проверка сессии:

```bash
python scripts/probe_browserstack_launch.py
```

4. Smoke в CI (2 теста, экономит минуты):

```bash
pytest -m cloud_smoke --run-context browserstack
```

Документация: [Appium + BrowserStack](https://www.browserstack.com/docs/app-automate/appium/getting-started/python)

## Локальный эмулятор

```bash
pytest -m mobile --run-context local
```

Appium: `appium -p 4723`, AVD запущен, `adb devices`.

## Переключение без правки env

```bash
pytest -m mobile --run-context local
pytest -m cloud_smoke --run-context browserstack
```

## Allure

```bash
pytest --alluredir=allure-results
allure serve allure-results
```
