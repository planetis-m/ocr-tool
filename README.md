# OCR Tool Skill

`ocr-tool` is an installable Agent Skill for extracting text from PDFs with `pdfocr`.

## Features

It handles the OCR-specific part of the workflow:
- Extracts text from full PDFs or selected page ranges.
- Reuses cached OCR output when the same file and page selection are requested again.
- Installs `pdfocr` on demand when it is missing.
- Returns clean extracted text for downstream skills or tasks.

This skill is intentionally limited to extraction. Use another skill after OCR if you want notes, flashcards, quizzes, or other transformed outputs.

## Requirements

- **`pdfocr`**: Used for PDF-to-text extraction. If it is missing, the agent can attempt installation.
- **DeepInfra API Key**: Required by `pdfocr`.
  - Recommended: set `DEEPINFRA_API_KEY`
  - Alternative: place `config.json` next to the real `pdfocr` binary

## Installation

### Using Codex

Codex recommends installing non-built-in skills using the `$skill-installer`. Prompt Codex with:

```text
$skill-installer install the skill from repo planetis-m/study-assistant with path ocr-tool
```

*(If the skill does not appear immediately, restart Codex).*

### Manual Install

Clone or copy the `ocr-tool` directory into your agent's scanned skills path (for example `~/.agents/skills/ocr-tool`).

If you are copying from the `study-assistant` repository, preserve the full folder structure:

```text
ocr-tool/
  SKILL.md
  README.md
  agents/openai.yaml
  references/ocr-cache.md
  references/pdfocr-install.md
  scripts/ocr_cache.py
```

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
