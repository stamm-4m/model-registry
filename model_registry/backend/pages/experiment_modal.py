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

            dbc.Label("Project", className="mt-3"),
            dcc.Dropdown(
                id="exp-project-dropdown",
                placeholder="Select project"
            ),

            dbc.Label("Experiment Description", className="mt-3"),
            dbc.Textarea(
                id="exp-description-input",
                placeholder="Enter experiment description"
            ),

            dbc.Label("Initial Conditions (JSON)", className="mt-3"),
            dbc.Textarea(
                id="exp-initial-conditions-input",
                placeholder='{"temp": 37, "ph": 7.0}'
            ),

            dbc.Label("Set Points (JSON)", className="mt-3"),
            dbc.Textarea(
                id="exp-set-points-input",
                placeholder='{"temp": 30, "ph": 6.5}'
            ),

            dbc.Label("Start Time", className="mt-3"),
            dbc.InputGroup([
                dbc.InputGroupText(
                    html.I(className="bi bi-calendar-date"),
                    style={"backgroundColor": "#f8f9fa"}
                ),
                dbc.Input(
                    id="exp-start-time-input",
                    type="text",
                    placeholder="YYYY-MM-DD HH:MM:SS",
                    style={"borderLeft": 0}
                ),
            ], className="mb-2"),

            dbc.Label("End Time", className="mt-3"),
            dbc.InputGroup([
                dbc.InputGroupText(
                    html.I(className="bi bi-calendar-date"),
                    style={"backgroundColor": "#f8f9fa"}
                ),
                dbc.Input(
                    id="exp-end-time-input",
                    type="text",
                    placeholder="YYYY-MM-DD HH:MM:SS",
                    style={"borderLeft": 0}
                ),
            ]),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-close-exp-modal"),
            dbc.Button("Save", id="btn-save-exp", color="success")
        ])
    ], id="experiment-modal", is_open=False, size="xl", centered=True)
