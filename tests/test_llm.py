from unittest.mock import patch

from app.llm import VisionExtraction, extract_check


def make_result():
    return VisionExtraction(
        check_number="0007",
        issue_date="2019-08-11",
        beneficiary_name="Mary Johnson",
        amount="715.39",
        memo="Monthly rent",
        confidence={
            "check_number": 1.0,
            "issue_date": 1.0,
            "beneficiary_name": 1.0,
            "amount": 1.0,
            "memo": 1.0,
        },
        raw_response="{}",
    )


def test_ollama_provider_selected():
    with patch(
        "app.llm.settings.vision_provider",
        "ollama",
    ), patch(
        "app.llm.extract_with_ollama",
        return_value=make_result(),
    ) as provider:
        result = extract_check(object())

    provider.assert_called_once()
    assert result.check_number == "0007"


def test_huggingface_provider_selected():
    with patch(
        "app.llm.settings.vision_provider",
        "huggingface",
    ), patch(
        "app.llm.extract_with_huggingface",
        return_value=make_result(),
    ) as provider:
        result = extract_check(object())

    provider.assert_called_once()
    assert result.check_number == "0007"


def test_unsupported_provider_rejected():
    with patch(
        "app.llm.settings.vision_provider",
        "invalid",
    ):
        try:
            extract_check(object())
        except ValueError as exc:
            assert "Unsupported vision provider" in str(exc)
        else:
            raise AssertionError(
                "Expected ValueError"
            )