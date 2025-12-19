from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware
from dash import Dash
import dash_bootstrap_components as dbc
import flask

from model_registry.backend.utils.logging_config import setup_logging
from model_registry.backend.layouts.main_layout import app_layout
from model_registry.backend.callbacks import register_callbacks
from model_registry.api.routes.ml_registry_routes import router as ml_router

# Logging config
setup_logging()

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    dbc.icons.BOOTSTRAP,  
]

# FastAPI
api = FastAPI(title="ML registry API", version="1.0.0")
api.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
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

# Mount Dash
api.mount("/", WSGIMiddleware(server))

# Include API routers
api.include_router(ml_router)


def main():
    app.run(debug=True, host="0.0.0.0", port=8050)


# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8050)
