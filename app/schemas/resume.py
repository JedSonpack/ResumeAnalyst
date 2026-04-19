from pydantic import BaseModel, Field


class ResumeSection(BaseModel):
    title: str
    content: str


class ParsedResume(BaseModel):
    raw_text: str
    education: ResumeSection | None = None
    skills: ResumeSection | None = None
    projects: list[ResumeSection] = Field(default_factory=list)
    internships: list[ResumeSection] = Field(default_factory=list)
    competitions: list[ResumeSection] = Field(default_factory=list)
    extras: list[ResumeSection] = Field(default_factory=list)


class MarkdownPipelineResult(BaseModel):
    raw_markdown: str
    normalized_markdown: str
    used_fallback: bool = False
    fallback_reason: str | None = None
