---
name: ocr-tool
description: Extract raw text from PDF files with OCR, including full-document extraction, selected page ranges, and reuse of cached pages. Use when a user asks to OCR a PDF, extract text from a scanned PDF, or read selected PDF pages.
---

# OCR Tool

Use this skill only to extract source text from PDFs.

Do not add verification steps unless the user explicitly asks.

## Scope

This skill owns all `pdfocr` usage.

- Use it when the input is a PDF that must be converted to text.

## Session OCR Cache

Run one cache command for both cache lookup and OCR extraction. The script prints
cached text immediately when possible. Otherwise it runs `pdfocr`, caches each
successful page independently, and prints the extracted text. This allows
overlapping page ranges to reuse work.

- Run cache commands directly from your current working directory.
- Exit code `0`: OCR text was printed.
- Exit code `3`: no valid text was extracted.
- Exit code `1` or `2`: stop and report the failure.

## Process PDF Input

Extract text exclusively through `pdfocr` shell execution.

- Do not read PDFs with direct file readers or ad hoc parsers when this skill is active.

### Installation

Run the installation steps only when the cache command reports that `pdfocr` is
not installed.

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

- Full document: `python3 <SKILL_PATH>/scripts/ocr_cache.py INPUT.pdf`
- Page ranges: `python3 <SKILL_PATH>/scripts/ocr_cache.py INPUT.pdf "8-20,22-27"`

## Clean OCR Text

Before returning extracted text, remove only clear metadata, such as:

- Headers and footers
- Page numbers
- Timestamps
- Extraneous document identifiers

Preserve all substantive content. If a fragment is too broken to recover confidently, omit it rather than guess.
