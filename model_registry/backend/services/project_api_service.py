from model_registry.backend.services.api_client import authenticated_request


def list_projects(session_data):
    response, session_data = authenticated_request(
        "GET",
        "/list_projects/",
        session_data
    )

    if response is None:
        return None, None 

    if response.status_code == 200:
        return response.json(), session_data

    return None, session_data