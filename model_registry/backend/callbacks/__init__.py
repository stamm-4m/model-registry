from model_registry.backend.callbacks.callbacks_sidebar import register_sidebar_callbacks
from model_registry.backend.callbacks.callbacks_model_upload import register_model_upload_callbacks
from model_registry.backend.callbacks.callback_auth import register_auth_callbacks
from model_registry.backend.callbacks.callbacks_toolbar import register_toolbar_callbacks


def register_callbacks(app):
    register_sidebar_callbacks(app)
    register_model_upload_callbacks(app)
    register_auth_callbacks(app)
    register_toolbar_callbacks(app)