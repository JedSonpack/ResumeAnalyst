from __future__ import annotations

import re
import unicodedata

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
