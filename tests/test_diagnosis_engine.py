from app.schemas.resume import ParsedResume, ResumeSection
from app.services.diagnosis_engine import DiagnosisEngine


def test_generate_issues_risks_and_rewrite_guidance():
    parsed = ParsedResume(
        raw_text="demo",
        projects=[ResumeSection(title="项目经历", content="负责后端开发")],
        skills=ResumeSection(title="技能清单", content="Python Java Redis Kafka MySQL"),
    )

    result = DiagnosisEngine().analyze(parsed)

    assert len(result.top_issues) >= 1
    assert len(result.risk_flags) >= 1
    assert len(result.rewrite_suggestions) >= 1
