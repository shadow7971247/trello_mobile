"""Маркеры local / browserstack для pytest."""

from __future__ import annotations

import pytest


def apply_local_browserstack_markers(items: list[pytest.Item]) -> None:
    for item in items:
        if item.get_closest_marker("lambdatest_only") is not None:
            item.add_marker(pytest.mark.browserstack)
        if item.get_closest_marker("browserstack") is None:
            item.add_marker(pytest.mark.local)
