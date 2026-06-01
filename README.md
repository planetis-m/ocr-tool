# OCR Tool Skill

`ocr-tool` is an installable Agent Skill for extracting text from PDFs with
`pdfocr`.

## Features

It provides one workflow:
- extracts text from full PDFs or selected page ranges
- caches OCR output one page at a time so overlapping requests reuse prior work
- installs `pdfocr` when needed
- returns cleaned extracted text for downstream skills or tasks

This skill is intentionally limited to extraction. Use another skill after OCR
if you want notes, flashcards, quizzes, or other transformed outputs.

## Requirements

- **`pdfocr`**: Required for PDF-to-text extraction.
- **DeepInfra API Key**: Required by `pdfocr`.
  - Set it via `DEEPINFRA_API_KEY` (recommended).
  - Or provide it via `config.json` next to the `pdfocr` executable.

## Installation

### Using Codex

Codex recommends installing non-built-in skills using the `$skill-installer`.
Prompt Codex with:

```text
$skill-installer install the skill from repo planetis-m/study-assistant with path ocr-tool
```

### Manual Install

Clone or copy `ocr-tool` into your agent's scanned skills path.

## Usage Examples

Invoke the skill explicitly using `$ocr-tool` in your prompts:

```text
Use $ocr-tool to extract text from lecture1.pdf.
```

```text
Use $ocr-tool to OCR pages 8-20 of lecture1.pdf and return only the cleaned text.
```

```text
Use $ocr-tool on this PDF, then use $study-assistant in study-notes mode on the extracted text.
```
