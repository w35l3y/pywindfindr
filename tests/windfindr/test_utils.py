"""Tests for windfindr.utils"""

from datetime import datetime

from windfindr.utils import (
    filter_by,
    get_current_index,
    get_inverted_tp,
    get_result,
    to_value)


def test_filter_by():
    """Test filter_by"""

    assert filter_by({}) is False
    assert filter_by({"tp":""}) is False
    assert filter_by({"tp":"low"}) is True
    assert filter_by({"tp":"high"}) is True


def test_get_current_index():
    """Test get_current_index"""

    next_item = str(1+datetime.now().year)+"-01-01T00:00:00-03:00"

    assert get_current_index([]) == -1
    assert get_current_index([{"dtl": "2022-01-01T00:00:00-03:00"}]) == -1
    assert get_current_index([{"dtl": next_item}]) == 0
    assert get_current_index([
        {"dtl": "2022-01-01T00:00:00-03:00"},
        {"dtl": next_item}
    ]) == 1


def test_get_inverted_tp():
    """Test get_inverted_tp"""

    assert get_inverted_tp("") == "low"
    assert get_inverted_tp("low") == "high"
    assert get_inverted_tp("high") == "low"


def test_get_result_empty():
    """Test get_result empty"""

    actual = get_result([])

    assert actual["available"] is False
    assert actual["value"] is None
    assert actual["prevTide"] is None
    assert actual["nextTide"] is None
    assert not actual["tides"]


def test_get_result_index_minus1():
    """Test get_result empty"""

    prev_item = {"dtl":"2022-01-01T00:00:00-03:00","tp":"low"}

    actual = get_result([
        prev_item
    ])

    assert actual["available"] is True
    assert actual["value"] == "rising"
    assert actual["prevTide"] is None
    assert actual["nextTide"] is None
    assert actual["tides"] == [
        prev_item
    ]


def test_get_result_index_0():
    """Test get_result empty"""

    next_item = {"dtl":str(1+datetime.now().year)+"-01-01T00:00:00-03:00","tp":"high"}

    actual = get_result([
        next_item
    ])

    assert actual["available"] is True
    assert actual["value"] == "rising"
    assert actual["prevTide"] is None
    assert actual["nextTide"] == next_item
    assert actual["tides"] == [
        next_item
    ]


def test_get_result_index_1():
    """Test get_result empty"""

    prev_item = {"dtl":"2022-01-01T00:00:00-03:00","tp":"high"}
    next_item = {"dtl":str(1+datetime.now().year)+"-01-01T00:00:00-03:00","tp":"low"}

    actual = get_result([
        prev_item,
        {"dtl":"2022-01-01T12:00:00-03:00"},
        next_item
    ])

    assert actual["available"] is True
    assert actual["value"] == "lowering"
    assert actual["prevTide"] == prev_item
    assert actual["nextTide"] == next_item
    assert actual["tides"] == [
        prev_item,
        next_item
    ]


def test_to_value():
    """Test to_value"""

    assert to_value("") is None
    assert to_value("low") == "lowering"
    assert to_value("high") == "rising"
