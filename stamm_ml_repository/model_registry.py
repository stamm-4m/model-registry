# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:15:33 2025

@author: David Camilo Corrales
@email: David-Camilo.Corrales-Munoz@inrae.fr

"""

import yaml  # type: ignore
import os
import joblib
import tensorflow as tf

CONFIG_DIR = "configs"
MODEL_DIR = "models"
soft_sensors = {}
PROJECT_INFO_FILE = os.path.join(os.path.dirname(__file__), "project_info.yaml")
project_info = {}

def load_model_and_scalers(model_name):
    """Loads the model and its associated scalers only if required."""
    if model_name not in soft_sensors:
        raise ValueError(f"Model '{model_name}' not found in soft_sensors")

    model_info = soft_sensors[model_name]
    config = model_info["config"]
    model = model_info["model"]

    # Check if the model needs scalers
    input_scaler = None
    output_scaler = None

    if "scaler" in config["ml_model_configuration"]["inputs"]:
        input_scaler_path = os.path.join(MODEL_DIR, config["ml_model_configuration"]["inputs"]["scaler"])
        if os.path.exists(input_scaler_path):
            input_scaler = joblib.load(input_scaler_path)
            print(f"Loaded input scaler for {model_name} from {input_scaler_path}")
        else:
            print(f"Warning: Input scaler file {input_scaler_path} not found for {model_name}")

    if "scaler" in config["ml_model_configuration"]["outputs"]:
        output_scaler_path = os.path.join(MODEL_DIR, config["ml_model_configuration"]["outputs"]["scaler"])
        if os.path.exists(output_scaler_path):
            output_scaler = joblib.load(output_scaler_path)

    return model, input_scaler, output_scaler

# Load all YAML configurations dynamically
for file in os.listdir(CONFIG_DIR):
      if file.endswith(".yaml"):
          with open(os.path.join(CONFIG_DIR, file), "r") as f:
              config = yaml.safe_load(f)
              model_name = config["ml_model_configuration"]["model_identification"]["name"]
              model_file = config["ml_model_configuration"]["model_description"]["config_files"]["model_file"]
              model_path = os.path.join(MODEL_DIR, model_file)
 
              if os.path.exists(model_path):
                  file_ext = os.path.splitext(model_file)[-1].lower()
                  if file_ext in [".keras", ".h5"]:
                      model = tf.keras.models.load_model(model_path)
                  elif file_ext in [".joblib", ".pkl"]:
                      model = joblib.load(model_path)
                  else:
                      print(f"Warning: Unsupported model file format for {model_file}")
                      continue
  
                  soft_sensors[model_name] = {
                      "config": config,
                      "model": model,
                  }
              else:
                  print(f"Warning: Model file {model_file} not found!")


def predict(model_name, features):
    """Runs inference using the selected ML soft sensor."""
    if model_name not in soft_sensors:
        return {"error": f"Model '{model_name}' not found"}

    model, input_scaler, output_scaler = load_model_and_scalers(model_name)

    print(f"\nRaw input features: {features}")

    # Handle input scaling
    if model_name == "CART":
        features_array = [features]  # CART uses raw features
        print("Skipping input scaling for CART.")
    else:
        features_array = input_scaler.transform([features]) if input_scaler else [features]
        print(f"Scaled input features: {features_array}")

    # Handle LSTM reshaping
    if isinstance(model, tf.keras.Model):
        features_array = features_array.reshape((1, 1, -1))
        print(f"Reshaped input for LSTM: {features_array.shape}")

    # Make prediction
    prediction = model.predict(features_array)
    print(f"Raw prediction output: {prediction}")

    # Inverse transform if necessary
    if output_scaler:
        prediction = output_scaler.inverse_transform(prediction)
        print(f"Rescaled prediction: {prediction}")
    else:
        print("No output scaler applied.")

    return {"model": model_name, "prediction": prediction.tolist()}


# Explicitly define the exported symbols
__all__ = ["predict", "soft_sensors", "load_model_and_scalers"]

def load_project_info():
    if os.path.exists(PROJECT_INFO_FILE):
        try:
            with open(PROJECT_INFO_FILE, "r", encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading {PROJECT_INFO_FILE}: {e}")
    else:
        print(f"Warning: {PROJECT_INFO_FILE} not found!")
    return {}


# Add project_info to exported symbols
__all__ += ["project_info"]