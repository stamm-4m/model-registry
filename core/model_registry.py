# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:15:33 2025

@author: David Camilo Corrales
@email: David-Camilo.Corrales-Munoz@inrae.fr

"""

import yaml
import os
import joblib
import tensorflow as tf

# Root repo directory (parent of core/)
BASE_DIR = os.path.dirname(__file__)

# Store models per project
# soft_sensors[project_id] = { model_ID: { "config": ..., "model": ..., "name": model_name } }
soft_sensors = {}

# ---------------- Project Utilities ----------------

def list_projects_by_id():
    """Return a dict mapping project_ID to project folder names."""
    projects_dir = os.path.join(BASE_DIR, "projects")
    project_map = {}
    if not os.path.exists(projects_dir):
        return project_map

    for project_folder in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, project_folder)
        info_file = os.path.join(project_path, "project_info.yaml")
        if os.path.exists(info_file):
            with open(info_file, "r", encoding="utf-8") as f:
                info = yaml.safe_load(f)
                project_id = info.get("project_ID")
                if project_id:
                    project_map[project_id] = project_folder
    return project_map

def get_project_folder_from_id(project_id: str):
    """Return the folder name of a project given its project_ID."""
    project_map = list_projects_by_id()
    folder = project_map.get(project_id)
    if not folder:
        raise ValueError(f"Project ID '{project_id}' not found")
    return folder

def get_project_paths(project_id: str):
    """Return important directories/files for a given project_ID."""
    project_folder = get_project_folder_from_id(project_id)
    project_dir = os.path.join(BASE_DIR, "projects", project_folder)
    return {
        "CONFIG_DIR": os.path.join(project_dir, "configs"),
        "MODEL_DIR": os.path.join(project_dir, "models"),
        "PROJECT_INFO_FILE": os.path.join(project_dir, "project_info.yaml")
    }

# ---------------- Project Loading ----------------

def load_project(project_id: str):
    """Load all models and config for a given project_ID into registry using model_ID as key."""
    if project_id in soft_sensors:
        return soft_sensors[project_id]  # Already loaded

    paths = get_project_paths(project_id)
    models = {}

    if not os.path.exists(paths["CONFIG_DIR"]):
        raise FileNotFoundError(f"No configs found for project_ID {project_id}")

    for file in os.listdir(paths["CONFIG_DIR"]):
        if file.endswith(".yaml"):
            with open(os.path.join(paths["CONFIG_DIR"], file), "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                model_name = config["ml_model_configuration"]["model_identification"]["name"]
                model_id = config["ml_model_configuration"]["model_identification"].get("ID")
                if not model_id:
                    print(f"Warning: Model {model_name} has no ID, skipping.")
                    continue

                model_file = config["ml_model_configuration"]["model_description"]["config_files"]["model_file"]
                model_path = os.path.join(paths["MODEL_DIR"], model_file)

                # inside load_project(), replace the extension handling block with this:
                if os.path.exists(model_path):
                    file_ext = os.path.splitext(model_file)[-1].lower()
                
                    if file_ext in [".keras", ".h5"]:
                        model = tf.keras.models.load_model(model_path)
                    elif file_ext in [".joblib", ".pkl"]:
                        model = joblib.load(model_path)
                    elif file_ext in [".rds", ".rdata"]:   # <- R models
                        model = None  # keep metadata only
                        print(f"Info: R model {model_file} registered (metadata + REST only).")
                    else:
                        print(f"Warning: Unsupported model file format for {model_file}")
                        model = None
                
                    models[model_id] = {
                        "config": config,
                        "model": model,  # None if R
                        "name": model_name
                    }
                else:
                    print(f"Warning: Model file {model_file} not found!")


    soft_sensors[project_id] = models
    return models

# ---------------- Model and Scaler Loading ----------------

def load_model_and_scalers(project_id: str, model_id: str):
    """Loads the model and its associated scalers for a project_ID using model_ID as key."""
    models = load_project(project_id)

    if model_id not in models:
        raise ValueError(f"Model ID '{model_id}' not found in project_ID '{project_id}'")

    model_info = models[model_id]
    config = model_info["config"]
    model = model_info["model"]

    paths = get_project_paths(project_id)

    input_scaler = None
    output_scaler = None

    if "scaler" in config["ml_model_configuration"]["inputs"]:
        scaler_file = config["ml_model_configuration"]["inputs"]["scaler"]
        scaler_path = os.path.join(paths["MODEL_DIR"], scaler_file)
        if os.path.exists(scaler_path):
            input_scaler = joblib.load(scaler_path)

    if "scaler" in config["ml_model_configuration"]["outputs"]:
        scaler_file = config["ml_model_configuration"]["outputs"]["scaler"]
        scaler_path = os.path.join(paths["MODEL_DIR"], scaler_file)
        if os.path.exists(scaler_path):
            output_scaler = joblib.load(scaler_path)

    outputs = config["ml_model_configuration"]["outputs"]
    return model,config, input_scaler, output_scaler, outputs

# ---------------- Model Utilities ----------------

def get_model_name_from_id(project_id: str, model_id: str):
    """Return the human-readable model name for a given model_ID."""
    models = load_project(project_id)
    if model_id not in models:
        raise ValueError(f"Model ID '{model_id}' not found in project_ID '{project_id}'")
    return models[model_id]["name"]

def list_models_by_id(project_id: str):
    """Return dict mapping model_ID to model_name for a given project."""
    models = load_project(project_id)
    return {model_id: info["name"] for model_id, info in models.items()}

# ---------------- Project Metadata ----------------

def load_project_info(project_id: str):
    """Load project metadata for a given project_ID."""
    paths = get_project_paths(project_id)
    if os.path.exists(paths["PROJECT_INFO_FILE"]):
        with open(paths["PROJECT_INFO_FILE"], "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

# ---------------- Expose API ----------------

__all__ = [
    "list_projects_by_id",
    "get_project_folder_from_id",
    "load_project",
    "load_model_and_scalers",
    "get_model_name_from_id",
    "list_models_by_id",
    "load_project_info",
    "soft_sensors"
]
