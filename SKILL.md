---
name: ocr-tool
description: Extracts text from PDFs using the `pdfocr` CLI. Use this skill as a foundational step to convert document content into raw text for downstream processing.
---

# OCR Tool

Use this skill only to extract source text. Do not generate final processed outputs or summaries here; hand off the extracted raw text to the next step unless the user explicitly asks only for the OCR text.

Do not add verification steps unless the user explicitly asks.

## Scope

This skill owns all `pdfocr` usage.

- Use it when the input is a PDF that must be converted to text.
- After extraction, pass the resulting text to the next relevant skill or continue with the user's downstream task.

## Session OCR Cache

Use the caching procedure to avoid repeated OCR execution on the same file and page selection.

- Follow [references/ocr-cache.md](references/ocr-cache.md) exactly for the command sequence.
- Run cache commands directly from your current working directory.

## Process PDF Input

Extract text exclusively through `pdfocr` shell execution.

- Do not read PDFs with direct file readers or ad hoc parsers when this skill is active.

### Installation

Run the installation steps only when cache misses, before OCR execution.

- Check for `pdfocr` with `command -v pdfocr`.
- If it is missing, read [references/pdfocr-install.md](references/pdfocr-install.md) and attempt installation.
- Check again after installation. If it is still missing, stop and report the failure.

### Execution

- Request unrestricted network or escalated execution directly in the tool call.
  Do not run a sandboxed `pdfocr` probe first.
- Do not inspect environment variables, shell profiles, or filesystem files to discover API keys.
  If OCR reports an auth or config failure, report the error and ask the user to configure
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

Preserve all substantive content. If a fragment is too broken to recover confidently, omit it rather than guess.
