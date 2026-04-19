import importlib
from io import BytesIO

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient


def test_upload_pdf_and_render_analysis_result(monkeypatch):
    expected_analysis = {
        "overall_score": 78,
        "summary": "建议修改后投递",
        "raw_markdown": "# 项目经历\n\n原始内容\n",
        "normalized_markdown": "## 项目经历\n\n整理后的内容\n",
        "used_fallback": True,
        "fallback_reason": "missing_api_key",
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
    }

    main_module = importlib.import_module("app.main")
    app = main_module.create_app()
    analyze_route = next(
        route
        for route in app.router.routes
        if isinstance(route, APIRoute) and route.path == "/analyze"
    )
    monkeypatch.setitem(
        analyze_route.endpoint.__globals__,
        "extract_and_analyze_resume",
        lambda _: {
            **expected_analysis,
        },
    )
    client = TestClient(app)

    response = client.post(
        "/analyze",
        files={"resume": ("resume.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")},
    )

    assert response.status_code == 200
    assert "建议修改后投递" in response.text
    assert "项目描述偏职责罗列" in response.text
    assert "技能清单偏堆砌" in response.text
    assert "接口平均响应时间降至 120 ms" in response.text
    assert "原始 Markdown" in response.text
    assert "整理后 Markdown" in response.text
    assert "missing_api_key" in response.text
    assert '<h1 id="项目经历">项目经历</h1>' in response.text
    assert '<h2 id="项目经历">项目经历</h2>' in response.text
