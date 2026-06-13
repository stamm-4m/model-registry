from dash import html, dcc
import dash_bootstrap_components as dbc


def user_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Create User")),

        dbc.ModalBody([

            dbc.Label("Full Name"),
            dbc.Input(
                id="user-name-input",
                type="text",
                placeholder="Enter full name"
            ),

            dbc.Label("Email", className="mt-3"),
            dbc.Input(
                id="user-email-input",
                type="email",
                placeholder="Enter email"
            ),

            dbc.Label("Password", className="mt-3"),
            dbc.Input(
                id="user-password-input",
                type="password",
                placeholder="Enter password"
            ),

            dbc.Label("Department", className="mt-3"),
            dcc.Dropdown(
                id="user-dept-dropdown",
                placeholder="Select department"
            ),
            dbc.Label("Laboratory", className="mt-3", id="lab-label", style={"display": "none"}),
            dcc.Dropdown(
                id="user-lab-dropdown",
                placeholder="Select laboratory",
                style={"display": "none"}
            )

        ]),

        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-close-user-modal"),
            dbc.Button("Save", id="btn-save-user", color="primary")
        ])

    ], id="user-modal", is_open=False)