"""Edit model callbacks — legacy stub.

The Add/Edit/Details pages now share model_form_layout() and the
callbacks in callbacks_model_upload.py. This file is kept so that
existing imports in __init__.py do not break.
"""

import logging

logger = logging.getLogger(__name__)


def register_edit_model_callbacks(app):
    """No-op: all edit logic is handled by register_model_upload_callbacks."""
    pass
