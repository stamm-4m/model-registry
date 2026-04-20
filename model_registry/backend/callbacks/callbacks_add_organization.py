from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate

from model_registry.backend.services.organization_service import OrganizationService
import logging
logger = logging.getLogger(__name__)

def register_add_organization_modal_callbacks(app):

    @app.callback(
        Output("organization-modal", "is_open"),
        Input("btn-open-org-modal", "n_clicks"),
        Input("btn-close-org-modal", "n_clicks"),
        Input("btn-save-org", "n_clicks"),
        State("organization-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_modal(open_click, close_click, save_click, is_open):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered_id

        logger.debug(f"Modal toggle triggered by: {trigger}")

        if trigger == "btn-open-org-modal":
            return True

        elif trigger in ["btn-close-org-modal", "btn-save-org"]:
            return False

        return is_open


    @app.callback(
        Output("org-name-input", "value"),
        Output("org-location-input", "value"),
        Output("org-refresh-trigger", "data"),
        Input("btn-save-org", "n_clicks"),
        State("org-name-input", "value"),
        State("org-location-input", "value"),
        State("org-edit-id", "data"),
        prevent_initial_call=True
    )
    def save_organization(n_clicks, name, location, org_id):
        logger.debug(f"Save organization triggered with name: {name}, location: {location}, ID: {org_id}")
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate
        
        if not name:
            raise PreventUpdate

        service = OrganizationService()

        if org_id:  # Edit existing organization
            logger.debug(f"Editing organization with ID: {org_id}")
            service.update_organization(org_id, name, location)
        else:  # Create new organization
            logger.debug("Creating new organization")
            service.create_organization(name, location)

        return "", "", True
    
    @app.callback(
        Output("organization-modal", "is_open", allow_duplicate=True),
        Output("org-name-input", "value", allow_duplicate=True),
        Output("org-location-input", "value", allow_duplicate=True),
        Output("org-edit-id", "data"),
        Input({"type": "btn-edit-org", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    ) 
    def open_edit_modal(n_clicks_list):
        logger.debug(f"Edit organization triggered with clicks: {n_clicks_list}")
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate
        
        if not any(n_clicks_list):
            raise PreventUpdate

        org_id = ctx.triggered_id["index"]
        service = OrganizationService()
        org = service.get_organization(org_id)

        return True, org.name, org.location, str(org_id)
    
    