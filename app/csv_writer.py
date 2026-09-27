import csv
from datetime import date
from decimal import Decimal
from pathlib import Path
from app.models import CheckRecord
CSV_COLUMNS = ('PDF File','PDF Page Number','Check Number','Issue Date','Beneficiary Name','Amount','Memo','Status','Notes')
def write_results(records: list[CheckRecord], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f'Results-{date.today().isoformat()}.csv'
    with output_path.open('w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow({'PDF File':record.pdf_file,'PDF Page Number':record.pdf_page_number,'Check Number':record.check_number or '','Issue Date':record.issue_date or '','Beneficiary Name':record.beneficiary_name or '','Amount':_format_amount(record.amount),'Memo':record.memo or '','Status':record.status,'Notes':record.notes})
    return output_path
def _format_amount(amount: Decimal | None) -> str:
    return '' if amount is None else f'{amount:.2f}'
