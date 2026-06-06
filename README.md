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

**Устройство по умолчанию:** `Google Pixel 8` / Android `14.0` (см. `.env.browserstack`).

Если сессия падает с `app launch failed` — часто виноват **слишком новый APK Trello** (например `2026.10.x`).
Загрузите **более старую** сборку APK (APKMirror и т.п.), получите новый `bs://...`.
Activity в APK: `com.trello.home.HomeActivity` (не `com.trello.app.activity.HomeActivity`).

Диагностика устройств: `python scripts/probe_bs_devices.py`

1. Загрузите APK в [BrowserStack App Automate](https://app-automate.browserstack.com/) → **App ID** (`bs://...`).
2. Заполните `.env.browserstack` (username, access key, `BROWSERSTACK_APP`).
3. Проверка сессии:

```bash
python scripts/probe_browserstack_launch.py
```

4. Smoke в CI (3 теста **без логина** Atlassian — полные сценарии на эмуляторе):

```bash
pytest -m cloud_smoke --run-context browserstack
```

Файл: `tests/test_smoke_browserstack.py` — package, welcome, reactivate.

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
