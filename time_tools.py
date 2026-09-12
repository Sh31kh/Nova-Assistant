"""time_tools.py — deterministic time/date/day responses.

These bypass the LLM entirely (see original spec Section 5: avoid the
LLM for trivial deterministic commands). Matched via keyword detection
in core.py before any Ollama call is made — faster, and removes one
more thing the model could get wrong.

KNOWN LIMITATION: keyword matching is a blunter instrument than the LLM
router — "I have a date tonight" would false-trigger get_date_and_time.
Acceptable here because the cost of a false positive is a harmless wrong
answer, not a dangerous action. Revisit if this becomes a real annoyance
in practice.
"""

from datetime import datetime
from num2words import num2words


def _ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _speakable_time(dt: datetime) -> str:
    """Fully spell out the time in words — Piper reads any colon-separated
    or leading-zero numeric time digit-by-digit, so we avoid handing it
    numeric time formats at all. Hyphens from num2words are replaced with
    spaces. Midnight gets its conventional spoken name; all other
    on-the-hour times are spoken as '<hour> <AM/PM>' with no 'o'clock'."""
    hour = int(dt.strftime("%I"))
    minute = dt.minute
    period = dt.strftime("%p")

    if hour == 12 and minute == 0 and period == "AM":
        return "midnight"

    hour_word = num2words(hour).replace("-", " ")

    if minute == 0:
        return f"{hour_word} {period}"
    elif minute < 10:
        return f"{hour_word} oh {num2words(minute)} {period}"
    else:
        minute_word = num2words(minute).replace("-", " ")
        return f"{hour_word} {minute_word} {period}"


def get_time() -> str:
    return f"It's {_speakable_time(datetime.now())}."


def get_date_and_time() -> str:
    """Date requests return date + time together, per design."""
    now = datetime.now()
    date_str = now.strftime(f"the {_ordinal(now.day)} of %B, %Y")
    time_str = _speakable_time(now)
    return f"It's {date_str}. The time is {time_str}."


def get_day() -> str:
    return f"It's {datetime.now().strftime('%A')}."


def check_deterministic(text: str) -> str | None:
    """Returns a direct response string if the transcript matches a
    trivial time/date/day query, or None if it should fall through to
    the normal LLM tool-calling path.

    Order matters: check "date" before "time", since a date request
    should return both."""
    lowered = text.lower()

    if "date" in lowered:
        return get_date_and_time()
    if "time" in lowered:
        return get_time()
    if "day" in lowered:
        return get_day()
    return None