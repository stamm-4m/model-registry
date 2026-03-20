import dash_bootstrap_components as dbc
import flask
from dash import Dash

from model_registry.backend.callbacks import register_callbacks
from model_registry.backend.layouts.main_layout import app_layout
from model_registry.backend.models.db_init import init_db
from model_registry.backend.utils.logging_config import setup_logging

# Logging config
setup_logging()

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    dbc.icons.BOOTSTRAP,  
]

# Dash app
# Flask server
server = flask.Flask(__name__)
app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    server=server,
    suppress_callback_exceptions=True,
)
app.layout = app_layout()
register_callbacks(app)
db_initialized = False
# Initialize DB
if not db_initialized:
    init_db()
    db_initialized = True

def main():
    app.run(debug=True, host="0.0.0.0", port=8051)


# Run
if __name__ == "__main__":
    main()
