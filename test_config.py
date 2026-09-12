"""Tests for config.py's alias resolution — the highest-risk piece,
already caused a real bug once (space/underscore mismatch)."""

from config import Config

def make_test_config():
    return Config({
        "hotkey": "f8",
        "ollama": {"model": "test", "url": "http://test", "timeout": 30},
        "aliases": {"val": "valorant", "bloons": "bloons_td6"},
        "apps": {
            "valorant": {"open_path": "C:\\fake\\valorant.exe", "close_process": "valorant.exe"},
            "bloons_td6": {"open_path": "C:\\fake\\steam.exe", "close_process": "bloons.exe"},
            "google_sheets": {"open_path": "n/a", "close_process": "n/a"},
        },
        "sites": {"google_sheets": {"url": "https://sheets.google.com"}},
    })


def test_direct_alias_match():
    cfg = make_test_config()
    assert cfg.app_open_path("val") == "C:\\fake\\valorant.exe"


def test_case_insensitive():
    cfg = make_test_config()
    assert cfg.app_open_path("VAL") == "C:\\fake\\valorant.exe"
    assert cfg.app_open_path("Val") == "C:\\fake\\valorant.exe"


def test_space_to_underscore_normalization():
    """The exact bug found tonight — 'google sheets' must resolve to
    the 'google_sheets' config key without needing an explicit alias."""
    cfg = make_test_config()
    assert cfg.site_url("google sheets") == "https://sheets.google.com"
    assert cfg.site_url("google_sheets") == "https://sheets.google.com"


def test_unknown_app_returns_none():
    cfg = make_test_config()
    assert cfg.app_open_path("nonexistent_app") is None
    assert cfg.app_close_process("nonexistent_app") is None


def test_canonical_name_still_works_without_alias():
    cfg = make_test_config()
    assert cfg.app_open_path("valorant") == "C:\\fake\\valorant.exe"