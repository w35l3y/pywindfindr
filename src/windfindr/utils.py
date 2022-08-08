"""utils.py"""

from datetime import datetime

import logging
import re
import sys

_LOGGER = logging.getLogger(__name__)

ISOFORMAT = "%Y-%m-%dT%H:%M:%S%z"

is_3_7_newer = (
    sys.version_info[0] > 3 or sys.version_info[0] == 3 and sys.version_info[1] >= 7
)


def to_datetime(value: str):
    """Converts str to datetime"""
    if is_3_7_newer:
        return datetime.fromisoformat(value)
    return datetime.strptime(re.sub(r"(?<=[-+]\d{2}):", "", value), ISOFORMAT)


def get_today():
    """Returns today"""

    return (datetime.now()
            .astimezone()
            .replace(hour=0, minute=0, second=0, microsecond=0))


def to_value(value: str):
    """Returns value based on tp"""
    return None if not value else "lowering" if value == "low" else "rising"


def get_inverted_tp(value: str):
    """Returns inverted tp"""
    return "high" if value == "low" else "low"


def get_current_tp(items):
    """Returns current tp based on current datetime"""
    now = datetime.now().astimezone()

    return next(
        (x["tp"] for x in items if now < to_datetime(x["dtl"])),
        get_inverted_tp(items[-1]["tp"]),
    )


def get_current_index(items):
    """Returns current tp based on current datetime"""
    now = datetime.now().astimezone()

    return next(
        (i for i, x in enumerate(items) if now < to_datetime(x["dtl"])),
        -1,
    )

def filter_by(item):
    """Filter item by tp"""

    return item.get("tp") in ["low", "high"]

def get_result(items):
    """Returns result based on items"""

    filtered_tides = list(filter(filter_by, items))

    index = get_current_index(filtered_tides)
    unavailable = 0 == len(filtered_tides)

    return {
        "available": not unavailable,
        "value": to_value(
            None
            if unavailable
            else get_inverted_tp(filtered_tides[-1]["tp"])
            if -1 == index
            else filtered_tides[index]["tp"]
        ),
        "prevTide": None if index <= 0 else filtered_tides[index - 1],
        "nextTide": None if index == -1 else filtered_tides[index],
        "tides": filtered_tides,
    }
