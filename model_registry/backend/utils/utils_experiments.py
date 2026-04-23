from dash import html
import dash_bootstrap_components as dbc

def build_table_experiments(experiments):
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Name"),
                html.Th("Description"),
                html.Th("Created At"),
                html.Th("Actions")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(exp.name),
                    html.Td(exp.description),
                    html.Td(exp.created_at),
                    html.Td([
                        dbc.Button(
                            "Edit",
                            id={"type": "btn-edit-exp", "index": str(exp.id)},
                            size="sm",
                            color="warning",
                            className="me-2"
                        ),
                        dbc.Button(
                            "Delete",
                            id={"type": "btn-delete-exp", "index": str(exp.id)},
                            size="sm",
                            color="danger"
                        )
                    ])
                ]) for exp in experiments
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True
    )

def toast_confirm_delete_exp():
    return html.Div([
        dbc.Toast(
            id="exp-toast",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            icon="primary",
            style={
                "position": "fixed",
                "top": 10,
                "right": 10,
                "width": 350,
                "zIndex": 9999
            }
        ),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
            dbc.ModalBody("Are you sure you want to delete this experiment?"),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="btn-cancel-delete", color="secondary"),
                dbc.Button("Delete", id="btn-confirm-delete", color="danger")
            ])
        ], id="delete-exp-modal", is_open=False),
    ])