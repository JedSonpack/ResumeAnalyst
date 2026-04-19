from app.services.resume_section_parser import ResumeSectionParser


def test_parse_resume_sections():
    parser = ResumeSectionParser()
    parsed = parser.parse(
        "教育经历\n某大学\n技能清单\nPython Redis\n项目经历\n校园论坛系统"
    )

    assert parsed.education is not None
    assert parsed.skills is not None
    assert len(parsed.projects) == 1
