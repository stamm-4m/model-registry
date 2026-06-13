"""Callbacks for the Drift Detectors page.

CRUD is over the PACK (zip): add (upload/register), update (re-upload same
name+version), delete, activate/pin. Uploading lists the detectors found in
the pack (read-only) — it never edits the drift_detectors catalog.
"""
import base64
import json
import logging

import dash
from dash import ALL, Input, Output, State, callback_context, html, no_update
import dash_bootstrap_components as dbc

from model_registry.backend.services.api_clients.detector_packs_api_client import (
    DetectorPacksApiClient,
)

logger = logging.getLogger(__name__)

_packs = DetectorPacksApiClient()


def _kind_badge(kind):
    color = {"univariate": "info", "multivariate": "primary",
             "model_based": "warning"}.get(kind, "secondary")
    return dbc.Badge(kind or "—", color=color, className="text-uppercase")


def _packs_table(rows):
    if not rows:
        return html.Div("No packs yet. Use “Add pack” to upload a .zip package.",
                        className="text-muted fst-italic p-3")
    rows = sorted(rows, key=lambda r: (r.get("name", ""), r.get("version", "")),
                  reverse=True)
    header = html.Thead(html.Tr([html.Th(c) for c in
        ["Name", "Version", "Detectors", "Status", "Checksum", "Actions"]]))
    body = []
    for r in rows:
        pid = r.get("id")
        active = r.get("is_active")
        status = (dbc.Badge("Active", color="success") if active
                  else dbc.Badge("Inactive", color="secondary"))
        actions = [
            dbc.Button("View detectors", id={"type": "dp-view", "index": pid},
                       size="sm", color="primary", outline=True, className="me-2"),
            dbc.Button("Activate", id={"type": "dp-activate", "index": pid},
                       size="sm", color="success", outline=True,
                       disabled=bool(active), className="me-2"),
            dbc.Button("Delete", id={"type": "dp-delete", "index": pid},
                       size="sm", color="danger", outline=True),
        ]
        body.append(html.Tr([
            html.Td(r.get("name")),
            html.Td(r.get("version")),
            html.Td(dbc.Badge(f'{r.get("detector_count", 0)}', color="light",
                              text_color="dark")),
            html.Td(status),
            html.Td(html.Code((r.get("checksum") or "")[:10] or "—")),
            html.Td(actions),
        ]))
    return dbc.Table([header, html.Tbody(body)], hover=True, responsive=True,
                     striped=True, className="align-middle")


def _normalize_detectors(detectors):
    """Coerce a pack's `detectors` field into a list of dicts.

    Tolerates older rows that stored bare detector_id strings, a
    JSON-encoded string, or the current list-of-dict metadata shape.
    """
    if isinstance(detectors, str):
        try:
            detectors = json.loads(detectors)
        except Exception:
            return []
    out = []
    for d in (detectors or []):
        if isinstance(d, dict):
            out.append(d)
        elif isinstance(d, str):
            out.append({"detector_id": d, "name": d, "kind": "",
                        "description": "", "params": {}})
    return out


def _detectors_list(detectors):
    """Read-only listing of the detectors shipped in a pack."""
    detectors = _normalize_detectors(detectors)
    if not detectors:
        return html.Div("This pack lists no detectors.",
                        className="text-muted fst-italic")
    detectors = sorted(detectors, key=lambda d: (d.get("kind", ""),
                                                  d.get("detector_id", "")))
    header = html.Thead(html.Tr([html.Th(c) for c in
        ["Detector", "Kind", "Description", "Parameters"]]))
    body = []
    for d in detectors:
        desc = (d.get("description") or "")
        if len(desc) > 220:
            desc = desc[:220] + "…"
        params = d.get("params") or {}
        if isinstance(params, dict):
            pkeys = ", ".join(params.keys())
        elif isinstance(params, list):
            pkeys = ", ".join(map(str, params))
        else:
            pkeys = str(params)
        body.append(html.Tr([
            html.Td([html.Strong(d.get("name") or d.get("detector_id")),
                     html.Br(),
                     html.Small(d.get("detector_id"), className="text-muted")]),
            html.Td(_kind_badge(d.get("kind"))),
            html.Td(desc, style={"maxWidth": "420px"}),
            html.Td(html.Small(pkeys or "—")),
        ]))
    return dbc.Table([header, html.Tbody(body)], hover=True, responsive=True,
                     className="align-middle")


