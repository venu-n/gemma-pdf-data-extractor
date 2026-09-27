from decimal import Decimal
from app.normalize import normalize_amount, normalize_date

def test_normalize_date():
    assert normalize_date('Aug. 11, 2019') == '2019-08-11'

def test_normalize_amount():
    assert normalize_amount('$715.39') == Decimal('715.39')
    assert normalize_amount('715,39') == Decimal('715.39')
