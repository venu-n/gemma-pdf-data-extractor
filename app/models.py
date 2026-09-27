from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class CheckRecord:
    pdf_file: str
    pdf_page_number: int
    check_number: Optional[str] = None
    issue_date: Optional[str] = None
    beneficiary_name: Optional[str] = None
    amount: Optional[Decimal] = None
    memo: Optional[str] = None
    confidence: dict[str, float] | None = None
    status: str = "Manual Review"
    notes: str = ""


@dataclass(frozen=True)
class VisionExtraction:
    check_number: Optional[str]
    issue_date: Optional[str]
    beneficiary_name: Optional[str]
    amount: Optional[str]
    memo: Optional[str]
    confidence: dict[str, float]
    raw_response: str
