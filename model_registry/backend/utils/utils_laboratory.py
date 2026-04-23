from dash import html
import dash_bootstrap_components as dbc

def build_table_laboratories(laboratories):
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Name"),
                html.Th("Department"),
                html.Th("Location"),
                html.Th("Actions")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(lab.name),
                    html.Td(dept_name),  #
                    html.Td(lab.location),
                    html.Td([
                        dbc.Button(
                            "Edit",
                            id={"type": "btn-edit-lab", "index": str(lab.id)},
                            size="sm",
                            color="warning",
                            className="me-2"
                        ),
                        dbc.Button(
                            "Delete",
                            id={"type": "btn-delete-lab", "index": str(lab.id)},
                            size="sm",
                            color="danger"
                        )
                    ])
                ]) for lab, dept_name in laboratories
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True
    )

def toast_confirm_delete_lab():
    return html.Div([
        dbc.Toast(
            id="lab-toast",
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
            dbc.ModalBody("Are you sure you want to delete this laboratory?"),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="btn-cancel-delete", color="secondary"),
                dbc.Button("Delete", id="btn-confirm-delete", color="danger")
            ])
        ], id="delete-lab-modal", is_open=False),
    ])