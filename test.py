from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

from markitdown import MarkItDown

PRIVATE_USE_RANGES = (
    (0xE000, 0xF8FF),
    (0xF0000, 0xFFFFD),
    (0x100000, 0x10FFFD),
)

CHAR_REPLACEMENTS = str.maketrans(
    {
        "⻓": "长",
        "⻅": "见",
        "⻔": "门",
        "戶": "户",
        "｜": "|",
        "〜": "-",
    }
)

ASCII_WORD_RE = re.compile(r"[A-Za-z0-9]$")
ASCII_WORD_START_RE = re.compile(r"^[A-Za-z0-9]")
DATE_LINE_RE = re.compile(r"^\d{4}\.\d{2}\s*-\s*(?:\d{4}\.\d{2}|至今)$")
FIELD_LABEL_RE = re.compile(r"^[^:：]{1,20}[:：]")
BLOCK_START_PREFIXES = (
    "学士",
    "硕士",
    "博士",
    "在读硕士",
    "在读博士",
    "荣誉证书",
    "工作概述",
    "项目介绍",
    "技术栈",
    "主要工作",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a PDF file to Markdown with markitdown."
    )
    parser.add_argument("pdf", help="Path to the source PDF file")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output Markdown file. Defaults to the PDF name with .md suffix.",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Write the raw markitdown output without post-processing cleanup.",
    )
    return parser.parse_args()


def is_private_use(character: str) -> bool:
    codepoint = ord(character)
    return any(start <= codepoint <= end for start, end in PRIVATE_USE_RANGES)


def strip_noise(text: str) -> str:
    cleaned_chars: list[str] = []
    for character in text:
        if character == "\n":
            cleaned_chars.append(character)
            continue
        if character == "\t":
            cleaned_chars.append(" ")
            continue
        if character == "\x00" or is_private_use(character):
            continue
        if unicodedata.category(character).startswith("C"):
            continue
        cleaned_chars.append(character)
    return "".join(cleaned_chars)


def smart_join(left: str, right: str) -> str:
    if not left:
        return right
    if not right:
        return left

    if left.endswith("-") and ASCII_WORD_START_RE.match(right):
        return left + right

    if ASCII_WORD_RE.search(left) and ASCII_WORD_START_RE.match(right):
        return f"{left} {right}"

    return left + right


def is_heading_candidate(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 12:
        return False
    if re.search(r"\d", stripped):
        return False
    if any(marker in stripped for marker in ("：", ":", "。", "；", ";", "，", ",", "|")):
        return False
    return True


def is_new_block_line(line: str) -> bool:
    stripped = line.strip()
    if is_heading_candidate(stripped) or DATE_LINE_RE.match(stripped):
        return True
    if stripped.startswith(BLOCK_START_PREFIXES):
        return True
    if FIELD_LABEL_RE.match(stripped):
        return True
    return False


def merge_wrapped_lines(text: str) -> str:
    paragraphs = re.split(r"\n\s*\n", text.strip())
    merged_paragraphs: list[str] = []

    for paragraph in paragraphs:
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if not lines:
            continue

        if len(lines) > 1 and is_heading_candidate(lines[0]):
            merged_paragraphs.append(lines[0])
            lines = lines[1:]
            if not lines:
                continue

        current = lines[0]
        for line in lines[1:]:
            if is_new_block_line(line):
                merged_paragraphs.append(current)
                current = line
                continue
            current = smart_join(current, line)
        merged_paragraphs.append(current)

    return "\n\n".join(merged_paragraphs)


def clean_markdown(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.translate(CHAR_REPLACEMENTS)
    normalized = strip_noise(normalized)
    normalized = re.sub(r"[ \u3000]+", " ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    cleaned = merge_wrapped_lines(normalized)
    return cleaned.strip() + "\n"


def convert_pdf(pdf_path: Path, clean_output: bool = True) -> str:
    converter = MarkItDown()
    result = converter.convert(str(pdf_path))
    if clean_output:
        return clean_markdown(result.text_content)
    return result.text_content


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf).expanduser().resolve()

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return 1

    if pdf_path.suffix.lower() != ".pdf":
        print(f"Input is not a PDF file: {pdf_path}")
        return 1

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else pdf_path.with_suffix(".md")
    )

    output_text = convert_pdf(pdf_path, clean_output=not args.no_clean)
    output_path.write_text(output_text, encoding="utf-8")

    print(f"Converted: {pdf_path}")
    print(f"Markdown written to: {output_path}")
    print(f"Post-processed cleanup: {'disabled' if args.no_clean else 'enabled'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
