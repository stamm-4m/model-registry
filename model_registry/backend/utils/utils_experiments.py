from dash import html
import dash_bootstrap_components as dbc

_DASH = "\u2014"


def _fmt_dt(value):
    if not value:
        return _DASH
    try:
        return value.strftime("%Y-%m-%d %H:%M")
    except AttributeError:
        return str(value)[:16]


def build_table_experiments(experiments):
    """FermOps-style card list for experiments."""
    rows = [
        html.Div([
            html.Div([
                html.Div(exp.name, className="tree-name"),
                html.Div(exp.description or _DASH, className="tree-sub"),
                html.Div(
                    f"Start: {_fmt_dt(exp.start_time)} \u2022 End: {_fmt_dt(exp.end_time)}",
                    className="tree-meta",
                ),
            ], className="tree-info"),
            html.Div([
                html.Button(
                    "Edit",
                    id={"type": "btn-edit-exp", "index": str(exp.id)},
                    className="tree-btn",
                    n_clicks=0,
                ),
                html.Button(
                    "Delete",
                    id={"type": "btn-delete-exp", "index": str(exp.id)},
                    className="tree-btn danger",
                    n_clicks=0,
                ),
            ], className="tree-actions"),
        ], className="tree-row")
        for exp in experiments
    ]
    return html.Div(rows)

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