from __future__ import annotations

import re
from html import unescape

from markupsafe import Markup
from markdown import markdown

HEADING_RE = re.compile(r"<h([1-6])>(.*?)</h\1>")
TAG_RE = re.compile(r"<[^>]+>")


def render_markdown(markdown_text: str) -> Markup:
    html = markdown(
        markdown_text,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    html = _add_heading_ids(html)
    return Markup(html)


def _add_heading_ids(html: str) -> str:
    def replace(match: re.Match[str]) -> str:
        level = match.group(1)
        content = match.group(2)
        heading_id = _heading_id(content)
        return f'<h{level} id="{heading_id}">{content}</h{level}>'

    return HEADING_RE.sub(replace, html)


def _heading_id(content: str) -> str:
    plain_text = TAG_RE.sub("", content).strip()
    return unescape(plain_text)
