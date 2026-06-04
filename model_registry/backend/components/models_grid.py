# components/models_grid.py

import dash_ag_grid as dag

# Mapping of action column -> required permission on the "Models" resource.
# Columns whose required permission is not granted to the user are hidden.
ACTION_PERMISSIONS = {
    "register_to": "models:write",   # Register to IBISBA
    "xai":         "models:read",    # Explainability
    "details":     "models:read",    # Details
    "edit":        "models:edit",    # Edit
    "delete":      "models:edit",  # Delete
}


def _has_perm(perm, permissions):
    """Permissions=None means caller did not enforce -> show everything (back-compat)."""
    if permissions is None:
        return True
    return perm in permissions


def get_models_grid(permissions=None):
    """Build the models grid. ``permissions`` is the set of permission strings
    granted to the current user (e.g. ``{"models:read", "models:edit"}``).

    Action columns whose required permission is not granted are excluded.
    """
    base_columns = [
        {"headerName": "Model", "field": "model_name", "width": 100},
        {"headerName": "Author", "field": "authors", "width": 100},
        {"headerName": "Created on", "field": "creation_data", "width": 100},
        {"headerName": "Version", "field": "version", "width": 60},
    ]

    action_columns = [
        {
            "headerName": "Register to",
            "field": "register_to",
            "filter": False,
            "cellRenderer": "RegisterToRenderer",
            "dangerously_allow_unsafe_html": True,
            "width": 60,
        },
        {
            "headerName": "Status",
            "field": "status",
            "cellRenderer": "StatusRenderer",
            "width": 40,
        },
        {
            "headerName": "XAI",
            "field": "xai",
            "filter": False,
            "cellRenderer": "XAIRenderer",
            "dangerously_allow_unsafe_html": True,
            "width": 40,
        },
        {
            "headerName": "Details",
            "field": "details",
            "filter": False,
            "cellRenderer": "DetailsIconRenderer",
            "width": 40,
        },
        {
            "headerName": "Edit",
            "field": "edit",
            "filter": False,
            "cellRenderer": "EditIconRenderer",
            "width": 40,
        },
        {
            "headerName": "Delete",
            "field": "delete",
            "filter": False,
            "cellRenderer": "DeleteIconRenderer",
            "width": 40,
        },
    ]

    visible_actions = []
    for col in action_columns:
        required = ACTION_PERMISSIONS.get(col["field"])
        # Status has no permission gate -> always visible
        if required is None or _has_perm(required, permissions):
            visible_actions.append(col)

    return dag.AgGrid(
        id="models-grid",
        columnDefs=base_columns + visible_actions,
        rowData=[],
        defaultColDef={
            "sortable": True,
            "filter": True,
            "resizable": True,
        },
        dashGridOptions={
            "rowHeight": 45,
            "getRowId": "params.data.model_id",
        },
        columnSize="responsiveSizeToFit",
    )