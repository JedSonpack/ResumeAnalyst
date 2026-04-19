import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    main_module = importlib.import_module("app.main")
    return TestClient(main_module.create_app())
