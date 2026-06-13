import logging
from uuid import UUID

from dash import Output, Input,html, State, ALL
import dash
from dash.exceptions import PreventUpdate
from dash import no_update
from model_registry.backend.services.laboratory_service import LaboratoryService
from model_registry.backend.services.role_service import RoleService
from model_registry.backend.services.user_service import UserService
from model_registry.backend.services.project_service import ProjectService
from model_registry.backend.services.soft_sensors_service import SoftSensorsService
from model_registry.backend.services.project_soft_sensors_service import ProjectSoftSensorsService
logger = logging.getLogger(__name__)

def register_user_modal_role_callbacks(app):

    @app.callback(
        Output("roles-modal", "is_open"),
        Output("user-roles-checklist", "options"),
        Output("user-roles-checklist", "value"),
        Output("roles-user-name", "children"),
        Output("roles-user-email", "children"),
        Output("roles-user-laboratory", "children"),
        Output("roles-user-id", "data"),
        Input({"type": "btn-manage-roles", "index": ALL}, "n_clicks"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def open_roles_modal(n_clicks_list, session_data):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate


        user_id = ctx.triggered[0]["prop_id"].split(".")[0]
        user_id = eval(user_id)["index"]

        service = UserService()
        service_role = RoleService()
        service_lab = LaboratoryService()
        roles = service_role.get_all_roles()
        user_roles, _ = service.get_all_roles_by_user_id(session_data, user_id)

        options = [{"label": r.name, "value": str(r.id)} for r in roles]
        # Solo roles generales (resource_type is None)
        values = [str(r.role_id) for r in user_roles if getattr(r, 'permission_id', None) is None]

        user, _ = service.get_user(session_data, user_id)
        lab, _ = service_lab.get_laboratory_by_user_id(session_data, user_id) 
        if lab:
            lab_name = lab.name
        else:
            lab_name = "No laboratory"
        return True, options, values, user.full_name, user.email, lab_name, user_id

    @app.callback(
        Output("role-permissions-view", "children"),
        Input("user-roles-checklist", "value")
    )
    def show_permissions(role_ids):
        if not role_ids:
            return "No permissions"

        service = RoleService()
        permissions = service.get_permissions_by_role_ids(role_ids)

        return html.Ul([
            html.Li(p.description) for p in permissions
        ])
    
    @app.callback(
        Output("roles-modal", "is_open", allow_duplicate=True),
        Input("btn-close-roles-modal", "n_clicks"),
        prevent_initial_call=True
    )
    def close_roles_modal(n_clicks):
        return False
    

    # Callback to load projects into the dropdown
    @app.callback(
        Output("user-projects-dropdown", "options"),
        Input("roles-user-id", "data"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def load_projects(user_id, session_data):
        # You can filter projects by user if needed, here we load all
        service = ProjectService()
        projects, _ = service.get_all_projects(session_data)
        return [{"label": p.name, "value": str(p.id)} for p in projects]

    # Callback to load models (soft sensors) for the selected project
    @app.callback(
        Output("user-models-dropdown", "options"),
        Input("user-projects-dropdown", "value"),
        prevent_initial_call=True
    )
    def load_models(project_id):
        if not project_id:
            return []
        soft_sensor_service = SoftSensorsService()
        models = soft_sensor_service.get_by_project(project_id)
        # Display path_model or path_metadata as label
        return [{"label": m.path_model, "value": str(m.id)} for m in models]

    # Callback to load available 'models' roles for the selected model and user
    @app.callback(
        Output("user-models-permissions-checklist", "options"),
        Output("user-models-permissions-checklist", "value"),
        Input("user-models-dropdown", "value"),
        State("roles-user-id", "data"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def load_model_roles(model_id, user_id, session_data):
        if not model_id or not user_id:
            return [], []
        role_service = RoleService()
        user_service = UserService()

        # Show 'model' permissions in the checklist (values are permission IDs).
        all_roles = role_service.get_all_roles()
        permissions = role_service.get_permissions_by_role_ids(
            role_ids=[str(r.id) for r in all_roles]
        )
        # Deduplicate permissions by id (a permission can be granted by several roles)
        seen = set()
        model_permissions = []
        for p in permissions:
            if 'model' in (p.name or '').lower() and p.id not in seen:
                seen.add(p.id)
                model_permissions.append(p)
        options = [{"label": p.name, "value": str(p.id)} for p in model_permissions]

        # Get roles already assigned to this user for this model, then translate
        # them back to permission IDs so they can be pre-checked in the UI.
        
        user_roles, _ = user_service.get_all_roles_by_user_id(session_data, user_id)
        logger.debug(f"[callback] user_roles crudos: {[(ur.user_id, ur.role_id, ur.permission_id, ur.real_resource_id) for ur in user_roles]}")
        
        permission_ids = [
            str(r.permission_id)
            for r in user_roles
            if getattr(r, 'permission_id', None) is not None and str(getattr(r, 'real_resource_id', None)) == str(model_id)
        ]


        assigned_permission_ids = set()
        
        perms = role_service.get_permissions_by_ids(permission_ids)
        logger.info(f"Permisos para model_id {model_id}: {[str(p.id) for p in perms]}")
        for p in perms:
            if 'model' in (p.name or '').lower():
                assigned_permission_ids.add(str(p.id))
        logger.info(f"[load_model_roles] assigned_permission_ids: {list(assigned_permission_ids)}")
        return options, list(assigned_permission_ids)

    # Callback para guardar roles generales y de modelos al presionar guardar
    @app.callback(
        Output("roles-modal", "is_open", allow_duplicate=True),
        Output("user-toast", "is_open", allow_duplicate=True),
        Output("user-toast", "children", allow_duplicate=True),
        Output("user-toast", "header", allow_duplicate=True),
        Output("user-toast", "icon", allow_duplicate=True),
        Input("btn-save-roles", "n_clicks"),
        State("user-roles-checklist", "value"),
        State("roles-user-id", "data"),
        State("user-models-dropdown", "value"),
        State("user-models-permissions-checklist", "value"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def save_roles_and_model_roles(n_clicks, role_ids, user_id, model_id, model_permission_ids, session_data):
        if not n_clicks:
            raise PreventUpdate
        service = UserService()
        # Asignar solo los roles seleccionados (generales)
        selected_role_ids = [str(r) for r in (role_ids or [])]
        logging.info(f"Assigning roles {selected_role_ids} to user {user_id}")
        service.assign_user_roles(session_data, user_id, selected_role_ids)

        # Save model-specific roles only if a model is selected
        if model_id:
            valid_model_permission_ids = [str(r) for r in (model_permission_ids or [])]
            logging.info(
                f"Assigning model permissions {valid_model_permission_ids} "
                f"to user {user_id} for model {model_id}"
            )
            # Asignar permisos sobre el modelo usando los roles generales del usuario
            service.assign_user_model_permissions(session_data, user_id, selected_role_ids, valid_model_permission_ids, model_id)

        # Close modal and show success toast
        return False, True, "Roles updated successfully!", "Success", "success"
