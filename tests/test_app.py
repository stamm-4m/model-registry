from model_registry.backend.app_backend import app


def test_create_app():
    assert app is not None
