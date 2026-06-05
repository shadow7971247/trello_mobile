"""Capabilities для локального Android, LambdaTest и BrowserStack."""

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


def browserstack_capabilities(
    config: MobileConfig, *, session_name: str = "trello-mobile"
) -> dict[str, object]:
    """W3C capabilities для APK в BrowserStack (bs://...)."""
    return {
        "platformName": config.platform_name,
        "appium:automationName": config.automation_name,
        "appium:deviceName": config.device_name,
        "appium:platformVersion": config.platform_version,
        "appium:app": config.browserstack_app,
        "appium:noReset": config.no_reset,
        "appium:autoGrantPermissions": True,
        "appium:newCommandTimeout": 300,
        "bstack:options": {
            "userName": config.browserstack_username,
            "accessKey": config.browserstack_access_key,
            "projectName": config.browserstack_project_name,
            "buildName": config.browserstack_build_name,
            "sessionName": session_name,
            "networkLogs": True,
            "appiumVersion": "2.0.1",
        },
    }


def build_capabilities(
    config: MobileConfig, *, session_name: str | None = None
) -> dict[str, object]:
    name = session_name or "trello-mobile"
    if config.is_lambdatest:
        return lambdatest_capabilities(config, session_name=name)
    if config.is_browserstack:
        return browserstack_capabilities(config, session_name=name)
    return local_android_capabilities(config)


def remote_hub_url(config: MobileConfig) -> str:
    if config.is_lambdatest:
        return config.lambdatest_hub_url()
    if config.is_browserstack:
        return config.browserstack_hub_url()
    return config.appium_server_url
