"""Callbacks for the Federated Learning view — basic CRUD on federations.

Add / edit via a modal, delete via a confirm dialog, and a per-federation
selector that drives the detail. After any change the list, selector and detail
are refreshed from the registry API. All service calls are defensive (never
raise); on failure the toast shows an error and the UI is left unchanged.
"""
import logging

import dash
from dash import Input, Output, State, ctx, html, no_update
from dash.exceptions import PreventUpdate

from model_registry.backend.pages import federated_learning as page
from model_registry.backend.services import federations_service as fl

logger = logging.getLogger(__name__)


def _refresh(session, select_id=None):
    feds, session = fl.list_federations(session)
    parts, session = fl.list_participants(session)
    rounds, session = fl.list_rounds(session)
    labels, session = fl.project_label_map(session)
    feds = feds or []
    parts = parts or []
    rounds = rounds or []
    page._apply_labels(parts, labels)
    fed = next((f for f in feds if str(f.get("id")) == str(select_id)),
               (feds[0] if feds else None))
    store = {"federations": feds, "participants": parts, "rounds": rounds, "live": bool(feds)}
    return (store, page.build_overview(feds, parts), page.fed_options(feds),
            page.build_detail(fed, parts, rounds), (fed.get("id") if fed else None), session)


def register_federated_learning_callbacks(app):

    @app.callback(
        Output("fl-detail", "children", allow_duplicate=True),
        Input("fl-select", "value"),
        State("fl-store", "data"),
        prevent_initial_call=True,
    )
    def _on_select(fed_id, store):
        store = store or {}
        feds = store.get("federations", [])
        parts = store.get("participants", [])
        fed = next((f for f in feds if str(f.get("id")) == str(fed_id)), None)
        return page.build_detail(fed, parts, store.get("rounds"))

    @app.callback(
        Output("fl-modal", "is_open"),
        Output("fl-modal-title", "children"),
        Output("fl-editing-id", "data"),
        Output("fl-in-name", "value"),
        Output("fl-in-slug", "value"),
        Output("fl-in-strategy", "value"),
        Output("fl-in-privacy", "value"),
        Output("fl-in-epsilon", "value"),
        Output("fl-in-rounds", "value"),
        Output("fl-in-status", "value"),
        Output("fl-modal-msg", "children"),
        Input("fl-add", "n_clicks"),
        Input("fl-edit", "n_clicks"),
        State("fl-select", "value"),
        State("fl-store", "data"),
        prevent_initial_call=True,
    )
    def _open_modal(add_c, edit_c, sel_id, store):
        trig = ctx.triggered_id
        if trig == "fl-add":
            return (True, "Add federation", None, "", "", "FedAvg", "none", None, 10, "planning", "")
        if trig == "fl-edit":
            store = store or {}
            fed = next((f for f in store.get("federations", [])
                        if str(f.get("id")) == str(sel_id)), None)
            if not fed:
                raise PreventUpdate
            pp = page._priv_params(fed)
            return (True, "Edit federation", fed.get("id"),
                    fed.get("name", ""), fed.get("slug", ""),
                    fed.get("aggregation_strategy", "FedAvg"),
                    fed.get("privacy_mechanism", "none"), pp.get("epsilon"),
                    fed.get("rounds_planned", 10), fed.get("status", "planning"), "")
        raise PreventUpdate

    @app.callback(
        Output("fl-modal", "is_open", allow_duplicate=True),
        Input("fl-modal-cancel", "n_clicks"),
        prevent_initial_call=True,
    )
    def _cancel(_):
        return False

    @app.callback(
        Output("fl-store", "data", allow_duplicate=True),
        Output("fl-overview", "children", allow_duplicate=True),
        Output("fl-select", "options", allow_duplicate=True),
        Output("fl-detail", "children", allow_duplicate=True),
        Output("fl-select", "value", allow_duplicate=True),
        Output("fl-modal", "is_open", allow_duplicate=True),
        Output("fl-modal-msg", "children", allow_duplicate=True),
        Output("fl-toast", "is_open", allow_duplicate=True),
        Output("fl-toast", "children", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("fl-modal-save", "n_clicks"),
        State("fl-in-name", "value"), State("fl-in-slug", "value"),
        State("fl-in-strategy", "value"), State("fl-in-privacy", "value"),
        State("fl-in-epsilon", "value"), State("fl-in-rounds", "value"),
        State("fl-in-status", "value"), State("fl-editing-id", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def _save(n, name, slug, strategy, privacy, eps, rounds, status, editing_id, session):
        if not n:
            raise PreventUpdate
        if not (name and slug and strategy):
            return (no_update,) * 6 + ("Name, slug and strategy are required.",
                                       no_update, no_update, no_update)
        privacy = privacy or "none"
        pp = {}
        if privacy == "differential_privacy" and eps not in (None, ""):
            try:
                pp = {"epsilon": float(eps)}
            except (TypeError, ValueError):
                pp = {}
        payload = {
            "name": name, "slug": slug, "aggregation_strategy": strategy,
            "privacy_mechanism": privacy, "privacy_params": pp,
            "rounds_planned": int(rounds) if rounds else 1,
            "status": status or "planning",
        }
        if editing_id:
            res, session = fl.update_federation(session, editing_id, payload)
        else:
            res, session = fl.create_federation(session, payload)
        if not res:
            return (no_update,) * 6 + (
                "Save failed — check permissions or a duplicate slug.",
                no_update, no_update, no_update)
        new_id = editing_id or (res.get("id") if isinstance(res, dict) else None)
        store, overview, options, detail, selid, session = _refresh(session, new_id)
        msg = f"Federation {'updated' if editing_id else 'created'}."
        return (store, overview, options, detail, selid, False, "", True, msg, session)

    @app.callback(
        Output("fl-delete-confirm", "displayed"),
        Input("fl-delete", "n_clicks"),
        prevent_initial_call=True,
    )
    def _ask_delete(n):
        if not n:
            raise PreventUpdate
        return True

    @app.callback(
        Output("fl-store", "data", allow_duplicate=True),
        Output("fl-overview", "children", allow_duplicate=True),
        Output("fl-select", "options", allow_duplicate=True),
        Output("fl-detail", "children", allow_duplicate=True),
        Output("fl-select", "value", allow_duplicate=True),
        Output("fl-toast", "is_open", allow_duplicate=True),
        Output("fl-toast", "children", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("fl-delete-confirm", "submit_n_clicks"),
        State("fl-select", "value"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def _do_delete(submit, sel_id, session):
        if not submit or not sel_id:
            raise PreventUpdate
        fl.delete_federation(session, sel_id)
        store, overview, options, detail, selid, session = _refresh(session)
        return (store, overview, options, detail, selid, True,
                "Federation deleted.", session)
