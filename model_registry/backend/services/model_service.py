
from model_registry.backend.services.api_client import authenticated_request


def list_models(project_id, session_data):
    response, session_data = authenticated_request(
        "GET",
        f"{project_id}/list_models/",
        session_data
    )

    if response is None:
        return None, None 

    if response.status_code == 200:
        return response.json(), session_data

    return None, session_data    


def get_model_metadata(project_id, model_id, session_data):
    """Fetch full metadata for a single model.

    Returns ``(metadata_dict | None, session_data)``. ``None`` is returned when
    the request fails or the user is not authorized.
    """
    response, session_data = authenticated_request(
        "GET",
        f"/{project_id}/metadata/{model_id}",
        session_data,
    )

    if response is None:
        return None, None

    if response.status_code == 200:
        return response.json(), session_data

    return None, session_data


def get_model_file_info(project_id, model_id, session_data):
    """Return ``(model_file_name, model_file_relative, session_data)`` for a model.

    Wraps :func:`get_model_metadata` and extracts the file-related fields
    needed by upload callbacks. ``(None, None, session_data)`` is returned when
    the request fails or the user is not authorised.
    """
    metadata, session_data = get_model_metadata(project_id, model_id, session_data)
    if not metadata:
        return None, None, session_data

    model_identification = metadata.get("model_identification") or {}
    config_files = (
        (metadata.get("model_description") or {}).get("config_files") or {}
    )

    model_file_name = model_identification.get("ID") or ""
    model_file_relative = config_files.get("model_file") or ""
    return model_file_name, model_file_relative, session_data


def predict_dummy(X):
    # Placeholder for model inference
    return [0 for _ in range(len(X))]
