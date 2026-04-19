from fastapi.testclient import TestClient

from app.main import create_app


def test_home_page_renders_upload_entry():
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "上传 PDF 简历" in response.text
    assert "简历诊断助手" in response.text
    assert "正在解析简历" in response.text
