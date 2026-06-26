import dash_bootstrap_components as dbc
from dash import html

_DASH = "\u2014"


def build_table_laboratories(laboratories):
    """FermOps-style card list for laboratories."""
    rows = [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(lab.name, className="tree-name"),
                        html.Div(
                            f"Department: {dept_name or _DASH}", className="tree-sub"
                        ),
                        html.Div(
                            lab.location or "",
                            className="tree-meta",
                        ),
                    ],
                    className="tree-info",
                ),
                html.Div(
                    [
                        html.Button(
                            "Edit",
                            id={"type": "btn-edit-lab", "index": str(lab.id)},
                            className="tree-btn",
                            n_clicks=0,
                        ),
                        html.Button(
                            "Delete",
                            id={"type": "btn-delete-lab", "index": str(lab.id)},
                            className="tree-btn danger",
                            n_clicks=0,
                        ),
                    ],
                    className="tree-actions",
                ),
            ],
            className="tree-row",
        )
        for lab, dept_name in laboratories
    ]
    return html.Div(rows)


def toast_confirm_delete_lab():
    return html.Div(
        [
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
                    "zIndex": 9999,
                },
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
                    dbc.ModalBody("Are you sure you want to delete this laboratory?"),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel", id="btn-cancel-delete-lab", color="secondary"
                            ),
                            dbc.Button(
                                "Delete", id="btn-confirm-delete-lab", color="danger"
                            ),
                        ]
                    ),
                ],
                id="delete-lab-modal",
                is_open=False,
            ),
        ]
    )
