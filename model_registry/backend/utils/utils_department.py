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


def build_table_departments(departments):
    """FermOps-style card list for departments."""
    rows = [
        html.Div([
            html.Div([
                html.Div(dept.name, className="tree-name"),
                html.Div(f"Organization: {org_name or _DASH}", className="tree-sub"),
                html.Div(
                    f"Created {_fmt_date(dept.created_at)}" if dept.created_at else "",
                    className="tree-meta",
                ),
            ], className="tree-info"),
            html.Div([
                html.Button(
                    "Edit",
                    id={"type": "btn-edit-dept", "index": str(dept.id)},
                    className="tree-btn",
                    n_clicks=0,
                ),
                html.Button(
                    "Delete",
                    id={"type": "btn-delete-dept", "index": str(dept.id)},
                    className="tree-btn danger",
                    n_clicks=0,
                ),
            ], className="tree-actions"),
        ], className="tree-row")
        for dept, org_name in departments
    ]
    return html.Div(rows)

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