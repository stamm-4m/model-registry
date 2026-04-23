from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate

from model_registry.backend.services.laboratory_service import LaboratoryService
from model_registry.backend.services.organization_service import OrganizationService
from model_registry.backend.services.department_service import DepartmentService
import logging
logger = logging.getLogger(__name__)



def register_laboratory_modal_callbacks(app):

    @app.callback(
        Output("laboratory-modal", "is_open"),
        Input("btn-open-lab-modal", "n_clicks"),
        Input("btn-close-lab-modal", "n_clicks"),
        Input("btn-save-lab", "n_clicks"),
        State("laboratory-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_laboratory_modal(open_click, close_click, save_click, is_open):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered_id

        if trigger == "btn-open-lab-modal":
            return True

        elif trigger in ["btn-close-lab-modal", "btn-save-lab"]:
            return False

        return is_open

    @app.callback(
        Output("lab-dept-dropdown", "options"),
        Input("btn-open-lab-modal", "n_clicks"),
        Input({"type": "btn-edit-lab", "index": ALL}, "n_clicks"),
        prevent_initial_call=True 
    )
    def load_departments_dropdown(n, n_list):
        service = DepartmentService() 
        deps = service.get_department_all()
        logger.debug(f"Loaded departments for dropdown: {deps}")
        return [
            {"label": dept.name, "value": str(dept.id)}
            for dept, _ in deps
        ]

    @app.callback(
        Output("lab-name-input", "value"),
        Output("lab-location-input", "value"),
        Output("lab-dept-dropdown", "value"),
        Output("lab-edit-id", "data",allow_duplicate=True),
        Output("lab-refresh-trigger", "data", allow_duplicate=True),
        Input("btn-save-lab", "n_clicks"),
        State("lab-name-input", "value"),
        State("lab-location-input", "value"),
        State("lab-dept-dropdown", "value"),
        State("lab-edit-id", "data"), 
        prevent_initial_call=True
    )
    def save_laboratory(n, name, location, dept_id, lab_id):

        if not n:
            raise PreventUpdate 

        if not name or not location or not dept_id:
            raise PreventUpdate

        service = LaboratoryService()

        if lab_id:
            logger.debug(f"Editing laboratory with ID: {lab_id}")
            service.update_laboratory(lab_id, name, location, dept_id)
        else:
            logger.debug("Creating new laboratory")
            service.create_laboratory(name, location, dept_id)

        logger.debug(f"Saved laboratory: {name}, location: {location}, dept_id: {dept_id}")

        return "","", None, None, n
    
    @app.callback(
        Output("laboratory-modal", "is_open", allow_duplicate=True),
        Output("lab-name-input", "value", allow_duplicate=True),
        Output("lab-location-input", "value", allow_duplicate=True),
        Output("lab-dept-dropdown", "value", allow_duplicate=True),
        Output("lab-edit-id", "data"),
        Input({"type": "btn-edit-lab", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def open_edit_laboratory(n_clicks_list):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate

        lab_id = ctx.triggered_id["index"]

        service = LaboratoryService() 
        lab, dept_id = service.get_laboratory_with_dept(lab_id)
        logger.debug(f"Editing laboratory with ID: {lab_id}, name: {lab.name}, dept_id: {dept_id}")

        return True, lab.name, lab.location, str(dept_id), str(lab_id)
    
    @app.callback(
        Output("user-lab-dropdown", "options"),
        Output("user-lab-dropdown", "style"),
        Output("lab-label", "style"),
        Input("user-dept-dropdown", "value"),
    )
    def update_labs(department_id):
        if not department_id:
            return [], {"display": "none"}, {"display": "none"}

        service = LaboratoryService()
        labs = service.get_labs_by_department(department_id)

        options = [
            {"label": lab.name, "value": str(lab.id)}
            for lab in labs
        ]

        return options, {"display": "block"}, {"display": "block"}
    
    #callback to reset lab dropdown when department changes in user modal
    @app.callback(
        Output("user-lab-dropdown", "value", allow_duplicate=True),
        Input("user-dept-dropdown", "value"),
        prevent_initial_call=True
    )
    def reset_lab_dropdown(department_id):
        return None 