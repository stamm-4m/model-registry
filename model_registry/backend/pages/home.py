import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.utils.utils_home import get_option_projects_dropdown


def home_layout():
    models_grid = dag.AgGrid(
        id="models-grid",
        columnDefs=[
            {"headerName": "Model", "field": "model_name","width": 100},
            {"headerName": "Author", "field": "authors", "width": 100},
            {"headerName": "Creation Date", "field": "creation_data", "width": 100},
            {"headerName": "Version", "field": "version", "width": 60},

            {
                "headerName": "Register to",
                "field": "register_to",
                "filter": False,
                "cellRenderer": "RegisterToRenderer",
                "dangerously_allow_unsafe_html": True,
                "width": 100
            },
            {
                "headerName": "Status",
                "field": "status",
                "cellRenderer": "StatusRenderer",
                "width": 40
            },
            {
                "headerName": "Details",
                "field": "details",
                "filter": False,
                "cellRenderer": "DetailsIconRenderer",
                "width": 40
            },
            {
                "headerName": "Edit",
                "field": "edit",
                "filter": False,
                "cellRenderer": "EditIconRenderer",
                "width": 40
            },
            {
                "headerName": "Delete",
                "field": "delete",
                "filter": False,
                "cellRenderer": "DeleteIconRenderer",
                "width": 40
            }
        ],
        rowData=[],
        defaultColDef={
            "sortable": True,
            "filter": True,
            "resizable": True
        },
        dashGridOptions={
            "rowHeight": 45,
            "getRowId": "params.data.model_id"

        },
        columnSize="responsiveSizeToFit",
    )
    projetcs_options = get_option_projects_dropdown()
    return dbc.Container(
        fluid=True,
        className="vh-100 p-4",
        children=[

            # Title
            html.H2(
                "Model Registry",
                className="text-primary text-center mb-4"
            ),

            # =========================
            # Filter bar
            # =========================
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.FormFloating([
                                dcc.Dropdown(
                                id="filter-project",
                                options=projetcs_options,
                                placeholder="Project name",
                                clearable=True,
                                value=projetcs_options[0]["value"] if projetcs_options else None,
                                ),
                                
                            ],className="mb-3"),
                        ]),                        
                    ]),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "Add Project",
                                    id="add-project",
                                    color="primary",
                                ),
                                width="auto",
                            )
                        ],
                        className="align-items-center mt-4",
                    )
                ]),
                className="mb-4 shadow-sm"
            ),

            # =========================
            # Models table
            # =========================
            dbc.Card(
                dbc.CardBody([
                    models_grid,

                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "Add Model",
                                    id="add-model",
                                    color="primary",
                                ),
                                width="auto",
                            )
                        ],
                        className="align-items-center mt-4",
                    )
                ]),
                className="shadow-lg"
            ),

            dcc.ConfirmDialog(
                id="confirm-delete-model",
                message="Are you sure you want to delete this model? This action cannot be undone."
            ),

            dcc.Store(id="model-to-delete"),

            dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Project Required")),
                dbc.ModalBody(
                    "Please select a project name before adding a new model."
                ),
                dbc.ModalFooter(
                dbc.Button(
                        "OK",
                        id="close-project-modal",
                        className="ms-auto",
                        n_clicks=0
                    )
                ),
            ],
            id="project-required-modal",
            is_open=False,
            )

        ]
    )

