from model_registry.backend.vendor.metadata_tools.fairdom_seek.model2seek import model2seek
from model_registry.backend.config.settings import MODEL2SEEK_API_TOKEN,MODEL2SEEK_BASE_URL
import os
import logging
logger = logging.getLogger(__name__)

def upload_model_to_seek(
    metadata_yaml,
    model_filename,
    model_filepath,
    project_id,
    model_title,
    creators,
):
    
        m2s = model2seek(
            base_url=MODEL2SEEK_BASE_URL,
            token=MODEL2SEEK_API_TOKEN,
        )

        m2s.start_session()
        m2s.add_model(
            model_metadata_yml=metadata_yaml,
            model_filename=model_filename,
            model_filepath=model_filepath,
            containing_project_id=project_id,
            model_title=model_title,
            model_creators=creators,
        )
    
