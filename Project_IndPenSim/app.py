# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:17:08 2025

@author: David Camilo Corrales
@email: David-Camilo.Corrales-Munoz@inrae.fr

"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
import pandas as pd
import requests
import tensorflow as tf
from model_registry import predict, soft_sensors, load_model_and_scalers, load_project_info

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

app = FastAPI()

# Define request format
class PredictionRequest(BaseModel):
    model: str  # Model name (e.g., "CUBIST")
    req: dict   # Contains "input_data"



@app.get("/project_info/")
def get_project_info():
    """Returns metadata about the ML project from project_info.yaml"""
    info = load_project_info()
    if not info:
        raise HTTPException(status_code=404, detail="Project information not available.")
    return info
        

@app.get("/metadata/{model_name}")
def get_soft_sensor(model_name: str):
    """Returns details for a specific soft sensor."""
    if model_name not in soft_sensors:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model_config = soft_sensors[model_name]["config"]["ml_model_configuration"]
    
    return {
        "name": model_name,
        "model_identification": model_config["model_identification"],
        "model_description": model_config["model_description"],
        "training_information": model_config.get("training_information", {}),
        "input_features": [feature["name"] for feature in model_config["inputs"]["features"]],
        "output_features": [output["name"] for output in model_config["outputs"]["predictions"]]
    }

@app.get("/list_models/")
def list_available_soft_sensors():
    """Returns a list of available soft sensors with full metadata."""
    return {
        "available_soft_sensors": [
            {
                "name": model_name,
                "model_identification": soft_sensors[model_name]["config"]["ml_model_configuration"]["model_identification"]
            }
            for model_name in soft_sensors
        ]
    }


@app.post("/predict/")
def get_prediction(request: PredictionRequest):
    """Endpoint for making predictions with structured response."""
    model_name = request.model
    input_data = request.req.get("input_data", {})  # Get feature dictionary from request

    if model_name not in soft_sensors:
        raise HTTPException(status_code=404, detail="Model not found")

    model, input_scaler, output_scaler = load_model_and_scalers(model_name)

    # Extract feature names in the order they appear in the request
    feature_names = list(input_data.keys())

    # Convert input data into a Pandas DataFrame to preserve order
    features_df = pd.DataFrame([input_data], columns=feature_names)

    # Handle CART , Random Forest and GBM models
    if isinstance(model, (DecisionTreeRegressor, GradientBoostingRegressor, RandomForestRegressor)): 
        scaled_features = features_df  # Use raw input in the correct order
    
    print(f"INPUT SCALER: {input_scaler}")

    
    # Handle LSTM models    
    if isinstance(model, SVR): 
        scaled_features = input_scaler.transform(features_df)
        print(f"Scaled input features: {scaled_features}")

    # Handle LSTM models
    if isinstance(model, tf.keras.Model):       
        scaled_features = input_scaler.transform(features_df)
        scaled_features = scaled_features.reshape((scaled_features.shape[0], 1, scaled_features.shape[1]))
        print(f"Reshaped input for LSTM: {scaled_features.shape}")

    # Predict
    prediction = model.predict(scaled_features)
    print(f"Raw prediction output: {prediction}")

    # Inverse transform if output_scaler exists
    if output_scaler:
        if isinstance(model, SVR):
            prediction = output_scaler.inverse_transform(prediction.reshape(-1, 1)).ravel()
        
        if isinstance(model, tf.keras.Model):        
            prediction = output_scaler.inverse_transform(prediction)   
        
        print(f"Rescaled prediction: {prediction}")

    # Structure response
    response = {
        "predictions": [
            {
                "name": "penicillin_concentration",
                "value": prediction.tolist()
            }
        ]
    }

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=443, reload=True)