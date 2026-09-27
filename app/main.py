from app.config import settings
from app.csv_writer import write_results
from app.pipeline import process_all

def main() -> None:
    settings.input_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.samples_dir.mkdir(parents=True, exist_ok=True)
    records = process_all(settings.input_dir)
    output_path = write_results(records, settings.output_dir)
    print(f'Checks processed: {len(records)}')
    print(f'CSV created: {output_path}')

if __name__ == '__main__':
    main()
