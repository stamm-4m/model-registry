import logging
from typing import Dict

from model_registry.api.utils.project_loader import (
    list_projects_by_id,
    load_project,
)

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Central registry that stores all loaded projects and models in memory.
    """

    def __init__(self):
        # Dictionary to hold loaded projects: { project_id: { model_id: { "config": ..., "model": ..., "name": ... } } }
        self.projects: Dict[str, dict] = {}

    def load_all(self):
        """
        Load all projects at application startup.
        """
        logger.info("Loading all projects into registry...")
        for project_id in list_projects_by_id().keys():
            self.load_project(project_id)

    def load_project(self, project_id: str):
        """
        Load a single project into memory.
        """
        if project_id in self.projects:
            return self.projects[project_id]

        logger.info(f"Loading project '{project_id}' into registry")
        models = load_project(project_id)
        self.projects[project_id] = models
        return models

    def get_project(self, project_id: str):
        if project_id not in self.projects:
            raise ValueError(f"Project '{project_id}' not loaded")
        return self.projects[project_id]

    def reload_project(self, project_id: str):
        """
        Force reload of a project.
        """
        logger.info(f"Reloading project '{project_id}'")
        models = load_project(project_id)
        self.projects[project_id] = models
    
    def update_model(self, project_id: str, model_id: str, updates: dict):
        """
        Update a model configuration and reload it into memory.
        """
        if project_id not in self.projects:
            raise ValueError(f"Project '{project_id}' not loaded")

        project_models = self.projects[project_id]

        if model_id not in project_models:
            raise ValueError(f"Model '{model_id}' not found in project '{project_id}'")

        model_info = project_models[model_id]

        # Actualizar config en memoria
        from model_registry.api.utils.project_loader import deep_update, save_model

        updated_config = deep_update(model_info["config"], updates)

        # Guardar YAML actualizado
        save_model(project_id, model_id, updated_config)

        # Recargar TODO el proyecto (más seguro)
        self.reload_project(project_id)

    def get_models_full(self, project_id: str):
        """Return full model info for all online models in a project."""

        project = self.get_project(project_id)
        return [
            model_data["config"]
            for model_data in project.values()
            if model_data
                .get("config", {})
                .get("ml_model_configuration", {})
                .get("model_identification", {})
                .get("status", "")
                .lower() == "online"
        ]