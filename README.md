# Gemma-only PDF Check Extractor

PDF -> render -> detect check regions -> crop -> Gemma vision -> normalize -> validate -> CSV/Manual Review.

OCR is intentionally excluded.

Output columns: PDF File, PDF Page Number, Check Number, Issue Date, Beneficiary Name, Amount, Memo, Status, Notes.

Windows:
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m pytest -q
python run.py
```

Put PDFs in `input\`. Ollama is expected at `http://localhost:11434` with `gemma4:e4b`.
