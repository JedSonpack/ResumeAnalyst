from app.schemas.resume import ParsedResume, ResumeSection


class ResumeSectionParser:
    def parse(self, raw_text: str) -> ParsedResume:
        parsed = ParsedResume(raw_text=raw_text)
        blocks = [block.strip() for block in raw_text.split("\n") if block.strip()]

        for index, line in enumerate(blocks):
            normalized_line = self._normalize_heading(line)
            if normalized_line == "教育经历" and index + 1 < len(blocks):
                parsed.education = ResumeSection(title=normalized_line, content=blocks[index + 1])
            if normalized_line == "技能清单" and index + 1 < len(blocks):
                parsed.skills = ResumeSection(title=normalized_line, content=blocks[index + 1])
            if normalized_line == "项目经历" and index + 1 < len(blocks):
                parsed.projects.append(
                    ResumeSection(title=normalized_line, content=blocks[index + 1])
                )

        return parsed

    def _normalize_heading(self, line: str) -> str:
        return line.lstrip("#").strip()
