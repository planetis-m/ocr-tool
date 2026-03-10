# OCR Cache Procedure

Use this procedure for any request that starts from a PDF to avoid redundant OCR execution.

## 1. Read Cache

```bash
python3 <SKILL_PATH>/scripts/ocr_cache.py read \
  --pdf-input "path/to/file.pdf" --page-sel "1-5"
```

*(Omit `--page-sel` for full documents).*

**Exit codes:**
- `0`: Cache hit. The extracted text is printed to stdout. Consume it directly.
- `3`: Cache miss. Go to **Step 2 (Run & Store)**.
- `1` or `2`: Error. Stop and report.

## 2. Run OCR & Store (On Miss)

```bash
pdfocr "path/to/file.pdf" <OCR_PAGE_ARG> | \
  python3 <SKILL_PATH>/scripts/ocr_cache.py store \
  --pdf-input "path/to/file.pdf" --page-sel "1-5"
```

**Exit codes:**
- `0`: Text printed to stdout. Consume it directly.
- `3`: No valid text extracted. Report failure.
- `1` or `2`: Error. Stop and report.
