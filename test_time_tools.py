"""Tests for _speakable_time — locks in the exact behavior from tonight's
debugging session so it can never silently regress."""

from datetime import datetime
from time_tools import _speakable_time


def test_on_the_hour_no_oclock():
    assert _speakable_time(datetime(2026, 9, 12, 15, 0)) == "three PM"


def test_noon_is_twelve_pm_not_noon():
    assert _speakable_time(datetime(2026, 9, 12, 12, 0)) == "twelve PM"


def test_midnight_special_case():
    assert _speakable_time(datetime(2026, 9, 12, 0, 0)) == "midnight"


def test_twelve_oh_one_am_not_midnight():
    assert _speakable_time(datetime(2026, 9, 12, 0, 1)) == "twelve oh one AM"


def test_single_digit_minute_gets_oh():
    assert _speakable_time(datetime(2026, 9, 12, 15, 5)) == "three oh five PM"


def test_hyphen_stripped_from_compound_numbers():
    result = _speakable_time(datetime(2026, 9, 12, 15, 45))
    assert "-" not in result
    assert result == "three forty five PM"