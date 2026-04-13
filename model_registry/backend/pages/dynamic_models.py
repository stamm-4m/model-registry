import logging

from dash import html

logger = logging.getLogger(__name__)

def dynamic_models_layout():
    return html.Div([
        html.H1("Dynamic Models"),
        html.P("This is the Dynamic Models page.")
    ])