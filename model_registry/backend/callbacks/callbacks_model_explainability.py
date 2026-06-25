"""Callbacks for the Model Explainability (XAI) detail view.

Drives the two interactive panels in the model-agnostic core:
  * Partial-dependence feature selector  -> xai-pdp-graph
  * Local-instance selector              -> xai-local-graph

When the explainer service computed real values, they are stashed in
`xai-model-store` (`pdp`, `shap_instances`) and the callbacks render the REAL
figure for the chosen feature / instance. Otherwise they fall back to the
deterministic placeholder builders. IDs never change.
"""
import logging

from dash import Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate

from model_registry.backend.pages.model_explainability import (
    build_pdp_fig,
    build_pdp_fig_real,
    build_local_waterfall_fig,
    build_local_waterfall_fig_real,
)

logger = logging.getLogger(__name__)


def register_model_explainability_callbacks(app):
    @app.callback(
        Output("xai-pdp-graph", "figure"),
        Input("xai-pdp-feature", "value"),
        State("xai-model-store", "data"),
        prevent_initial_call=True,
    )
    def _update_pdp(feature, store):
        if not feature or not store:
            raise PreventUpdate
        pdp = (store.get("pdp") or {})
        if feature in pdp:
            d = pdp[feature]
            return build_pdp_fig_real(feature, d["x"], d["y"])
        return build_pdp_fig(feature, store.get("seed_key", "x"))

    @app.callback(
        Output("xai-local-graph", "figure"),
        Input("xai-instance-select", "value"),
        State("xai-model-store", "data"),
        prevent_initial_call=True,
    )
    def _update_local(instance, store):
        if instance is None or not store:
            raise PreventUpdate
        inst = (store.get("shap_instances") or {})
        key = str(instance)
        if key in inst:
            d = inst[key]
            out_name = (store.get("outputs") or ["output"])[0]
            return build_local_waterfall_fig_real(
                d["pairs"], d.get("base", 0.0), d.get("pred", 0.0), out_name)
        return build_local_waterfall_fig(
            store.get("features", []), store.get("outputs", []),
            store.get("seed_key", "x"), instance)

    @app.callback(
        Output("xai-core-container", "children"),
        Output("xai-model-store", "data"),
        Output("xai-data-status", "children"),
        Input("xai-data-upload", "contents"),
        State("xai-data-upload", "filename"),
        State("xai-model-store", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def _on_data_upload(contents, filename, store, session_data):
        if not contents or not store:
            raise PreventUpdate

        def _err(msg):
            return html.Span([html.I(className="bi bi-x-circle me-1"), msg],
                             className="text-danger")

        try:
            import base64
            import io
            import pandas as pd
            _, b64 = contents.split(",", 1)
            df = pd.read_csv(io.BytesIO(base64.b64decode(b64)))
        except Exception as exc:
            return no_update, no_update, _err(f"Could not read CSV: {exc}")

        features = store.get("features") or []
        missing = [f for f in features if f not in df.columns]
        if missing:
            return no_update, no_update, _err(
                f"Missing required input column(s): {', '.join(missing)}")

        outputs = store.get("outputs") or []
        target_column = outputs[0] if (outputs and outputs[0] in df.columns) else None

        # Cap rows before shipping to the registry; send records over HTTP —
        # the API selects the model's feature columns + target and computes.
        _MAX_ROWS = 2000
        cols = features + ([target_column] if target_column else [])
        rows = df[cols].head(_MAX_ROWS).to_dict("records")

        try:
            from model_registry.backend.services import xai_service
            live = xai_service.explain_with_data(
                store.get("project_id"), store.get("model_id"),
                store.get("profile"), rows,
                target_column=target_column, session_data=session_data)
        except Exception as exc:
            return no_update, no_update, _err(f"Explainer error: {exc}")

        if not live.get("ok"):
            return no_update, no_update, _err(
                f"Could not explain on this data: {live.get('reason', 'unknown')}")

        from model_registry.backend.pages.model_explainability import _core_section
        new_core = _core_section(features, outputs, store.get("seed_key", "x"),
                                 bool(store.get("supervised", True)), live)
        new_store = {**store, "pdp": live.get("pdp"),
                     "shap_instances": live.get("shap_instances")}
        target_note = "" if target_column else " (no target column → permutation importance skipped)"
        msg = html.Span([
            html.I(className="bi bi-check-circle me-1"),
            f"Loaded {len(df)} rows from {filename}. Recomputed: "
            f"{', '.join(live.get('capabilities', [])) or 'nothing'}.{target_note}",
        ], className="text-success")
        return new_core, new_store, msg
