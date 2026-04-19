from io import BytesIO


def test_show_friendly_message_when_pdf_parsing_fails(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.web.extract_and_analyze_resume",
        lambda _: (_ for _ in ()).throw(ValueError("PDF 文本提取失败")),
    )

    response = client.post(
        "/analyze",
        files={"resume": ("resume.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")},
    )

    assert response.status_code == 400
    assert "PDF 解析失败" in response.text
