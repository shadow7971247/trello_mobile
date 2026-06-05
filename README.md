# trello-mobile-tests

Mobile-автотесты Trello (Appium). **API-first** + проверка в приложении на **локальном эмуляторе**, **BrowserStack** или **LambdaTest**.

Экосистема: **trello_api** → **trello_ui** → **trello_mobile**. CI: [docs/CI.md](docs/CI.md)

## Конфигурация (диплом)

- `config.py` — Pydantic-профили **`LocalMobileConfig`**, **`BrowserStackMobileConfig`**, **`LambdaTestMobileConfig`**
- `.env` с Trello/API (или общий `.env` из **trello_ui** при локальной разработке)
- `.env.local` — эмулятор
- `.env.browserstack` — BrowserStack App Automate
- `.env.lambdatest` — LambdaTest

```bash
copy .env.local.example .env.local
copy .env.browserstack.example .env.browserstack
copy .env.lambdatest.example .env.lambdatest
```

## BrowserStack

1. Загрузите APK в [BrowserStack App Automate](https://app-automate.browserstack.com/) → скопируйте **App ID** (`bs://...`).
2. Заполните `.env.browserstack` (username, access key, `BROWSERSTACK_APP`).
3. Smoke (2 теста, экономит минуты):

```bash
pytest -m lambdatest_smoke --run-context browserstack
```

Документация: [Appium + BrowserStack](https://www.browserstack.com/docs/app-automate/appium/getting-started/python)

## LambdaTest

**Бесплатный тариф:** real devices недоступны; для Appium нужны **virtual emulators** — в `.env.lambdatest` задайте `LAMBDATEST_IS_REAL_MOBILE=false` и устройство из [Capabilities Generator](https://www.lambdatest.com/capabilities-generator/) (раздел emulator, не real device). На free есть лимит минут на **Native App на эмуляторах**; «Web virtual devices» в LT — это браузер в облаке (для `trello_ui`/Selenium), не замена Appium APK-тестов.

**Платный real device:** `LAMBDATEST_IS_REAL_MOBILE=true`, `DEVICE_NAME=Pixel 7` и т.п.

**Интеграция Trello** в LT (Integrations → Trello) — это отправка багов с сессии в доску Trello ([документация](https://www.lambdatest.com/support/docs/trello-integration/)). Для **Appium-автотестов** всё равно нужен `LAMBDATEST_APP=lt://...` (загруженный APK). Эмуляторы: [App Automation on emulators](https://www.lambdatest.com/support/docs/app-automation-on-emulators-simulators/).

### 1. Загрузить APK

```bash
# после заполнения LAMBDATEST_* в .env.lambdatest
.venv\Scripts\python.exe scripts\upload_lambdatest_app.py path\to\trello.apk
```

Скопируйте `LAMBDATEST_APP=lt://...` из вывода в `.env.lambdatest`.

Документация: [Appium + Python на LambdaTest](https://www.lambdatest.com/support/docs/appium-python/)

Список уже загруженных приложений:

```bash
.venv\Scripts\python.exe scripts\list_lambdatest_apps.py
```

### 2. Проверка запуска

```bash
.venv\Scripts\python.exe scripts\probe_lambdatest_launch.py
```

### 3. Smoke на облаке

```bash
pytest -m lambdatest_smoke --run-context lambdatest
```

## Локальный эмулятор

```bash
pytest -m mobile --run-context local
```

Appium: `appium -p 4723`, AVD запущен, `adb devices`.

## Переключение без правки env

```bash
pytest -m mobile --run-context local
pytest -m lambdatest_smoke --run-context browserstack
pytest -m lambdatest_smoke --run-context lambdatest
```

## Allure

```bash
pytest --alluredir=allure-results
allure serve allure-results
```
