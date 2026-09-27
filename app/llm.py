from dataclasses import dataclass
from typing import Optional

from app.config import settings
from app.huggingface_provider import extract_with_huggingface
from app.ollama_provider import extract_with_ollama

@dataclass(frozen=True)
class VisionExtraction:
    check_number: Optional[str]
    issue_date: Optional[str]
    beneficiary_name: Optional[str]
    amount: Optional[str]
    memo: Optional[str]
    confidence: dict[str, float]
    raw_response: str


def extract_check(image) -> VisionExtraction:
    provider = settings.vision_provider.strip().lower()

    if provider == "ollama":
        result = extract_with_ollama(image)

    elif provider == "huggingface":
        result = extract_with_huggingface(image)

    else:
        raise ValueError(
            f"Unsupported vision provider: {settings.vision_provider}"
        )

    return VisionExtraction(
        check_number=result.check_number,
        issue_date=result.issue_date,
        beneficiary_name=result.beneficiary_name,
        amount=result.amount,
        memo=result.memo,
        confidence=result.confidence,
        raw_response=result.raw_response,
    )