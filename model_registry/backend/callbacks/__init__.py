from model_registry.backend.callbacks.callback_auth import register_auth_callbacks
from model_registry.backend.callbacks.callbacks_add_project import (
    register_add_project_callbacks,
)
from model_registry.backend.callbacks.callbacks_details_model import register_details_model_callbacks
from model_registry.backend.callbacks.callbacks_edit_model import (
    register_edit_model_callbacks,
)
from model_registry.backend.callbacks.callbacks_help import register_help_callbacks
from model_registry.backend.callbacks.callbacks_home import register_home_callbacks
from model_registry.backend.callbacks.callbacks_model_upload import (
    register_model_upload_callbacks,
)
from model_registry.backend.callbacks.callbacks_sidebar import (
    register_sidebar_callbacks,
)
from model_registry.backend.callbacks.callbacks_toolbar import (
    register_toolbar_callbacks,
)
from model_registry.backend.callbacks.callbacks_upload_model_ibisba import (
    register_upload_model_ibisba_callbacks,
)


def register_callbacks(app):
    register_sidebar_callbacks(app)
    register_model_upload_callbacks(app)
    register_auth_callbacks(app)
    register_toolbar_callbacks(app)
    register_home_callbacks(app)
    register_edit_model_callbacks(app)
    register_add_project_callbacks(app)
    register_upload_model_ibisba_callbacks(app)
    register_help_callbacks(app)
    register_details_model_callbacks(app)