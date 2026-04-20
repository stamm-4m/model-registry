from dash import html
import dash_bootstrap_components as dbc
from model_registry.api.schemas import user

def build_table_users(users):
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Name"),
                html.Th("Department"),
                html.Th("Email"),
                html.Th("Created At"),
                html.Th("Actions")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(user.full_name),
                    html.Td(dept_name),
                    html.Td(user.email),
                    html.Td(user.created_at),
                    html.Td([
                        dbc.Button(
                            "Edit",
                            id={"type": "btn-edit-user", "index": str(user.id)},
                            size="sm",
                            color="warning",
                            className="me-2"
                        ),
                        dbc.Button(
                            "Delete",
                            id={"type": "btn-delete-user", "index": str(user.id)},
                            size="sm",
                            color="danger"
                        )
                    ])
                ]) for user, dept_name in users
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True
    )

def toast_confirm_delete_user():
    return html.Div([
        dbc.Toast(
            id="user-toast",
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
            dbc.ModalBody("Are you sure you want to delete this user?"),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="btn-cancel-delete-user", color="secondary"),
                dbc.Button("Delete", id="btn-confirm-delete-user", color="danger")
            ])
        ], id="delete-user-modal", is_open=False),
    ])