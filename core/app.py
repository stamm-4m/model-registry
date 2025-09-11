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

from model_registry import (
    load_project, 
    load_model_and_scalers, 
    load_project_info,
    get_model_name_from_id,
    list_models_by_id
)

app = FastAPI(title="Multi-Project ML API")

class PredictionRequest(BaseModel):
    req: dict   # Contains "input_data"

# ---------------- Project Metadata ----------------

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
        model, input_scaler, output_scaler, outputs = load_model_and_scalers(project_id, model_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
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

if __name__ == "__main__":
    import os
    import uvicorn

    # Read port from environment variable, default to 8000
    PORT = int(os.getenv("FASTAPI_PORT", 8000))

    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=True)
