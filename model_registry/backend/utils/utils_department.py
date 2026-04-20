from dash import html
import dash_bootstrap_components as dbc

def build_table_departments(departments):
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Name"),
                html.Th("Organization"),
                html.Th("Created At"),
                html.Th("Actions")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(dept.name),
                    html.Td(org_name),  # Asegúrate de que el servicio devuelva esto
                    html.Td(dept.created_at),
                    html.Td([
                        dbc.Button(
                            "Edit",
                            id={"type": "btn-edit-dept", "index": str(dept.id)},
                            size="sm",
                            color="warning",
                            className="me-2"
                        ),
                        dbc.Button(
                            "Delete",
                            id={"type": "btn-delete-dept", "index": str(dept.id)},
                            size="sm",
                            color="danger"
                        )
                    ])
                ]) for dept, org_name in departments
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True
    )

def toast_confirm_delete_dept():
    return html.Div([
        dbc.Toast(
            id="dept-toast",
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
            dbc.ModalBody("Are you sure you want to delete this department?"),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="btn-cancel-delete", color="secondary"),
                dbc.Button("Delete", id="btn-confirm-delete", color="danger")
            ])
        ], id="delete-dept-modal", is_open=False),
    ])