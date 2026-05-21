from dash import html
import dash_bootstrap_components as dbc

_DASH = "\u2014"


def _fmt_date(value):
    if not value:
        return ""
    try:
        return value.strftime("%Y-%m-%d")
    except AttributeError:
        return str(value)[:10]


def build_table(organizations):
    """FermOps-style card list for organizations.

    Each card shows name (bold), location (sub), and created date (meta).
    Edit/Delete buttons keep the exact pattern-matching IDs the existing
    callbacks listen on.
    """
    rows = [
        html.Div([
            html.Div([
                html.Div(org.name, className="tree-name"),
                html.Div(org.location or _DASH, className="tree-sub"),
                html.Div(
                    f"Created {_fmt_date(org.created_at)}" if org.created_at else "",
                    className="tree-meta",
                ),
            ], className="tree-info"),
            html.Div([
                html.Button(
                    "Edit",
                    id={"type": "btn-edit-org", "index": str(org.id)},
                    className="tree-btn",
                    n_clicks=0,
                ),
                html.Button(
                    "Delete",
                    id={"type": "btn-delete-org", "index": str(org.id)},
                    className="tree-btn danger",
                    n_clicks=0,
                ),
            ], className="tree-actions"),
        ], className="tree-row")
        for org in organizations
    ]
    return html.Div(rows)
    return html.Div(rows)

def toast_confirm_delete():
    return html.Div([
        dbc.Toast(
            id="org-toast",
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
            dbc.ModalBody("Are you sure you want to delete this organization?"),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="btn-cancel-delete", color="secondary"),
                dbc.Button("Delete", id="btn-confirm-delete", color="danger")
            ])
        ], id="delete-org-modal", is_open=False),
    ])