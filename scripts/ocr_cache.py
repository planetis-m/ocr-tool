#!/usr/bin/env python3
"""Deterministic OCR cache CLI for ocr-tool."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

EXIT_OK = 0
EXIT_RUNTIME_ERROR = 1
EXIT_INVALID_ARGS = 2
EXIT_CACHE_MISS = 3

CACHE_DIR = Path(".ocr-tool-cache")
DEFAULT_PAGE_SEL = "all-pages"


def eprint(message: str) -> None:
    print(f"ocr-cache: {message}", file=sys.stderr)


def build_raw_path(pdf_input: str, page_sel: str) -> Path:
    if not pdf_input.strip():
        eprint("--pdf-input cannot be empty")
        sys.exit(EXIT_INVALID_ARGS)

    pdf_norm = str(Path(pdf_input).expanduser().resolve())
    page_norm = page_sel.strip() if page_sel and page_sel.strip() else DEFAULT_PAGE_SEL

    seed = f"{pdf_norm}\n{page_norm}".encode("utf-8")
    key = hashlib.sha256(seed).hexdigest()[:32]
    return CACHE_DIR / f"{key}.jsonl"


def parse_lines(lines: list[str]) -> tuple[list[dict], bool]:
    pages = []
    is_perfect = True

    for line in lines:
        try:
            obj = json.loads(line)
            if obj.get("status") == "ok" and obj.get("text"):
                pages.append(obj)
            else:
                is_perfect = False
        except Exception:
            is_perfect = False

    is_perfect = is_perfect and len(pages) == len(lines) and len(lines) > 0
    return pages, is_perfect


def print_formatted(filename: str, pages: list[dict]) -> None:
    result = [f"File: {filename} | Pages: {len(pages)}"]
    for i, obj in enumerate(pages):
        page_num = obj.get("page", i + 1)
        text = obj.get("text", "").strip()
        result.append(f"\n<page n={page_num}>\n{text}")
    print("\n".join(result))


def cmd_read(args: argparse.Namespace) -> int:
    raw_path = build_raw_path(args.pdf_input, args.page_sel)

    if not raw_path.exists() or raw_path.stat().st_size == 0:
        eprint("miss")
        return EXIT_CACHE_MISS

    lines = [l.strip() for l in raw_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    pages, _ = parse_lines(lines)

    print_formatted(Path(args.pdf_input).name, pages)
    return EXIT_OK


def cmd_store(args: argparse.Namespace) -> int:
    raw_path = build_raw_path(args.pdf_input, args.page_sel)

    data = sys.stdin.read()
    lines = [line.strip() for line in data.splitlines() if line.strip()]
    pages, is_perfect = parse_lines(lines)

    if not pages:
        eprint("no valid OCR text")
        return EXIT_CACHE_MISS

    if is_perfect:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", dir=CACHE_DIR, delete=False,
            prefix=".ocr-store.", suffix=".jsonl", encoding="utf-8"
        ) as f:
            f.write(data)
            tmp_path = f.name
        os.replace(tmp_path, raw_path)
        eprint("cached")
    else:
        eprint(f"partial OCR; not cached ({len(pages)} valid pages)")

    print_formatted(Path(args.pdf_input).name, pages)
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scripts/ocr_cache.py",
        description="Minimal deterministic cache CLI for ocr-tool OCR reuse.",
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    for name, fn in (("read", cmd_read), ("store", cmd_store)):
        p = sub.add_parser(name)
        p.add_argument("--pdf-input", required=True)
        p.add_argument("--page-sel", default=DEFAULT_PAGE_SEL)
        p.set_defaults(func=fn)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except BrokenPipeError:
        return EXIT_OK
    except Exception as exc:
        eprint(f"unexpected failure: {exc}")
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    sys.exit(main())
