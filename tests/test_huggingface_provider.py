import json
from unittest.mock import patch

import pytest

from app.huggingface_provider import (
    _parse_confidence,
    _parse_json,
    _optional_string,
)


def test_optional_string():
    assert _optional_string(None) is None
    assert _optional_string("") is None
    assert _optional_string("  Mary Johnson  ") == "Mary Johnson"


def test_parse_json_valid():
    payload = _parse_json(
        '{"check_number":"0007","amount":"715.39"}'
    )

    assert payload["check_number"] == "0007"
    assert payload["amount"] == "715.39"


def test_parse_json_with_extra_text():
    payload = _parse_json(
        'Here is the result: '
        '{"check_number":"0007"}'
    )

    assert payload["check_number"] == "0007"


def test_parse_json_invalid():
    with pytest.raises(ValueError):
        _parse_json("not json")


def test_parse_confidence():
    result = _parse_confidence(
        {
            "check_number": 1.2,
            "issue_date": 0.8,
            "amount": "0.6",
        }
    )

    assert result["check_number"] == 1.0
    assert result["issue_date"] == 0.8
    assert result["amount"] == 0.6
    assert result["memo"] == 0.0


def test_parse_confidence_invalid_values():
    result = _parse_confidence(
        {
            "check_number": "invalid",
            "issue_date": -1,
            "amount": 2,
        }
    )

    assert result["check_number"] == 0.0
    assert result["issue_date"] == 0.0
    assert result["amount"] == 1.0