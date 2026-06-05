"""Конфигурация mobile: Pydantic-профили local / browserstack."""

from __future__ import annotations

import os
from typing import Literal
from urllib.parse import quote

import env_loader  # noqa: F401
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TrelloCredentials(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: str
    password: str
    otp_code: str
    trello_api_key: str
    trello_api_token: str
    trello_api_base_url: str

    @classmethod
    def from_env(cls) -> TrelloCredentials:
        return cls(
            email=os.getenv("TRELLO_EMAIL", ""),
            password=os.getenv("TRELLO_PASSWORD", ""),
            otp_code=os.getenv("TRELLO_OTP", ""),
            trello_api_key=os.getenv("TRELLO_API_KEY", ""),
            trello_api_token=os.getenv("TRELLO_API_TOKEN", ""),
            trello_api_base_url=os.getenv(
                "TRELLO_BASE_URL", "https://api.trello.com/1"
            ).rstrip("/"),
        )


class LocalMobileConfig(BaseSettings):
    """Локальный Appium. Файл: .env.local"""

    model_config = SettingsConfigDict(extra="ignore")

    appium_server_url: str = Field(
        default="http://127.0.0.1:4723", validation_alias="APPIUM_SERVER_URL"
    )
    platform_name: str = Field(default="Android", validation_alias="PLATFORM_NAME")
    platform_version: str = Field(default="11.0", validation_alias="PLATFORM_VERSION")
    device_name: str = Field(default="emulator-5554", validation_alias="DEVICE_NAME")
    app_package: str = Field(default="com.trello", validation_alias="APP_PACKAGE")
    app_activity: str = Field(
        default="com.trello.home.HomeActivity", validation_alias="APP_ACTIVITY"
    )
    automation_name: str = Field(
        default="UiAutomator2", validation_alias="AUTOMATION_NAME"
    )
    no_reset: bool = Field(default=True, validation_alias="NO_RESET")
    visible_timeout_sec: float = Field(
        default=30.0, validation_alias="MOBILE_LOCAL_VISIBLE_TIMEOUT"
    )
    reload_pause_sec: float = Field(
        default=3.0, validation_alias="MOBILE_LOCAL_RELOAD_PAUSE"
    )

    @field_validator("no_reset", mode="before")
    @classmethod
    def _parse_bool(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).lower() == "true"


class BrowserStackMobileConfig(BaseSettings):
    """BrowserStack App Automate. Файл: .env.browserstack"""

    model_config = SettingsConfigDict(extra="ignore")

    appium_server_url: str = Field(
        default="https://hub-cloud.browserstack.com/wd/hub",
        validation_alias="APPIUM_SERVER_URL",
    )
    platform_name: str = Field(default="Android", validation_alias="PLATFORM_NAME")
    platform_version: str = Field(default="12.0", validation_alias="PLATFORM_VERSION")
    device_name: str = Field(
        default="Samsung Galaxy S22", validation_alias="DEVICE_NAME"
    )
    app_package: str = Field(default="com.trello", validation_alias="APP_PACKAGE")
    app_activity: str = Field(
        default="com.trello.home.HomeActivity", validation_alias="APP_ACTIVITY"
    )
    automation_name: str = Field(
        default="UiAutomator2", validation_alias="AUTOMATION_NAME"
    )
    no_reset: bool = Field(default=False, validation_alias="NO_RESET")
    browserstack_username: str = Field(
        default="", validation_alias=AliasChoices("BROWSERSTACK_USERNAME", "BS_USERNAME")
    )
    browserstack_access_key: str = Field(
        default="",
        validation_alias=AliasChoices("BROWSERSTACK_ACCESS_KEY", "BS_ACCESS_KEY"),
    )
    browserstack_app: str = Field(
        default="", validation_alias=AliasChoices("BROWSERSTACK_APP", "BS_APP")
    )
    browserstack_build_name: str = Field(
        default="local",
        validation_alias=AliasChoices("BS_BUILD_NAME", "BUILD_NUMBER"),
    )
    browserstack_project_name: str = Field(
        default="Trello Diploma QA", validation_alias="BS_PROJECT_NAME"
    )
    visible_timeout_sec: float = Field(
        default=90.0, validation_alias="MOBILE_BS_VISIBLE_TIMEOUT"
    )
    reload_pause_sec: float = Field(default=8.0, validation_alias="MOBILE_BS_RELOAD_PAUSE")

    @field_validator("no_reset", mode="before")
    @classmethod
    def _parse_bool(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).lower() == "true"


class MobileConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_mode: Literal["local", "browserstack"]
    appium_server_url: str
    platform_name: str
    platform_version: str
    device_name: str
    app_package: str
    app_activity: str
    automation_name: str
    no_reset: bool
    email: str
    password: str
    otp_code: str
    trello_api_key: str
    trello_api_token: str
    trello_api_base_url: str
    browserstack_username: str = ""
    browserstack_access_key: str = ""
    browserstack_app: str = ""
    browserstack_build_name: str = ""
    browserstack_project_name: str = ""
    visible_timeout_sec: float
    reload_pause_sec: float

    @property
    def is_browserstack(self) -> bool:
        return self.run_mode == "browserstack"

    @property
    def is_cloud(self) -> bool:
        return self.is_browserstack

    def browserstack_hub_url(self) -> str:
        user = quote(self.browserstack_username, safe="")
        key = quote(self.browserstack_access_key, safe="")
        return f"https://{user}:{key}@hub-cloud.browserstack.com/wd/hub"

    @classmethod
    def from_local(cls, local: LocalMobileConfig, creds: TrelloCredentials) -> MobileConfig:
        return cls(
            run_mode="local",
            appium_server_url=local.appium_server_url,
            platform_name=local.platform_name,
            platform_version=local.platform_version,
            device_name=local.device_name,
            app_package=local.app_package,
            app_activity=local.app_activity,
            automation_name=local.automation_name,
            no_reset=local.no_reset,
            email=creds.email,
            password=creds.password,
            otp_code=creds.otp_code,
            trello_api_key=creds.trello_api_key,
            trello_api_token=creds.trello_api_token,
            trello_api_base_url=creds.trello_api_base_url,
            visible_timeout_sec=local.visible_timeout_sec,
            reload_pause_sec=local.reload_pause_sec,
        )

    @classmethod
    def from_browserstack(
        cls, remote: BrowserStackMobileConfig, creds: TrelloCredentials
    ) -> MobileConfig:
        return cls(
            run_mode="browserstack",
            appium_server_url=remote.appium_server_url,
            platform_name=remote.platform_name,
            platform_version=remote.platform_version,
            device_name=remote.device_name,
            app_package=remote.app_package,
            app_activity=remote.app_activity,
            automation_name=remote.automation_name,
            no_reset=remote.no_reset,
            email=creds.email,
            password=creds.password,
            otp_code=creds.otp_code,
            trello_api_key=creds.trello_api_key,
            trello_api_token=creds.trello_api_token,
            trello_api_base_url=creds.trello_api_base_url,
            browserstack_username=remote.browserstack_username,
            browserstack_access_key=remote.browserstack_access_key,
            browserstack_app=remote.browserstack_app,
            browserstack_build_name=remote.browserstack_build_name,
            browserstack_project_name=remote.browserstack_project_name,
            visible_timeout_sec=remote.visible_timeout_sec,
            reload_pause_sec=remote.reload_pause_sec,
        )

    def validate(self) -> None:
        missing = [
            name
            for name, value in (
                ("TRELLO_EMAIL", self.email),
                ("TRELLO_PASSWORD", self.password),
                ("TRELLO_API_KEY", self.trello_api_key),
                ("TRELLO_API_TOKEN", self.trello_api_token),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                f"Не заданы обязательные переменные окружения: {', '.join(missing)}"
            )
        if self.is_browserstack:
            bs_missing = [
                name
                for name, value in (
                    ("BROWSERSTACK_USERNAME", self.browserstack_username),
                    ("BROWSERSTACK_ACCESS_KEY", self.browserstack_access_key),
                    ("BROWSERSTACK_APP", self.browserstack_app),
                )
                if not value
            ]
            if bs_missing:
                raise ValueError(
                    f"Для BrowserStack задайте: {', '.join(bs_missing)} "
                    "(загрузите APK в BS → App ID bs://...)"
                )


def load_mobile_config() -> MobileConfig:
    mode = os.getenv("RUN_MODE", "local").strip().lower()
    creds = TrelloCredentials.from_env()
    if mode == "browserstack":
        return MobileConfig.from_browserstack(BrowserStackMobileConfig(), creds)
    return MobileConfig.from_local(LocalMobileConfig(), creds)


class RunTarget:
    def __init__(self, mode: str) -> None:
        self.mode = mode.strip().lower()

    @property
    def is_browserstack(self) -> bool:
        return self.mode == "browserstack"

    @property
    def is_cloud(self) -> bool:
        return self.is_browserstack

    @property
    def is_local(self) -> bool:
        return self.mode == "local"

    @property
    def label(self) -> str:
        if self.is_browserstack:
            return "BrowserStack App Automate"
        return "local emulator"


_cached_config: MobileConfig | None = None


def get_mobile_config() -> MobileConfig:
    global _cached_config
    if _cached_config is None:
        _cached_config = load_mobile_config()
    return _cached_config


def reset_mobile_config() -> None:
    global _cached_config
    _cached_config = None
