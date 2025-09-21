# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:17:08 2025

@author: David Camilo Corrales
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import tensorflow as tf
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
import requests
import os

from model_registry import (
    load_project, 
    load_model_and_scalers, 
    list_models_by_id,
    list_projects_by_id, 
    load_project_info
)

app = FastAPI(title="Multi-Project ML API")

#R_API_URL = "http://localhost:8081/predict"

R_API_URL = os.getenv("R_API_URL", "http://localhost:8081/predict")

class PredictionRequest(BaseModel):
    req: dict   # Contains "input_data"

# ---------------- Project Metadata ----------------

@app.get("/list_projects/")
def list_projects():
    """
    List all projects with their ID and basic information from project_info.yaml.
    """
    try:
        project_map = list_projects_by_id()
        projects = []
        for project_id in project_map.keys():
            info = load_project_info(project_id)
            if not info:
                continue
            projects.append({
                "project_ID": info.get("project_ID", project_id),
                "name": info.get("project_name", project_map[project_id]),
                "description": info.get("description", ""),
                "coordinator": info.get("coordinator", ""),
                "start_date": info.get("start_date", ""),
                "end_date": info.get("end_date", "")
            })
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing projects: {e}")
        
@app.get("/{project_id}/project_info/")
def get_project_info(project_id: str):
    info = load_project_info(project_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"No info for project ID {project_id}")
    return info

@app.get("/{project_id}/db_config/")
def get_db_config(project_id: str):
    info = load_project_info(project_id)
    return info.get("db_config", {})

@app.get("/{project_id}/references/")
def get_references(project_id: str):
    info = load_project_info(project_id)
    return info.get("references", [])

@app.get("/{project_id}/variables/")
def get_variables(project_id: str):
    info = load_project_info(project_id)
    return info.get("variables", [])

# ---------------- Model Endpoints ----------------

@app.get("/{project_id}/list_models/")
def list_models_endpoint(project_id: str):
    """
    List all models in a project with both model_ID and human-readable name.
    """
    try:
        model_id_map = list_models_by_id(project_id)
        sensors = load_project(project_id)
        return [
            {
                "model_ID": model_id,
                "model_name": name,
                "metadata": sensors[model_id]["config"]["ml_model_configuration"]["model_identification"]
            }
            for model_id, name in model_id_map.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/{project_id}/metadata/{model_id}")
def get_model_metadata(project_id: str, model_id: str):
    """Return model metadata using model ID."""
    try:
        models = load_project(project_id)
        if model_id not in models:
            raise ValueError(f"Model ID '{model_id}' not found in project '{project_id}'")
        return models[model_id]["config"]["ml_model_configuration"]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------------- Prediction Endpoint ----------------

@app.post("/{project_id}/predict/{model_id}")
def predict(project_id: str, model_id: str, request: PredictionRequest):
    """
    Predict using a model identified by its ID.
    """
    try:
        model, config, input_scaler, output_scaler, outputs = load_model_and_scalers(project_id, model_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Fix: language can be list of dicts or dict
    language_info = config["ml_model_configuration"]["model_description"]["language"]
    if isinstance(language_info, list):
        lang_entry = next((item for item in language_info if "name" in item), {})
        language = lang_entry.get("name", "").lower()
    else:
        language = language_info.get("name", "").lower()

    print(f"DEBUG >> model_id={model_id}, language={language}")

    # If R model -> proxy to R FastAPI
    if language == "r":
        return _proxy_to_r_api(project_id, model_id, request)

    # Otherwise -> run Python prediction
    return _predict_logic(model, input_scaler, output_scaler, outputs, request)

# ---------------- Internal Prediction Logic ----------------

def _predict_logic(model, input_scaler, output_scaler, outputs, request: PredictionRequest):
    input_data = request.req.get("input_data", {})
    feature_names = list(input_data.keys())
    features_df = pd.DataFrame([input_data], columns=feature_names)

    # Preprocessing depending on model type
    if isinstance(model, (DecisionTreeRegressor, GradientBoostingRegressor, RandomForestRegressor)):
        scaled_features = features_df
    elif isinstance(model, SVR):
        scaled_features = input_scaler.transform(features_df)
    elif isinstance(model, tf.keras.Model):
        scaled_features = input_scaler.transform(features_df)
        scaled_features = scaled_features.reshape((scaled_features.shape[0], 1, scaled_features.shape[1]))
    else:
        raise HTTPException(status_code=400, detail="Unsupported model type")

    prediction = model.predict(scaled_features)

    # Rescale if needed
    if output_scaler is not None:
        if isinstance(model, SVR):
            prediction = output_scaler.inverse_transform(prediction.reshape(-1, 1)).ravel()
        else:
            prediction = output_scaler.inverse_transform(prediction)

    return {
        "output_model": [
            {
                "metadata": outputs,
                "prediction": prediction.tolist()
            }
        ]
    }


def _proxy_to_r_api(project_id: str, model_id: str, request: PredictionRequest):
    try:

        payload = request.dict()
        payload["project_id"] = project_id
        payload["model_id"] = model_id

        response = requests.post(R_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        r_data = response.json()

        # Ensure schema matches Python _predict_logic
        if "output_model" in r_data and len(r_data["output_model"]) > 0:
            r_output = r_data["output_model"][0]

            unified = {
                "output_model": [
                    {
                        "metadata": r_output.get("metadata", {}),
                        "prediction": r_output.get("prediction", [])
                    }
                ]
            }
            return unified

        raise HTTPException(status_code=500, detail="Invalid response from R API")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error contacting R API: {e}")

if __name__ == "__main__":
    import os
    import uvicorn

    # Read port from environment variable, default to 8000
    PORT = int(os.getenv("FASTAPI_PORT", 8000))

    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=True)
