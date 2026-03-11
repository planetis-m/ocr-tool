---
name: ocr-tool
description: Extracts text from PDFs using the `pdfocr` CLI. Use this skill as a foundational step to convert document content into raw text for downstream processing.
---

# OCR Tool

Use this skill exclusively to extract source text. Do not generate final processed outputs or summaries here; simply hand off the extracted raw text to the next relevant step unless the user explicitly asks only for the raw OCR text.

Do not add verification steps unless the user explicitly asks for them.

## Scope

This skill owns all `pdfocr` usage.

- Use it when the input is a PDF that must be converted to text.
- After extraction, hand the resulting text to the next relevant skill or continue with the user's requested downstream task.

## Session OCR Cache

Use the caching procedure to avoid repeated OCR execution on the same file and page selection.

- Follow [references/ocr-cache.md](references/ocr-cache.md) exactly for the command sequence.
- Always execute cache commands directly from your current working directory.

## Process PDF Input

Extract text exclusively through `pdfocr` shell execution.

- Never read PDFs with direct file readers or ad-hoc parsers when this skill is active for extraction.

### Installation

Run the installation steps only when cache misses, before OCR execution.

- Check with `command -v pdfocr`.
- If missing, read [references/pdfocr-install.md](references/pdfocr-install.md) and attempt installation.
- Retry `command -v pdfocr` after installation. If still missing, stop and report.

### Execution

- Request unrestricted network/escalated execution directly in the tool call.
  Do not run a sandboxed `pdfocr` attempt as a probe.
- Do not inspect environment variables, shell profiles, or filesystem files to discover API keys.
  If OCR reports an auth/config failure, report the error and ask the user to configure
  `DEEPINFRA_API_KEY` or `config.json`, then retry.

### Usage

- Full document: `pdfocr INPUT.pdf --all-pages`
- Page ranges: `pdfocr INPUT.pdf --pages:"8-20,22-27"`

## Clean OCR Text

Before handing extracted text to another task, remove only clear metadata, such as:

- Headers and footers
- Page numbers
- Timestamps
- Extraneous document identifiers

Preserve all substantive core content. If text is severely fragmented, skip that fragment instead of guessing.
