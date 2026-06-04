"""Capabilities для локального Android и LambdaTest."""

from __future__ import annotations

from config import MobileConfig


def local_android_capabilities(config: MobileConfig) -> dict[str, object]:
    return {
        "platformName": config.platform_name,
        "appium:platformVersion": config.platform_version,
        "appium:deviceName": config.device_name,
        "appium:udid": config.device_name,
        "appium:appPackage": config.app_package,
        "appium:appActivity": config.app_activity,
        "appium:automationName": config.automation_name,
        "appium:noReset": config.no_reset,
        "appium:autoGrantPermissions": True,
        "appium:newCommandTimeout": 120,
    }


def lambdatest_capabilities(
    config: MobileConfig, *, session_name: str = "trello-mobile"
) -> dict[str, object]:
    """W3C capabilities для APK в LambdaTest (lt://...)."""
    return {
        "platformName": config.platform_name,
        "appium:automationName": config.automation_name,
        "appium:noReset": config.no_reset,
        "appium:autoGrantPermissions": True,
        "appium:newCommandTimeout": 300,
        "lt:options": {
            "w3c": True,
            "platformName": config.platform_name,
            "deviceName": config.device_name,
            "platformVersion": config.platform_version,
            "isRealMobile": config.lambdatest_is_real_mobile,
            "app": config.lambdatest_app,
            "build": config.lambdatest_build_name,
            "name": session_name,
            "project": config.lambdatest_project_name,
            "user": config.lambdatest_username,
            "accessKey": config.lambdatest_access_key,
            "network": True,
            "video": True,
            "visual": True,
        },
    }


def build_capabilities(
    config: MobileConfig, *, session_name: str | None = None
) -> dict[str, object]:
    if config.is_lambdatest:
        return lambdatest_capabilities(
            config, session_name=session_name or "trello-mobile"
        )
    return local_android_capabilities(config)


def remote_hub_url(config: MobileConfig) -> str:
    if config.is_lambdatest:
        return config.lambdatest_hub_url()
    return config.appium_server_url
