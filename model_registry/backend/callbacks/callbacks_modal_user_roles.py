import logging
from uuid import UUID

from dash import Output, Input,html, State, ALL
import dash
from dash.exceptions import PreventUpdate
from dash import no_update
from model_registry.backend.services.laboratory_service import LaboratoryService
from model_registry.backend.services.role_service import RoleService
from model_registry.backend.services.user_service import UserService
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
        prevent_initial_call=True
    )
    def open_roles_modal(n_clicks_list):
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
        user_roles = service.get_all_roles_by_user_id(user_id)

        options = [{"label": r.name, "value": str(r.id)} for r in roles]
        values = [str(r.role_id) for r in user_roles]

        user = service.get_user(user_id)
        lab = service_lab.get_laboratory_by_user_id(user_id)

        return True, options, values, user.full_name, user.email, lab.name, user_id

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
    
    @app.callback(
        Output("roles-modal", "is_open", allow_duplicate=True),
        Output("user-toast", "is_open"),
        Output("user-toast", "children"),
        Output("user-toast", "header"),
        Output("user-toast", "icon"),
        Input("btn-save-roles", "n_clicks"),
        State("user-roles-checklist", "value"),
        State("roles-user-id", "data"),
        prevent_initial_call=True
    )
    def save_roles(n_clicks, role_ids, user_id):

        if not n_clicks:
            raise PreventUpdate

        service = UserService()

        
        valid_role_ids = []
        for r in role_ids or []:
            try:
                valid_role_ids.append(str(r))
            except:
                continue
        logging.info(f"Assigning roles {valid_role_ids} to user {user_id}")
        service.assign_roles_to_user(user_id, valid_role_ids)

        return False, True, "Roles updated successfully!", "Success", "success"
    