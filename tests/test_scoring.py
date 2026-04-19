from app.schemas.resume import ParsedResume, ResumeSection
from app.services.scoring import ResumeScorer


def test_score_resume_with_missing_metrics():
    parsed = ParsedResume(
        raw_text="demo",
        education=ResumeSection(title="教育经历", content="某大学"),
        skills=ResumeSection(title="技能清单", content="Python Java Redis"),
        projects=[ResumeSection(title="项目经历", content="负责论坛后端开发")],
    )

    result = ResumeScorer().score(parsed)

    assert result.overall_score < 85
    assert result.summary == "建议修改后投递"
    assert any(item.name == "成果量化程度" for item in result.dimension_scores)
