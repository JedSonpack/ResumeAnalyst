from app.schemas.resume import ParsedResume, ResumeSection


class ResumeSectionParser:
    def parse(self, raw_text: str) -> ParsedResume:
        parsed = ParsedResume(raw_text=raw_text)
        blocks = [block.strip() for block in raw_text.split("\n") if block.strip()]

        for index, line in enumerate(blocks):
            if line == "教育经历" and index + 1 < len(blocks):
                parsed.education = ResumeSection(title=line, content=blocks[index + 1])
            if line == "技能清单" and index + 1 < len(blocks):
                parsed.skills = ResumeSection(title=line, content=blocks[index + 1])
            if line == "项目经历" and index + 1 < len(blocks):
                parsed.projects.append(ResumeSection(title=line, content=blocks[index + 1]))

        return parsed
