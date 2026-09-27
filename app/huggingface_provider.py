import base64
import json
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

from huggingface_hub import InferenceClient

from app.config import settings


_PROMPT = """
Inspect the supplied image of a single bank check.

Extract ONLY information visibly present on this check.

Return JSON only with exactly these fields:

{
  "check_number": null,
  "issue_date": null,
  "beneficiary_name": null,
  "amount": null,
  "memo": null,
  "confidence": {
    "check_number": 0.0,
    "issue_date": 0.0,
    "beneficiary_name": 0.0,
    "amount": 0.0,
    "memo": 0.0
  }
}

Rules:
- Read printed and handwritten information.
- Do not use outside knowledge.
- Do not guess, infer, or invent missing information.
- Use null when a field is not reliably readable.
- Preserve visible beneficiary text as reasonably readable.
- Preserve visible memo/payment-purpose text as reasonably readable.
- Amount should be the numeric amount printed on the check.
- Confidence must be from 0.0 to 1.0.
- Do not return explanatory text outside the JSON object.
"""


@dataclass(frozen=True)
class HuggingFaceExtraction:
    check_number: Optional[str]
    issue_date: Optional[str]
    beneficiary_name: Optional[str]
    amount: Optional[str]
    memo: Optional[str]
    confidence: dict[str, float]
    raw_response: str


def extract_with_huggingface(image) -> HuggingFaceExtraction:
    if not settings.huggingface_api_key:
        raise RuntimeError(
            "HUGGINGFACE_API_KEY is not configured"
        )

    if not settings.huggingface_model:
        raise RuntimeError(
            "HUGGINGFACE_MODEL is not configured"
        )

    image_bytes = _encode_image(image)

    image_data = (
        "data:image/jpeg;base64,"
        + base64.b64encode(image_bytes).decode("ascii")
    )

    client = InferenceClient(
        api_key=settings.huggingface_api_key,
        provider=(
            settings.huggingface_provider
            or "auto"
        ),
    )

    response = client.chat.completions.create(
        model=settings.huggingface_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": _PROMPT,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data,
                        },
                    },
                ],
            }
        ],
    )

    raw_response = _extract_response_text(response)
    payload = _parse_json(raw_response)

    return HuggingFaceExtraction(
        check_number=_optional_string(
            payload.get("check_number")
        ),
        issue_date=_optional_string(
            payload.get("issue_date")
        ),
        beneficiary_name=_optional_string(
            payload.get("beneficiary_name")
        ),
        amount=_optional_string(
            payload.get("amount")
        ),
        memo=_optional_string(
            payload.get("memo")
        ),
        confidence=_parse_confidence(
            payload.get("confidence")
        ),
        raw_response=raw_response,
    )


def _encode_image(image) -> bytes:
    buffer = BytesIO()

    if hasattr(image, "convert"):
        pil_image = image.convert("RGB")
    else:
        from PIL import Image

        pil_image = Image.fromarray(image).convert("RGB")

    pil_image.save(
        buffer,
        format="JPEG",
        quality=92,
    )

    return buffer.getvalue()


def _extract_response_text(response) -> str:
    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "Hugging Face returned an empty response"
        )

    return str(content).strip()


def _parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end <= start:
            raise ValueError(
                "Hugging Face response did not contain JSON"
            )

        return json.loads(
            text[start:end + 1]
        )


def _optional_string(value) -> Optional[str]:
    if value is None:
        return None

    value = str(value).strip()
    return value or None


def _parse_confidence(value) -> dict[str, float]:
    if not isinstance(value, dict):
        return {}

    result = {}

    for field in (
        "check_number",
        "issue_date",
        "beneficiary_name",
        "amount",
        "memo",
    ):
        try:
            score = float(value.get(field, 0.0))
        except (TypeError, ValueError):
            score = 0.0

        result[field] = max(
            0.0,
            min(1.0, score),
        )

    return result