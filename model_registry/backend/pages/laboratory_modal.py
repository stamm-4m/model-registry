from dash import html, dcc
import dash_bootstrap_components as dbc


def laboratory_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Create Laboratory")),
        dbc.ModalBody([

            dbc.Label("Laboratory Name"),
            dbc.Input(
                id="lab-name-input",
                type="text",
                placeholder="Enter laboratory name"
            ),

            dbc.Label("Location", className="mt-3"),
            dbc.Input(
                id="lab-location-input",
                type="text",
                placeholder="Enter laboratory location"
            ),
            
            dbc.Label("Department", className="mt-3"),
            dcc.Dropdown(
                id="lab-dept-dropdown",
                placeholder="Select department"
            )

        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-close-lab-modal"),
            dbc.Button("Save", id="btn-save-lab", color="success")
        ])
    ], id="laboratory-modal", is_open=False)