def register_drift_detectors_callbacks(app):

    # --- open / close upload modal
    @app.callback(
        Output("dp-upload-modal", "is_open"),
        Input("btn-open-dp-upload", "n_clicks"),
        Input("dp-upload-cancel", "n_clicks"),
        State("dp-upload-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_upload_modal(open_click, cancel_click, is_open):
        return not is_open

    # --- show selected filename
    @app.callback(
        Output("dp-upload-filename", "children"),
        Input("dp-upload", "filename"),
        prevent_initial_call=True,
    )
    def show_filename(filename):
        return f"Selected: {filename}" if filename else ""

    # --- render packs table + cache rows in a store
    @app.callback(
        Output("dp-packs-table", "children"),
        Output("dp-packs-store", "data"),
        Output("user-session", "data", allow_duplicate=True),
        Input("dp-refresh-trigger", "data"),
        State("user-session", "data"),
        prevent_initial_call="initial_duplicate",
    )
    def render_tables(_trigger, session_data):
        if not session_data or not session_data.get("authenticated"):
            return no_update, no_update, no_update
        packs, session_data = _packs.list(session_data)
        packs = packs or []
        return _packs_table(packs), packs, session_data or no_update

    # --- view detectors inside a pack (read-only)
    @app.callback(
        Output("dp-detectors-modal", "is_open"),
        Output("dp-detectors-title", "children"),
        Output("dp-detectors-body", "children"),
        Input({"type": "dp-view", "index": ALL}, "n_clicks"),
        Input("dp-detectors-close", "n_clicks"),
        State("dp-packs-store", "data"),
        prevent_initial_call=True,
    )
    def view_detectors(view_clicks, close_click, packs):
        triggered = callback_context.triggered_id
        if triggered == "dp-detectors-close":
            return False, no_update, no_update
        if not isinstance(triggered, dict) or not any(view_clicks or []):
            return no_update, no_update, no_update
        pack_id = triggered.get("index")
        pack = next((p for p in (packs or []) if p.get("id") == pack_id), None)
        if not pack:
            return no_update, no_update, no_update
        title = f'{pack.get("name")} v{pack.get("version")} — detectors'
        return True, title, _detectors_list(pack.get("detectors") or [])

    # --- register (upload) a pack
    @app.callback(
        Output("dp-upload-feedback", "children"),
        Output("dp-upload-modal", "is_open", allow_duplicate=True),
        Output("dp-refresh-trigger", "data", allow_duplicate=True),
        Output("dp-toast", "is_open", allow_duplicate=True),
        Output("dp-toast", "children", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("dp-upload-submit", "n_clicks"),
        State("dp-upload", "contents"),
        State("dp-upload", "filename"),
        State("dp-upload-name", "value"),
        State("dp-upload-notes", "value"),
        State("dp-upload-activate", "value"),
        State("dp-refresh-trigger", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def submit_register(n, contents, filename, name, notes, activate, trig, session_data):
        if not n:
            return (no_update,) * 6
        if not contents:
            return (dbc.Alert("Please choose a .zip file first.", color="warning"),
                    True, no_update, no_update, no_update, no_update)
        try:
            _header, b64 = contents.split(",", 1)
            file_bytes = base64.b64decode(b64)
        except Exception:
            return (dbc.Alert("Could not read the uploaded file.", color="danger"),
                    True, no_update, no_update, no_update, no_update)

        result, session_data = _packs.register(
            filename or "pack.zip", file_bytes, session_data,
            name=name or None, notes=notes or None, activate=bool(activate),
        )
        if not result:
            return (dbc.Alert("Upload failed (no response from API).", color="danger"),
                    True, no_update, no_update, no_update, session_data or no_update)
        if result.get("error"):
            return (dbc.Alert(f"Upload failed: {result['error']}", color="danger"),
                    True, no_update, no_update, no_update, session_data or no_update)

        pack = result.get("pack", {})
        count = result.get("detector_count", 0)
        msg = (f"Added {pack.get('name')} v{pack.get('version')} — "
               f"{count} detectors listed"
               + (" and activated." if pack.get("is_active") else "."))
        return (None, False, (trig or 0) + 1, True, msg, session_data or no_update)

    # --- activate (pin) a pack
    @app.callback(
        Output("dp-refresh-trigger", "data", allow_duplicate=True),
        Output("dp-toast", "is_open", allow_duplicate=True),
        Output("dp-toast", "children", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input({"type": "dp-activate", "index": ALL}, "n_clicks"),
        State("dp-refresh-trigger", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def activate_pack(n_clicks, trig, session_data):
        if not any(n_clicks or []):
            return (no_update,) * 4
        triggered = callback_context.triggered_id
        if not isinstance(triggered, dict):
            return (no_update,) * 4
        pack_id = triggered.get("index")
        result, session_data = _packs.activate(pack_id, session_data)
        if not result:
            return (no_update, True, "Activate failed.", session_data or no_update)
        return ((trig or 0) + 1, True, "Pack activated (deployed).",
                session_data or no_update)

    # --- delete a pack
    @app.callback(
        Output("dp-refresh-trigger", "data", allow_duplicate=True),
        Output("dp-toast", "is_open", allow_duplicate=True),
        Output("dp-toast", "children", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input({"type": "dp-delete", "index": ALL}, "n_clicks"),
        State("dp-refresh-trigger", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def delete_pack(n_clicks, trig, session_data):
        if not any(n_clicks or []):
            return (no_update,) * 4
        triggered = callback_context.triggered_id
        if not isinstance(triggered, dict):
            return (no_update,) * 4
        pack_id = triggered.get("index")
        status, session_data = _packs.delete(pack_id, session_data)
        if status not in (200, 204):
            return (no_update, True, f"Delete failed (status {status}).",
                    session_data or no_update)
        return ((trig or 0) + 1, True, "Pack deleted.", session_data or no_update)
