import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from app.models import CheckRecord

@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    issues: tuple[str, ...]

_CHECK_NUMBER_RE = re.compile(r'^\d{1,20}$')

def validate_check_record(
    record: CheckRecord,
) -> ValidationResult:
    issues = []

    if not record.check_number:
        issues.append("check number missing")
    elif not _valid_check_number(record.check_number):
        issues.append("check number invalid")

    if not record.issue_date:
        issues.append("issue date missing")
    elif not _valid_date(record.issue_date):
        issues.append("issue date invalid")

    if not record.beneficiary_name:
        issues.append("beneficiary name missing")
    elif not _valid_text_field(record.beneficiary_name):
        issues.append("beneficiary name invalid")

    if record.amount is None:
        issues.append("amount missing")
    elif not _valid_amount(record.amount):
        issues.append("amount invalid")

    if not record.memo:
        issues.append("memo missing")
    elif not _valid_text_field(record.memo):
        issues.append("memo invalid")

    if record.status not in {
        "Extracted",
        "Manual Review",
    }:
        issues.append("invalid status")

    return ValidationResult(
        valid=not issues,
        issues=tuple(issues),
    )

def _valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def _valid_check_number(value: str) -> bool:
    return bool(
        _CHECK_NUMBER_RE.fullmatch(value.strip())
    )


def _valid_text_field(value: str) -> bool:
    value = value.strip()

    if len(value) < 2 or len(value) > 150:
        return False

    return any(
        character.isalpha()
        for character in value
    )


def _valid_amount(value: Decimal) -> bool:
    return (
        isinstance(value, Decimal)
        and value >= 0
    )