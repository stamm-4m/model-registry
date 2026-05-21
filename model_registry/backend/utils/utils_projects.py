import os
import yaml 
from dash import html
import dash_bootstrap_components as dbc
from collections import OrderedDict


def create_project_structure(project_id: str, project_name: str, description: str):
    """
    Create the folder structure and project_info.yaml for a new project.
    """
    base_dir = os.path.join(os.path.dirname(__file__), '../../api/projects')
    project_folder = os.path.join(base_dir, project_name)
    config_folder = os.path.join(project_folder, 'configs')
    models_folder = os.path.join(project_folder, 'models')
    os.makedirs(config_folder, exist_ok=True)
    os.makedirs(models_folder, exist_ok=True)
    yaml_path = os.path.join(project_folder, 'project_info.yaml')
    project_info = OrderedDict([
        ('project_ID', project_id),
        ('project_name', project_name),
        ('description', description)
    ])
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(project_info, f, allow_unicode=True, sort_keys=False)

_DASH = "\u2014"


def _fmt_date(value):
    if not value:
        return ""
    try:
        return value.strftime("%Y-%m-%d")
    except AttributeError:
        return str(value)[:10]


def build_table_projects(projects):
    """FermOps-style card list for projects.

    Edit/Delete IDs preserved so existing callbacks keep working.
    """
    rows = [
        html.Div([
            html.Div([
                html.Div(proj.name, className="tree-name"),
                html.Div(
                    f"ID: {proj.project_id or _DASH}",
                    className="tree-sub",
                ),
                html.Div(
                    proj.description or "",
                    className="tree-sub",
                    style={"whiteSpace": "normal", "marginTop": "2px"},
                ),
                html.Div(
                    f"Created {_fmt_date(proj.created_at)}" if proj.created_at else "",
                    className="tree-meta",
                ),
            ], className="tree-info"),
            html.Div([
                html.Button(
                    "Edit",
                    id={"type": "btn-edit-proj", "index": str(proj.id)},
                    className="tree-btn",
                    n_clicks=0,
                ),
                html.Button(
                    "Delete",
                    id={"type": "btn-delete-proj", "index": str(proj.id)},
                    className="tree-btn danger",
                    n_clicks=0,
                ),
            ], className="tree-actions"),
        ], className="tree-row")
        for proj in projects
    ]
    return html.Div(rows)

def toast_confirm_delete_proj():
    return html.Div([
        dbc.Toast(
            id="proj-toast",
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
            dbc.ModalBody("Are you sure you want to delete this project?"),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="btn-cancel-delete_project", color="secondary"),
                dbc.Button("Delete", id="btn-confirm-delete_project", color="danger")
            ])
        ], id="delete-proj-modal", is_open=False),
    ])