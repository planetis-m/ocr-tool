# OCR Cache Procedure

Run one command for both cache lookup and OCR extraction:

```bash
python3 <SKILL_PATH>/scripts/ocr_cache.py "path/to/file.pdf"
```

For selected pages, add the page selection as the final argument:

```bash
python3 <SKILL_PATH>/scripts/ocr_cache.py "path/to/file.pdf" "1-5,8"
```

The script prints cached text immediately when possible. Otherwise it runs
`pdfocr`, caches each successful page independently, and prints the extracted
text. This allows later requests for overlapping page ranges to reuse work.

**Exit codes:**
- `0`: OCR text was printed.
- `3`: No valid text was extracted.
- `1` or `2`: Error. Stop and report the failure.
