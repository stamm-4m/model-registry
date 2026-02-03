import logging

from model_registry.backend.config.settings import (
        MODEL2SEEK_API_TOKEN,
        MODEL2SEEK_BASE_URL,
)
from model_registry.backend.vendor.metadata_tools.fairdom_seek.model2seek import (
        model2seek,
)

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

def check_model_vars_service(
    containing_project_id: int,
    model_creators: list[int],
    model_organisms: list[int],
):
    m2s = model2seek(
        base_url=MODEL2SEEK_BASE_URL,
        token=MODEL2SEEK_API_TOKEN,
    )

    m2s.start_session()

    return m2s.check_model_vars(
        containing_project_id=containing_project_id,
        model_creators=model_creators,
        model_organisms=model_organisms,
    )

    
    
                

