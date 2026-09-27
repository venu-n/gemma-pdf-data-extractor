import base64
import json
import cv2
import requests
from app.config import settings
from app.models import VisionExtraction

_PROMPT = '''
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
- Amount must be the numeric amount visible on the check.
- Confidence is your confidence that each field was actually read from the image.
- Do not return explanatory text outside the JSON object.
- The check number may appear as an unlabeled number, commonly near the top corner or another check-number position. Do not require a "check number" label.
- The payment-purpose field may have labels such as MEMO, FOR, or similar wording. Treat the text associated with that field as the memo/payment purpose.
'''

def extract_with_ollama(image) -> VisionExtraction:
    image_bytes = _encode_image(image)
    payload = {'model': settings.ollama_model, 'messages': [{'role': 'user', 'content': _PROMPT, 'images': [image_bytes]}], 'stream': False, 'format': 'json'}
    response = requests.post(f"{settings.ollama_url.rstrip('/')}/api/chat", json=payload, timeout=settings.vision_timeout)
    response.raise_for_status()
    try:
        content = response.json()['message']['content']
    except (KeyError, TypeError) as exc:
        raise ValueError('Invalid response from Ollama') from exc
    return _parse_response(content)

def _encode_image(image) -> str:
    if image is None or image.size == 0:
        raise ValueError('Invalid check image')
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.ndim == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    elif image.ndim != 3 or image.shape[2] != 3:
        raise ValueError('Expected grayscale, RGB, or RGBA image')
    success, encoded = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not success:
        raise ValueError('Unable to encode check image')
    return base64.b64encode(encoded.tobytes()).decode('utf-8')

def _parse_response(content: str) -> VisionExtraction:
    data = _extract_json_object(content)
    confidence_data = data.get('confidence') or {}
    confidence = {}
    for field in ('check_number', 'issue_date', 'beneficiary_name', 'amount', 'memo'):
        try:
            value = float(confidence_data.get(field, 0.0))
        except (TypeError, ValueError):
            value = 0.0
        confidence[field] = max(0.0, min(1.0, value))
    return VisionExtraction(
        check_number=data.get('check_number'), issue_date=data.get('issue_date'),
        beneficiary_name=data.get('beneficiary_name'), amount=data.get('amount'),
        memo=data.get('memo'), confidence=confidence, raw_response=content,
    )

def _extract_json_object(content: str) -> dict:
    if not isinstance(content, str):
        raise ValueError('Ollama returned non-text content')
    content = content.strip()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find('{'), content.rfind('}')
        if start < 0 or end <= start:
            raise ValueError('Ollama returned invalid JSON')
        try:
            data = json.loads(content[start:end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError('Ollama returned invalid JSON') from exc
    if not isinstance(data, dict):
        raise ValueError('Ollama JSON response must be an object')
    return data
