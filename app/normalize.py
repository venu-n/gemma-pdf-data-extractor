import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

def normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = ' '.join(str(value).split())
    return value or None

def normalize_date(value: Optional[str]) -> Optional[str]:
    value = normalize_text(value)
    if not value:
        return None
    value = value.replace('.', '')
    for fmt in ('%B %d, %Y', '%B %d %Y', '%b %d, %Y', '%b %d %Y', '%m/%d/%Y', '%m/%d/%y', '%m-%d-%Y', '%m-%d-%y'):
        try:
            return datetime.strptime(value, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None

def normalize_amount(value) -> Optional[Decimal]:
    if value is None:
        return None
    raw = str(value).strip().replace('$', '').replace(' ', '')
    if not raw:
        return None
    if ',' in raw and '.' not in raw:
        parts = raw.split(',')
        raw = f'{parts[0]}.{parts[1]}' if len(parts) == 2 and len(parts[1]) == 2 else raw.replace(',', '')
    else:
        raw = raw.replace(',', '')
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        return None
    return amount if amount >= 0 else None
