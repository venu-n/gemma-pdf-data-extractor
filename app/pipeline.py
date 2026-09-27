from dataclasses import replace
from pathlib import Path
import numpy as np
from app.config import settings
from app.detection import detect_check_regions
from app.image import crop_check, prepare_gemma_image
from app.llm import extract_check
from app.models import CheckRecord
from app.normalize import normalize_amount, normalize_date, normalize_text
from app.pdf import discover_pdfs, render_pages
from app.validation import validate_check_record

def process_check(image, pdf_file: str, pdf_page_number: int) -> CheckRecord:
    try:
        vision_result = extract_check(image)
    except Exception as exc:
        return CheckRecord(pdf_file=pdf_file, pdf_page_number=pdf_page_number, status='Manual Review', notes=f'Gemma failed: {type(exc).__name__}: {exc}')
    record = _build_record(vision_result, pdf_file, pdf_page_number)
    validation = validate_check_record(record)
    if validation.valid:
        return replace(record, status='Extracted', notes="")
    
    return replace(
    record,
    status="Manual Review",
    notes=_combine_notes(
        "; ".join(validation.issues),
    ),

    # *****If confidence level need to be printed, use the below.****
    # if validation.valid:
    #     return replace(record, status='Extracted', notes=_confidence_notes(record))
    
    # return replace(
    # record,
    # status="Manual Review",
    # notes=_combine_notes(
    #     "; ".join(validation.issues),
    #     _confidence_notes(record),
    # ),


)

def process_pdf(pdf_path: Path) -> list[CheckRecord]:
    records = []
    print(f'\nPDF: {pdf_path.name}')
    for page_number, page_image in render_pages(pdf_path, dpi=settings.render_dpi):
        page_array = np.asarray(page_image)
        regions = detect_check_regions(page_array)
        print(f'  Page {page_number}: {len(regions)} check candidate(s)')
        for index, region in enumerate(regions, start=1):
            print(f'  Check candidate {index}: confidence={region.confidence:.2f}')
            try:
                cropped = crop_check(page_array, region, padding=settings.detector_padding)
                gemma_image = prepare_gemma_image(cropped)
                record = process_check(gemma_image, pdf_path.name, page_number)
            except Exception as exc:
                record = CheckRecord(pdf_path.name, page_number, status='Manual Review', notes=f'Check processing failed: {type(exc).__name__}: {exc}')
            records.append(record)
            print(f"    Result: {record.status}" + (f" ({record.notes})" if record.notes else ''))
    print(f'  PDF complete: {len(records)} check record(s)')
    return records

def process_all(input_dir: Path) -> list[CheckRecord]:
    records = []
    pdfs = discover_pdfs(input_dir)
    print(f'PDF files found: {len(pdfs)}')
    for pdf_path in pdfs:
        try:
            records.extend(process_pdf(pdf_path))
        except Exception as exc:
            print(f'ERROR processing {pdf_path.name}: {type(exc).__name__}: {exc}')
    print(f'\nProcessing complete: {len(records)} check record(s)')
    return records

def _build_record(
    vision_result,
    pdf_file: str,
    pdf_page_number: int,
) -> CheckRecord:
    return CheckRecord(
        pdf_file=pdf_file,
        pdf_page_number=pdf_page_number,
        check_number=_clean_check_number(
            vision_result.check_number
        ),
        issue_date=normalize_date(
            vision_result.issue_date
        ),
        beneficiary_name=normalize_text(
            vision_result.beneficiary_name
        ),
        amount=normalize_amount(
            vision_result.amount
        ),
        memo=normalize_text(
            vision_result.memo
        ),
        confidence=dict(vision_result.confidence),
        status="Manual Review",
    )

def _clean_check_number(value):
    value = normalize_text(value)
    return value.replace(' ', '') if value else None

def _confidence_notes(record: CheckRecord) -> str:
    if not record.confidence:
        return ""

    fields = (
        "check_number",
        "issue_date",
        "beneficiary_name",
        "amount",
        "memo",
    )

    parts = []

    for field in fields:
        value = record.confidence.get(field)

        if value is not None:
            parts.append(
                f"{field} confidence={value:.2f}"
            )

    return ", ".join(parts)


def _combine_notes(*notes: str) -> str:
    return "; ".join(
        note for note in notes if note
    )
