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

def build_table_projects(projects):
    """
    Build a Dash Bootstrap Components table for displaying projects.

    Args:
        projects (list): List of project objects.

    Returns:
        dbc.Table: A Dash Bootstrap Components table.
    """
    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Name"),
                html.Th("Project ID"),
                html.Th("Description"),
                html.Th("Created At"),
                html.Th("Actions")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(proj.name),
                    html.Td(proj.project_id),
                    html.Td(proj.description),
                    html.Td(proj.created_at),
                    html.Td([
                        dbc.Button(
                            "Edit",
                            id={"type": "btn-edit-proj", "index": str(proj.id)},
                            size="sm",
                            color="warning",
                            className="me-2"
                        ),
                        dbc.Button(
                            "Delete",
                            id={"type": "btn-delete-proj", "index": str(proj.id)},
                            size="sm",
                            color="danger"
                        )
                    ])
                ]) for proj in projects
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True
    )

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