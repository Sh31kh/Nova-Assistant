"""Tests for tools.py logic using a fake config — never actually
launches/kills real applications."""

import tools


class FakeConfig:
    def app_open_path(self, name):
        return None if name == "unknown" else "C:\\fake\\path.exe"

    def app_open_args(self, name):
        return []

    def app_close_process(self, name):
        return None if name == "unknown" else "fake.exe"


def test_open_unconfigured_app_fails_cleanly():
    tools.configure(FakeConfig())
    result = tools.open_application("unknown")
    assert result["success"] is False
    assert "configured" in result["message"].lower()


def test_close_unconfigured_app_fails_cleanly():
    tools.configure(FakeConfig())
    result = tools.close_application("unknown")
    assert result["success"] is False


def test_tools_not_configured_fails_gracefully():
    tools._cfg = None  # simulate configure() never having been called
    result = tools.open_application("chrome")
    assert result["success"] is False
    assert "not configured" in result["message"].lower()


def test_unsupported_request_always_fails():
    result = tools.unsupported_request("no matching tool")
    assert result["success"] is False