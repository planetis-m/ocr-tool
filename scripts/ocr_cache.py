#!/usr/bin/env python3
"""Run pdfocr and cache each successful page."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CACHE_DIR = Path(".ocr-tool-cache")
OUTPUT_PATH = CACHE_DIR / "output.txt"

EXIT_OK = 0
EXIT_RUNTIME_ERROR = 1
EXIT_INVALID_ARGS = 2
EXIT_NO_TEXT = 3
PDFOCR_OK = 0
PDFOCR_PARTIAL_FAILURE = 2


def eprint(message: str) -> None:
    print(f"ocr-cache: {message}", file=sys.stderr)


def document_cache_path(pdf: Path) -> Path:
    pdf = pdf.expanduser().resolve()
    if not pdf.is_file():
        raise ValueError(f"PDF does not exist: {pdf}")

    stat = pdf.stat()
    seed = f"{pdf}\n{stat.st_size}\n{stat.st_mtime_ns}".encode("utf-8")
    return CACHE_DIR / f"{hashlib.sha256(seed).hexdigest()[:32]}.json"


def parse_pages(selection: str) -> list[int]:
    pages: set[int] = set()
    for item in selection.split(","):
        item = item.strip()
        if not item:
            raise ValueError("page selection cannot be empty")

        if "-" in item:
            start_text, separator, end_text = item.partition("-")
            if not separator or not start_text.strip().isdigit() or not end_text.strip().isdigit():
                raise ValueError(f"invalid page selection: {item}")
            start = int(start_text)
            end = int(end_text)
            if start > end:
                raise ValueError(f"invalid page range: {item}")
            pages.update(range(start, end + 1))
        elif item.isdigit():
            pages.add(int(item))
        else:
            raise ValueError(f"invalid page selection: {item}")

    if not pages or min(pages) < 1:
        raise ValueError("page numbers must be positive")
    return sorted(pages)


def valid_text(text: object) -> bool:
    return isinstance(text, str) and bool(text.strip())


def valid_page(obj: object) -> bool:
    return (
        isinstance(obj, dict)
        and obj.get("status") == "ok"
        and isinstance(obj.get("page"), int)
        and not isinstance(obj.get("page"), bool)
        and obj["page"] > 0
        and valid_text(obj.get("text"))
    )


def read_cache(cache_path: Path) -> dict:
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"complete": False, "pages": {}}

    pages = {}
    if isinstance(cache, dict) and isinstance(cache.get("pages"), dict):
        for page, text in cache["pages"].items():
            if page.isdigit() and int(page) > 0 and valid_text(text):
                pages[page] = text
    return {"complete": cache.get("complete") is True and bool(pages), "pages": pages}


def write_cache(cache_path: Path, cache: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def select_pages(cache: dict, page_numbers: list[int]) -> dict[int, str]:
    return {
        page: cache["pages"][str(page)]
        for page in page_numbers
        if str(page) in cache["pages"]
    }


def cache_status(cache: dict, page_numbers: list[int] | None) -> tuple[dict[int, str], list[int] | None]:
    if page_numbers is None:
        if cache["complete"]:
            return {int(page): text for page, text in cache["pages"].items()}, []
        return {}, None

    pages = select_pages(cache, page_numbers)
    missing = [page for page in page_numbers if page not in pages]
    return pages, missing


def cache_pages(cache_path: Path, cache: dict, pages: dict[int, str]) -> None:
    for page, text in pages.items():
        cache["pages"][str(page)] = text
    if pages:
        write_cache(cache_path, cache)


def run_pdfocr(pdf: Path, page_numbers: list[int] | None) -> tuple[int, dict[int, str]] | None:
    page_arg = "--all-pages"
    if page_numbers is not None:
        page_arg = "--pages:" + ",".join(str(page) for page in page_numbers)

    try:
        result = subprocess.run(
            ["pdfocr", str(pdf), page_arg],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        eprint("pdfocr is not installed")
        return None

    if result.stderr.strip():
        print(result.stderr.rstrip(), file=sys.stderr)
    if result.returncode not in (PDFOCR_OK, PDFOCR_PARTIAL_FAILURE):
        eprint(f"pdfocr failed with exit code {result.returncode}")
        return None

    pages = {}
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if valid_page(obj):
            pages[obj["page"]] = obj["text"]

    return result.returncode, pages


def write_output(pdf: Path, pages: dict[int, str], output_path: Path) -> None:
    result = [f"File: {pdf.name} | Pages: {len(pages)}"]
    for page_number in sorted(pages):
        result.append(f"\n<page n={page_number}>\n{pages[page_number].strip()}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(result) + "\n", encoding="utf-8")
    page_word = "page" if len(pages) == 1 else "pages"
    print(f"ocr-cache: wrote {len(pages)} {page_word} to {output_path}")


def extract(pdf: Path, selection: str | None, output_path: Path) -> int:
    cache_path = document_cache_path(pdf)
    cache = read_cache(cache_path)
    page_numbers = parse_pages(selection) if selection is not None else None

    pages, missing = cache_status(cache, page_numbers)
    if missing == []:
        write_output(pdf, pages, output_path)
        return EXIT_OK

    extracted = run_pdfocr(pdf, missing)
    if extracted is None:
        return EXIT_RUNTIME_ERROR

    pdfocr_exit, pdfocr_pages = extracted
    cache_pages(cache_path, cache, pdfocr_pages)

    if pdfocr_exit == PDFOCR_PARTIAL_FAILURE:
        if pdfocr_pages:
            eprint("partial OCR; cached valid pages only")
        else:
            eprint("pdfocr returned page errors and no valid text")
        return EXIT_RUNTIME_ERROR

    if page_numbers is None:
        if not pdfocr_pages:
            eprint("no valid OCR text")
            return EXIT_NO_TEXT
        cache["complete"] = True
        write_cache(cache_path, cache)
        write_output(pdf, pdfocr_pages, output_path)
        return EXIT_OK

    pages, missing = cache_status(cache, page_numbers)
    if missing:
        eprint("missing pages: " + ",".join(str(page) for page in missing))
        return EXIT_RUNTIME_ERROR if pdfocr_pages else EXIT_NO_TEXT

    write_output(pdf, pages, output_path)
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scripts/ocr_cache.py",
        description="OCR a PDF and cache each successful page.",
    )
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pages", help='optional page selection, such as "1-5,8"')
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return extract(args.pdf, args.pages, args.output)
    except ValueError as exc:
        eprint(str(exc))
        return EXIT_INVALID_ARGS
    except BrokenPipeError:
        return EXIT_OK
    except Exception as exc:
        eprint(f"unexpected failure: {exc}")
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    sys.exit(main())
