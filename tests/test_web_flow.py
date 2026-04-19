from io import BytesIO


def test_upload_pdf_and_render_analysis_result(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.web.extract_and_analyze_resume",
        lambda _: {
            "overall_score": 78,
            "summary": "建议修改后投递",
            "top_issues": ["项目描述偏职责罗列，缺少结果证明"],
            "risk_flags": ["技能清单偏堆砌"],
            "rewrite_suggestions": [
                {
                    "section_title": "项目经历",
                    "original_problem": "没有结果",
                    "rewrite_direction": "增加量化指标",
                    "example": "接口平均响应时间降至 120 ms。",
                }
            ],
            "dimension_scores": [],
            "strengths": ["有项目经历"],
            "weaknesses": ["缺少量化结果"],
        },
    )

    response = client.post(
        "/analyze",
        files={"resume": ("resume.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")},
    )

    assert response.status_code == 200
    assert "建议修改后投递" in response.text
    assert "项目描述偏职责罗列" in response.text
    assert "技能清单偏堆砌" in response.text
    assert "接口平均响应时间降至 120 ms" in response.text
