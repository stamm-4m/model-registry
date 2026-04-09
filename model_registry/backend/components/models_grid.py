# components/models_grid.py

import dash_ag_grid as dag


def get_models_grid():
    return dag.AgGrid(
        id="models-grid",
        columnDefs=[
            {"headerName": "Model", "field": "model_name", "width": 100},
            {"headerName": "Author", "field": "authors", "width": 100},
            {"headerName": "Creation Date", "field": "creation_data", "width": 100},
            {"headerName": "Version", "field": "version", "width": 60},
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
        ],
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