"""Callbacks for the Dynamic Models view — CRUD on dynamic_model rows.

Grid-driven (ML Soft Sensors style): the ag-grid Details / Edit / Delete icon
columns fire ``dm-grid.cellClicked``; we route by ``colId``. **Details opens a
separate page** (route ``/dynamic-model-details/<id>``) via the URL — it is NOT
shown inline under the list. Add via the header button; create/edit go through a
modal (core fields + a JSON metadata blob); delete goes through a confirm dialog.
After any change the grid rowData refreshes from the API. Defensive: service
calls never raise.
"""
import json
import logging

from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from model_registry.backend.pages import dynamic_models as page
from model_registry.backend.services import dynamic_models_service as dms

logger = logging.getLogger(__name__)


def _refresh(session, select_id=None):
    """Reload models from the API; return (store, rowData, session)."""
    models, session = dms.list_dynamic_models(session)
    models = models or []
    store = {"models": models, "live": bool(models)}
    return store, page.grid_rows(models), session


def register_dynamic_models_callbacks(app):

    # ---- grid clicks: details (navigate) / edit / delete ----------------
    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("dm-modal", "is_open", allow_duplicate=True),
        Output("dm-modal-title", "children", allow_duplicate=True),
        Output("dm-editing-id", "data", allow_duplicate=True),
        Output("dm-in-name", "value", allow_duplicate=True),
        Output("dm-in-version", "value", allow_duplicate=True),
        Output("dm-in-type", "value", allow_duplicate=True),
        Output("dm-in-process", "value", allow_duplicate=True),
        Output("dm-in-status", "value", allow_duplicate=True),
        Output("dm-in-endpoint", "value", allow_duplicate=True),
        Output("dm-in-info", "value", allow_duplicate=True),
        Output("dm-modal-msg", "children", allow_duplicate=True),
        Output("dm-delete-id", "data", allow_duplicate=True),
        Output("dm-delete-confirm", "displayed", allow_duplicate=True),
        Input("dm-grid", "cellClicked"),
        State("dm-store", "data"),
        prevent_initial_call=True,
    )
    def _on_grid_click(event, store):
        if not event:
            raise PreventUpdate
        col = event.get("colId")
        rid = event.get("rowId")
        if not rid or col not in ("details", "edit", "delete"):
            raise PreventUpdate
        m = next((x for x in (store or {}).get("models", [])
                  if str(x.get("id")) == str(rid)), None)
        if not m:
            raise PreventUpdate

        if col == "details":
            return (f"/dynamic-model-details/{m.get('id')}", no_update, no_update,
                    no_update, no_update, no_update, no_update, no_update,
                    no_update, no_update, no_update, no_update, no_update, no_update)

        if col == "edit":
            info = page._info(m)
            rest = {k: v for k, v in info.items()
                    if k not in ("type", "process", "status")}
            return (no_update, True, "Edit dynamic model", m.get("id"),
                    m.get("name", ""), m.get("version", "1.0"),
                    info.get("type", "unstructured kinetic"),
                    info.get("process", ""), info.get("status", "draft"),
                    m.get("url_endpoint") or "", json.dumps(rest, indent=2),
                    "", no_update, no_update)

        # delete
        return (no_update, no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update, no_update,
                m.get("id"), True)

    # ---- add button -----------------------------------------------------
    @app.callback(
        Output("dm-modal", "is_open", allow_duplicate=True),
        Output("dm-modal-title", "children", allow_duplicate=True),
        Output("dm-editing-id", "data", allow_duplicate=True),
        Output("dm-in-name", "value", allow_duplicate=True),
        Output("dm-in-version", "value", allow_duplicate=True),
        Output("dm-in-type", "value", allow_duplicate=True),
        Output("dm-in-process", "value", allow_duplicate=True),
        Output("dm-in-status", "value", allow_duplicate=True),
        Output("dm-in-endpoint", "value", allow_duplicate=True),
        Output("dm-in-info", "value", allow_duplicate=True),
        Output("dm-modal-msg", "children", allow_duplicate=True),
        Input("dm-add", "n_clicks"),
        prevent_initial_call=True,
    )
    def _open_add(n):
        if not n:
            raise PreventUpdate
        return (True, "Add dynamic model", None, "", "1.0",
                "unstructured kinetic", "", "draft", "",
                page._METADATA_TEMPLATE, "")

    @app.callback(
        Output("dm-modal", "is_open", allow_duplicate=True),
        Input("dm-modal-cancel", "n_clicks"),
        prevent_initial_call=True,
    )
    def _cancel(_):
        return False

    # ---- save (create / update) ----------------------------------------
    @app.callback(
        Output("dm-store", "data", allow_duplicate=True),
        Output("dm-grid", "rowData", allow_duplicate=True),
        Output("dm-modal", "is_open", allow_duplicate=True),
        Output("dm-modal-msg", "children", allow_duplicate=True),
        Output("dm-toast", "is_open", allow_duplicate=True),
        Output("dm-toast", "children", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("dm-modal-save", "n_clicks"),
        State("dm-in-name", "value"), State("dm-in-version", "value"),
        State("dm-in-type", "value"), State("dm-in-process", "value"),
        State("dm-in-status", "value"), State("dm-in-endpoint", "value"),
        State("dm-in-info", "value"), State("dm-editing-id", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def _save(n, name, version, mtype, process, status, endpoint, info_text,
              editing_id, session):
        if not n:
            raise PreventUpdate
        if not name:
            return (no_update, no_update, no_update, "Name is required.",
                    no_update, no_update, no_update)
        info = {}
        if info_text and info_text.strip():
            try:
                info = json.loads(info_text)
                if not isinstance(info, dict):
                    raise ValueError("must be a JSON object")
            except Exception as exc:
                return (no_update, no_update, no_update,
                        f"Invalid metadata JSON: {exc}", no_update, no_update,
                        no_update)
        info["type"] = mtype or "unstructured"
        info["process"] = process or ""
        info["status"] = status or "draft"
        payload = {"name": name, "version": version or "1.0",
                   "url_endpoint": (endpoint or None), "information": info}
        if editing_id:
            res, session = dms.update_dynamic_model(session, editing_id, payload)
        else:
            res, session = dms.create_dynamic_model(session, payload)
        if not res:
            return (no_update, no_update, no_update,
                    "Save failed — check permissions / the API.",
                    no_update, no_update, no_update)
        store, rows, session = _refresh(session)
        msg = f"Dynamic model {'updated' if editing_id else 'created'}."
        return (store, rows, False, "", True, msg, session)

    # ---- delete ---------------------------------------------------------
    @app.callback(
        Output("dm-store", "data", allow_duplicate=True),
        Output("dm-grid", "rowData", allow_duplicate=True),
        Output("dm-toast", "is_open", allow_duplicate=True),
        Output("dm-toast", "children", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("dm-delete-confirm", "submit_n_clicks"),
        State("dm-delete-id", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def _do_delete(submit, del_id, session):
        if not submit or not del_id:
            raise PreventUpdate
        dms.delete_dynamic_model(session, del_id)
        store, rows, session = _refresh(session)
        return (store, rows, True, "Dynamic model deleted.", session)
