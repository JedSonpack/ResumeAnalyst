from io import BytesIO


def test_reject_non_pdf_upload(client):
    response = client.post(
        "/analyze",
        files={"resume": ("resume.txt", BytesIO(b"bad"), "text/plain")},
    )

    assert response.status_code == 400
    assert "仅支持 PDF 文件" in response.text


def test_reject_empty_filename(client):
    response = client.post(
        "/analyze",
        files={"resume": ("", BytesIO(b""), "application/pdf")},
    )

    assert response.status_code == 400
    assert "请先选择简历文件" in response.text
