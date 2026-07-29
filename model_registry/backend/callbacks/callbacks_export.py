"""Metadata export for the ML Soft Sensors list — YAML / CSV / Excel.

Exports the metadata of all models the user can read (same payload the
registry serves and the stamm-sdk consumes), for exchanging data between labs.
YAML/CSV need no extra deps; Excel needs openpyxl (falls back to CSV if absent).
"""
import json
import logging

from dash import Input, Output, State, ctx, dcc, no_update
from dash.exceptions import PreventUpdate

from model_registry.backend.services.model_service import ModelService

logger = logging.getLogger(__name__)


def register_export_callbacks(app):
    @app.callback(
        Output("ml-export-dl", "data"),
        Input("ml-exp-yaml", "n_clicks"),
        Input("ml-exp-csv", "n_clicks"),
        Input("ml-exp-xlsx", "n_clicks"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def _export(_y, _c, _x, session):
        trig = ctx.triggered_id
        if not trig or not session:
            raise PreventUpdate
        try:
            rows, _ = ModelService().get_all_model_rows(session)
        except Exception as exc:
            logger.warning("export: could not fetch models: %s", exc)
            rows = []
        rows = rows or []

        if trig == "ml-exp-yaml":
            import yaml
            content = yaml.safe_dump(rows, sort_keys=False, allow_unicode=True) or "[]\n"
            return dict(content=content, filename="models_metadata.yaml")

        import pandas as pd
        flat = [
            {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
             for k, v in r.items()}
            for r in rows
        ]
        df = pd.DataFrame(flat)

        if trig == "ml-exp-csv":
            return dcc.send_data_frame(df.to_csv, "models_metadata.csv", index=False)

        # Excel — needs openpyxl; fall back to CSV if it's not installed
        try:
            import openpyxl  # noqa: F401
        except Exception:
            logger.info("export: openpyxl missing, sending CSV instead of xlsx")
            return dcc.send_data_frame(df.to_csv, "models_metadata.csv", index=False)
        return dcc.send_data_frame(df.to_excel, "models_metadata.xlsx",
                                   index=False, sheet_name="models")

    @app.callback(
        Output("ml-bundle-dl", "data"),
        Output("user-session", "data", allow_duplicate=True),
        Input("models-grid", "cellClicked"),
        State("models-grid-data", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def _download_bundle(event, rows, session):
        if not event or event.get("colId") != "download":
            raise PreventUpdate
        row_id = event.get("rowId")
        row = next((r for r in (rows or []) if str(r.get("model_id")) == str(row_id)), None)
        if not row or not session:
            raise PreventUpdate
        import base64
        from model_registry.backend.services.api_client import authenticated_request
        try:
            resp, session = authenticated_request(
                "GET", f"/{row['project_id']}/model_bundle/{row['model_id']}", session)
        except Exception as exc:
            logger.warning("bundle download failed: %s", exc)
            raise PreventUpdate
        if resp is None or resp.status_code != 200:
            logger.warning("bundle download HTTP %s", getattr(resp, "status_code", None))
            raise PreventUpdate
        b64 = base64.b64encode(resp.content).decode()
        return (dict(content=b64, filename=f"{row['model_id']}_bundle.zip", base64=True),
                session)
