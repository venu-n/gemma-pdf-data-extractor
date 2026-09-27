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

def make_record(**overrides):
    data = {
        "pdf_file": "test.pdf",
        "pdf_page_number": 1,
        "check_number": "0007",
        "issue_date": "2019-08-11",
        "beneficiary_name": "Mary Johnson",
        "amount": Decimal("715.39"),
        "memo": "Monthly rent",
        "status": "Manual Review",
    }
    data.update(overrides)
    return CheckRecord(**data)


def test_valid_record():
    result = validate_check_record(make_record())
    assert result.valid


def test_invalid_check_number():
    result = validate_check_record(
        make_record(check_number="ABC123")
    )
    assert not result.valid
    assert "check number invalid" in result.issues


def test_garbage_memo_is_rejected():
    result = validate_check_record(
        make_record(memo="00000018&")
    )
    assert not result.valid
    assert "memo invalid" in result.issues


def test_url_like_text_is_allowed():
    result = validate_check_record(
        make_record(memo="www.psdgraphics.com")
    )
    assert result.valid


def test_alphanumeric_memo_is_allowed():
    result = validate_check_record(
        make_record(memo="Rent #18")
    )
    assert result.valid


def test_invalid_amount():
    result = validate_check_record(
        make_record(amount=Decimal("-10.00"))
    )
    assert not result.valid
    assert "amount invalid" in result.issues
