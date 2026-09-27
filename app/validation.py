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

def validate_check_record(record: CheckRecord) -> ValidationResult:
    issues = []
    if not record.check_number:
        issues.append('check number missing')
    elif not _CHECK_NUMBER_RE.fullmatch(record.check_number.strip()):
        issues.append('check number invalid')
    if not record.issue_date:
        issues.append('issue date missing')
    elif not _valid_date(record.issue_date):
        issues.append('issue date invalid')
    if not record.beneficiary_name:
        issues.append('beneficiary name missing')
    if record.amount is None:
        issues.append('amount missing')
    elif not isinstance(record.amount, Decimal) or record.amount < 0:
        issues.append('amount invalid')
    if not record.memo:
        issues.append('memo missing')
    if record.status not in {'Extracted', 'Manual Review'}:
        issues.append('invalid status')
    return ValidationResult(not issues, tuple(issues))

def _valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return True
    except ValueError:
        return False
