# OCR Cache Procedure

Use this procedure for any PDF-based request to avoid rerunning OCR on the same file and page selection.

## 1. Read Cache

```bash
python3 <SKILL_PATH>/scripts/ocr_cache.py read \
  --pdf-input "path/to/file.pdf" --page-sel "1-5"
```

*(Omit `--page-sel` for full-document OCR.)*

**Exit codes:**
- `0`: Cache hit. The cached text is printed to stdout. Use it directly.
- `3`: Cache miss. Continue to **Step 2 (Run OCR & Store)**.
- `1` or `2`: Error. Stop and report the failure.

## 2. Run OCR & Store (On Miss)

```bash
pdfocr "path/to/file.pdf" <OCR_PAGE_ARG> | \
  python3 <SKILL_PATH>/scripts/ocr_cache.py store \
  --pdf-input "path/to/file.pdf" --page-sel "1-5"
```

**Exit codes:**
- `0`: OCR text is printed to stdout. Use it directly.
- `3`: No valid text was extracted. Report failure.
- `1` or `2`: Error. Stop and report the failure.
