from dash import html, dcc
import dash_bootstrap_components as dbc


def experiment_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Create Experiment")),
        dbc.ModalBody([

            dbc.Label("Experiment Name"),
            dbc.Input(
                id="exp-name-input",
                type="text",
                placeholder="Enter experiment name"
            ),

            dbc.Label("Experiment Description", className="mt-3"),
            dbc.Textarea(
                id="exp-description-input",
                placeholder="Enter experiment description"
            )

        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-close-exp-modal"),
            dbc.Button("Save", id="btn-save-exp", color="success")
        ])
    ], id="experiment-modal", is_open=False)