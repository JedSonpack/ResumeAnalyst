from pydantic import BaseModel, Field


class DimensionScore(BaseModel):
    name: str
    score: int
    reason: str


class RewriteSuggestion(BaseModel):
    section_title: str
    original_problem: str
    rewrite_direction: str
    example: str


class ResumeAnalysis(BaseModel):
    overall_score: int
    summary: str
    dimension_scores: list[DimensionScore] = Field(default_factory=list)
    top_issues: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    rewrite_suggestions: list[RewriteSuggestion] = Field(default_factory=list)
