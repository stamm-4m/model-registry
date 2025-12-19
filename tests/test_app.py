from model_registry.app import app


def test_create_app():
    assert app is not None
