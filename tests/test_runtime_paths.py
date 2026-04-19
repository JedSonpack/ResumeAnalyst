import importlib
import runpy
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def test_app_uses_file_based_paths_instead_of_working_directory(monkeypatch):
    project_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(project_root / "app")

    original_main = sys.modules.get("app.main")
    original_web = sys.modules.get("app.routes.web")

    sys.modules.pop("app.main", None)
    sys.modules.pop("app.routes.web", None)

    try:
        main_module = importlib.import_module("app.main")
        client = TestClient(main_module.create_app())

        response = client.get("/")

        assert response.status_code == 200
        assert "简历诊断助手" in response.text
    finally:
        if original_main is not None:
            sys.modules["app.main"] = original_main
        if original_web is not None:
            sys.modules["app.routes.web"] = original_web


def test_running_main_as_script_starts_uvicorn(monkeypatch):
    captured = {}
    project_root = Path(__file__).resolve().parents[1]

    def fake_run(app_target: str, host: str, port: int, reload: bool) -> None:
        captured["app_target"] = app_target
        captured["host"] = host
        captured["port"] = port
        captured["reload"] = reload

    monkeypatch.chdir(project_root)
    monkeypatch.setattr("uvicorn.run", fake_run)

    runpy.run_path(str(project_root / "app/main.py"), run_name="__main__")

    assert captured == {
        "app_target": "app.main:app",
        "host": "127.0.0.1",
        "port": 8000,
        "reload": False,
    }
