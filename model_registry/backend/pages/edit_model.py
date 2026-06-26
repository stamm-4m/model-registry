"""Edit Model page — delegates to the shared model_form_layout."""

from model_registry.backend.pages.model_upload import model_form_layout


def edit_model_layout(project_id: str, model_id: str, session_data=None):
    return model_form_layout("edit", project_id, model_id, session_data)
