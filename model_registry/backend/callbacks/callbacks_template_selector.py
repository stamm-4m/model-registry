"""Callbacks for template selection and configuration in model upload."""

import json
import logging
from dash import Input, Output, State, html, ALL
import dash_bootstrap_components as dbc
from model_registry.backend.utils.utils_template_ui import (
    get_template_fields_by_algorithm,
    STAMM_ALGORITHMS,
)


logger = logging.getLogger(__name__)

# Pattern-matching type used for all rendered hyperparameter inputs.
# Each input gets id={"type": "template-field", "index": <field_id>}
_TEMPLATE_FIELD_TYPE = "template-field"


def register_template_callbacks(app):
    """Register all template-related callbacks."""

    # Callback: Show/hide and populate template config fields
    @app.callback(
        Output("template-config-container", "style"),
        Output("template-config-fields", "children"),
        Output("template-config-store", "data"),
        Input("template-algorithm-selector", "value"),
        prevent_initial_call=True,
    )
    def update_template_fields(selected_algorithm):
        """Update template fields based on selected algorithm."""
        if not selected_algorithm:
            return (
                {"display": "none"},
                html.P("Select an algorithm to see template-specific fields.", 
                       className="text-muted"),
                {}
            )

        # Get template fields for this algorithm
        fields = get_template_fields_by_algorithm(selected_algorithm)
        if not fields:
            return (
                {"display": "none"},
                html.P(f"No template fields defined for {selected_algorithm}.", 
                       className="text-muted"),
                {}
            )

        # Build field components
        field_components = []
        field_data = {"algorithm": selected_algorithm, "fields": {}}

        for field in fields:
            field_id = field.get("id")
            field_type = field.get("type", "number")
            field_name = field.get("name", "")
            field_value = field.get("value")
            field_required = field.get("required", False)
            field_placeholder = field.get("placeholder", "")

            # Store field metadata
            field_data["fields"][field_id] = {
                "name": field_name,
                "type": field_type,
                "required": field_required,
                "default_value": field_value,
            }

            # Pattern-matching ID — collected as a group at save time via ALL.
            pm_id = {"type": _TEMPLATE_FIELD_TYPE, "index": field_id}

            # Create appropriate input component
            if field_type == "checkbox":
                component = html.Div(
                    [
                        dbc.Checkbox(
                            id=pm_id,
                            value=field_value or False,
                            className="me-2",
                        ),
                        html.Label(field_name),
                    ],
                    className="d-flex align-items-center mb-3",
                )
            elif field_type == "textarea":
                component = dbc.FormFloating([
                    dbc.Textarea(
                        id=pm_id,
                        placeholder=field_placeholder or field_name,
                        style=field.get("style", {}),
                        value=field_value or "",
                    ),
                    dbc.Label(field_name),
                ], className="mb-3")
            else:
                # Number, text, etc.
                input_props = {
                    "id": pm_id,
                    "type": field_type,
                    "placeholder": field_placeholder or field_name,
                    "value": field_value or "",
                }
                if "step" in field:
                    input_props["step"] = field["step"]
                if "min" in field:
                    input_props["min"] = field["min"]
                if "max" in field:
                    input_props["max"] = field["max"]

                component = dbc.FormFloating([
                    dbc.Input(**input_props),
                    dbc.Label(field_name),
                ], className="mb-3")

            # Add required marker if needed
            if field_required:
                field_components.append(
                    html.Div([
                        component,
                        html.Small(
                            "* Required field",
                            className="text-danger ms-2 d-block"
                        )
                    ])
                )
            else:
                field_components.append(component)

        return (
            {"display": "block"},
            field_components,
            field_data,
        )

    # Callback: Collect template values before save (triggered by save button).
    # Uses pattern-matching ALL so only currently-rendered fields are read —
    # no references to non-existent component IDs.
    @app.callback(
        Output("template-config-store", "data", allow_duplicate=True),
        Input("save-ml-model-config", "n_clicks"),
        State("template-algorithm-selector", "value"),
        State("template-config-store", "data"),
        State({"type": _TEMPLATE_FIELD_TYPE, "index": ALL}, "value"),
        State({"type": _TEMPLATE_FIELD_TYPE, "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def collect_template_config(n_clicks, selected_algorithm, current_store, field_values, field_ids):
        """Collect currently-rendered template field values into the store."""
        if not selected_algorithm:
            return current_store or {}

        # Build {field_id_string: value} from the pattern-matched lists
        field_value_map = {
            fid["index"]: val
            for fid, val in zip(field_ids, field_values)
        }

        fields = get_template_fields_by_algorithm(selected_algorithm)
        config = {
            "algorithm": selected_algorithm,
            "fields": {},
            "values": {},
        }

        for field in fields:
            field_id   = field.get("id")
            field_name = field.get("name", "")
            field_type = field.get("type", "number")
            field_val  = field_value_map.get(field_id)

            config["fields"][field_id] = {
                "name":     field_name,
                "type":     field_type,
                "required": field.get("required", False),
            }
            config["values"][field_id] = field_val
            logger.debug("Collected %s = %s (%s)", field_id, field_val, field_type)

        store = dict(current_store or {})
        store["config"] = config
        logger.info("Template config collected for %s: %s", selected_algorithm, config["values"])
        return store

    # Callback: Reset template config when algorithm is cleared
    @app.callback(
        Output("template-config-store", "data", allow_duplicate=True),
        Input("template-algorithm-selector", "value"),
        State("template-config-store", "data"),
        prevent_initial_call=True,
    )
    def reset_template_on_clear(selected_algorithm, current_store):
        """Clear template config when no algorithm is selected."""
        if not selected_algorithm:
            return {}
        return current_store

