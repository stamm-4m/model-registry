"""Model Details page — delegates to the shared model_form_layout (read-only)."""

from model_registry.backend.pages.model_upload import model_form_layout


def details_model_layout(project_id: str, model_id: str, session_data=None):
    return model_form_layout("details", project_id, model_id, session_data)
