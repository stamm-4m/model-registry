import dash_bootstrap_components as dbc


def organization_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Create New Organization")),
        dbc.ModalBody([
            dbc.Label("Organization Name"),
            dbc.Input(
                id="org-name-input",
                type="text",
                placeholder="Enter organization name"
            ),

            dbc.Label("Location", className="mt-3"),
            dbc.Input(
                id="org-location-input",
                type="text",
                placeholder="Enter location"
            ),
        ]),
        dbc.ModalFooter([
            dbc.Button(
                "Cancel",
                id="btn-close-org-modal",
                color="secondary"
            ),
            dbc.Button(
                "Save",
                id="btn-save-org",
                color="primary"
            ),
        ])
    ],
    id="organization-modal",
    is_open=False)