import base64
import logging
import os

import dash_bootstrap_components as dbc

from dash import dcc
from dash.exceptions import PreventUpdate
import os
from dash import ALL, Input, Output, State, ctx
from dash.exceptions import PreventUpdate

from model_registry.backend.utils.utils_details_model import (
    feature_item,
    output_item
)
from model_registry.backend.utils.utils_model_upload import get_path_config_folder

logger = logging.getLogger(__name__)

def register_details_model_callbacks(app):

    
    @app.callback(
        Output("features-accordion-details", "children"),
        Input("features-store-details", "data"),
    )
    def render_features(features):
        if not features:
            raise PreventUpdate
        return [feature_item(f) for f in features]

    @app.callback(
        Output("outputs-accordion-details", "children"),
        Input("outputs-store-details", "data"),
    )
    def render_outputs(outputs):
        if not outputs:
            return []

        return [output_item(o) for o in outputs]

    
# ---------------- download yaml ----------------#

    @app.callback(
        Output("download-feedback", "children"),
        Output("download-model-file", "data"),
        Input("download-model", "n_clicks"),
        State("edit-model-info", "data"),
        prevent_initial_call=True,
    )
    def download_yaml(n_clicks, info):

        if not info:
            raise PreventUpdate

        try:
            project_id = info["project_id"]
            model_id = info["model_id"]

            path = get_path_config_folder(project_id)
            file_path = os.path.join(path, f"{model_id}.yaml")

            if not os.path.exists(file_path):
                return (
                    dbc.Alert(
                        "❌ YAML file not found",
                        color="danger",
                        dismissable=True,
                    ),
                    None,
                )

            return (
                dbc.Alert(
                    "⬇️ Download started",
                    color="success",
                    dismissable=True,
                ),
                dcc.send_file(file_path),
            )

        except Exception as e:
            logger.exception("Download model failed")
            return (
                dbc.Alert(
                    f"❌ Unexpected error: {str(e)}",
                    color="danger",
                    dismissable=True,
                ),
                None,
            )

    