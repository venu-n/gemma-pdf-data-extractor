from decimal import Decimal
from app.models import CheckRecord
from app.validation import validate_check_record

def test_complete_record_is_valid():
    record = CheckRecord('check.pdf', 1, '0007', '2019-08-11', 'Mary Johnson', Decimal('715.39'), 'Monthly rent', 'Manual Review')
    result = validate_check_record(record)
    assert result.valid

def test_missing_memo_requires_manual_review():
    record = CheckRecord('check.pdf', 1, '0007', '2019-08-11', 'Mary Johnson', Decimal('715.39'), None, 'Manual Review')
    result = validate_check_record(record)
    assert not result.valid
    assert 'memo missing' in result.issues
