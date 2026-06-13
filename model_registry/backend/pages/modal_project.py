from dash import html, dcc
import dash_bootstrap_components as dbc


def project_modal():
    return dbc.Modal([

        # HEADER
        dbc.ModalHeader(dbc.ModalTitle("Create Project")),

        dbc.ModalBody([

            # Basic Info
            dbc.Card([
                dbc.CardBody([

                    html.H5("Project Information", className="mb-3"),

                    dbc.Label("Project Name"),
                    dbc.Input(
                        id="proj-name-input",
                        type="text",
                        placeholder="Enter project name"
                    ),

                    dbc.Label("Project Description", className="mt-3"),
                    dbc.Textarea(
                        id="proj-description-input",
                        placeholder="Enter project description"
                    ),

                    dbc.Label("External Project ID", className="mt-3"),
                    dbc.Input(
                        id="proj-external-id",
                        type="text",
                        placeholder="Optional external ID"
                    ),
                    html.Small("Format: P0001, P0002, ...", className="text-muted"),

                ])
            ], className="mb-4"),


            # organization/department/laboratory assignment
            dbc.Card([
                dbc.CardBody([

                    html.H5("Assignment", className="mb-3"),

                    dbc.Label("Organization"),
                    dcc.Dropdown(
                        id="proj-org-dropdown",
                        placeholder="Select organization"
                    ),

                    dbc.Label("Department", className="mt-3"),
                    dcc.Dropdown(
                        id="proj-dept-dropdown",
                        placeholder="Select department",
                        disabled=True
                    ),

                    dbc.Label("Laboratory", className="mt-3"),
                    dcc.Dropdown(
                        id="proj-lab-dropdown",
                        placeholder="Select laboratory",
                        disabled=True
                    )

                ])
            ])

        ]),

        # FOOTER
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-close-proj-modal"),
            dbc.Button("Save", id="btn-save-proj", color="success")
        ])

    ], id="project-modal", is_open=False, size="lg")