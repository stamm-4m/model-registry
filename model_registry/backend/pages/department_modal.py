from dash import html, dcc
import dash_bootstrap_components as dbc


def department_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Create Department")),
        dbc.ModalBody([

            dbc.Label("Department Name"),
            dbc.Input(
                id="dept-name-input",
                type="text",
                placeholder="Enter department name"
            ),

            dbc.Label("Organization", className="mt-3"),
            dcc.Dropdown(
                id="dept-org-dropdown",
                placeholder="Select organization"
            )

        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-close-dept-modal"),
            dbc.Button("Save", id="btn-save-dept", color="success")
        ])
    ], id="department-modal", is_open=False)