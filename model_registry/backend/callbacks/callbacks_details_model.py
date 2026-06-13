"""Details model callbacks — legacy stub.

Details page now uses the shared model_form_layout() (details mode).
Inputs/outputs are pre-populated via the Store; no extra callbacks needed.
"""
import logging

logger = logging.getLogger(__name__)


def register_details_model_callbacks(app):
    """No-op: details page uses shared form layout with disabled inputs."""
    pass
