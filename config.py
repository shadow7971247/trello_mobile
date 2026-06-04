"""Конфигурация mobile: Pydantic-профили local / lambdatest + общий MobileConfig."""

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


class LambdaTestMobileConfig(BaseSettings):
    """LambdaTest App Automate. Файл: .env.lambdatest"""

    model_config = SettingsConfigDict(extra="ignore")

    appium_server_url: str = Field(
        default="https://mobile-hub.lambdatest.com/wd/hub",
        validation_alias="APPIUM_SERVER_URL",
    )
    platform_name: str = Field(default="Android", validation_alias="PLATFORM_NAME")
    platform_version: str = Field(default="13", validation_alias="PLATFORM_VERSION")
    device_name: str = Field(
        default="Galaxy A33 5G", validation_alias="DEVICE_NAME"
    )
    lambdatest_is_real_mobile: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "LAMBDATEST_IS_REAL_MOBILE", "LT_IS_REAL_MOBILE", "IS_REAL_MOBILE"
        ),
    )
    app_package: str = Field(default="com.trello", validation_alias="APP_PACKAGE")
    app_activity: str = Field(
        default="com.trello.home.HomeActivity", validation_alias="APP_ACTIVITY"
    )
    automation_name: str = Field(
        default="UiAutomator2", validation_alias="AUTOMATION_NAME"
    )
    no_reset: bool = Field(default=False, validation_alias="NO_RESET")
    lambdatest_username: str = Field(
        default="", validation_alias=AliasChoices("LAMBDATEST_USERNAME", "LT_USERNAME")
    )
    lambdatest_access_key: str = Field(
        default="", validation_alias=AliasChoices("LAMBDATEST_ACCESS_KEY", "LT_ACCESS_KEY")
    )
    lambdatest_app: str = Field(
        default="", validation_alias=AliasChoices("LAMBDATEST_APP", "LT_APP")
    )
    lambdatest_build_name: str = Field(
        default="local", validation_alias=AliasChoices("LT_BUILD_NAME", "BUILD_NUMBER")
    )
    lambdatest_project_name: str = Field(
        default="Trello Diploma QA", validation_alias="LT_PROJECT_NAME"
    )
    visible_timeout_sec: float = Field(
        default=90.0, validation_alias="MOBILE_LT_VISIBLE_TIMEOUT"
    )
    reload_pause_sec: float = Field(default=8.0, validation_alias="MOBILE_LT_RELOAD_PAUSE")

    @field_validator("no_reset", "lambdatest_is_real_mobile", mode="before")
    @classmethod
    def _parse_bool(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).lower() == "true"


class MobileConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_mode: Literal["local", "lambdatest"]
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
    lambdatest_username: str
    lambdatest_access_key: str
    lambdatest_app: str
    lambdatest_build_name: str
    lambdatest_project_name: str
    lambdatest_is_real_mobile: bool
    visible_timeout_sec: float
    reload_pause_sec: float

    @property
    def is_lambdatest(self) -> bool:
        return self.run_mode == "lambdatest"

    @property
    def is_cloud(self) -> bool:
        return self.is_lambdatest

    def lambdatest_hub_url(self) -> str:
        user = quote(self.lambdatest_username, safe="")
        key = quote(self.lambdatest_access_key, safe="")
        return f"https://{user}:{key}@mobile-hub.lambdatest.com/wd/hub"

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
            lambdatest_username="",
            lambdatest_access_key="",
            lambdatest_app="",
            lambdatest_build_name="",
            lambdatest_project_name="",
            lambdatest_is_real_mobile=False,
            visible_timeout_sec=local.visible_timeout_sec,
            reload_pause_sec=local.reload_pause_sec,
        )

    @classmethod
    def from_lambdatest(
        cls, remote: LambdaTestMobileConfig, creds: TrelloCredentials
    ) -> MobileConfig:
        return cls(
            run_mode="lambdatest",
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
            lambdatest_username=remote.lambdatest_username,
            lambdatest_access_key=remote.lambdatest_access_key,
            lambdatest_app=remote.lambdatest_app,
            lambdatest_build_name=remote.lambdatest_build_name,
            lambdatest_project_name=remote.lambdatest_project_name,
            lambdatest_is_real_mobile=remote.lambdatest_is_real_mobile,
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
        if self.is_lambdatest:
            lt_missing = [
                name
                for name, value in (
                    ("LAMBDATEST_USERNAME", self.lambdatest_username),
                    ("LAMBDATEST_ACCESS_KEY", self.lambdatest_access_key),
                    ("LAMBDATEST_APP", self.lambdatest_app),
                )
                if not value
            ]
            if lt_missing:
                raise ValueError(
                    f"Для LambdaTest задайте: {', '.join(lt_missing)} "
                    "(загрузите APK в LT → App ID lt://...)"
                )


def load_mobile_config() -> MobileConfig:
    mode = os.getenv("RUN_MODE", "local").strip().lower()
    creds = TrelloCredentials.from_env()
    if mode == "lambdatest":
        return MobileConfig.from_lambdatest(LambdaTestMobileConfig(), creds)
    return MobileConfig.from_local(LocalMobileConfig(), creds)


class RunTarget:
    def __init__(
        self, mode: str, *, lambdatest_is_real_mobile: bool = False
    ) -> None:
        self.mode = mode.strip().lower()
        self.lambdatest_is_real_mobile = lambdatest_is_real_mobile

    @property
    def is_lambdatest(self) -> bool:
        return self.mode == "lambdatest"

    @property
    def is_cloud(self) -> bool:
        return self.is_lambdatest

    @property
    def is_local(self) -> bool:
        return self.mode == "local"

    @property
    def label(self) -> str:
        if self.is_lambdatest:
            kind = "real device" if self.lambdatest_is_real_mobile else "virtual emulator"
            return f"LambdaTest ({kind})"
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


