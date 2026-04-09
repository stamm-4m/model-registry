import logging
from pyexpat import model
import pandas as pd
import requests
import tensorflow as tf
from fastapi import HTTPException
from sklearn.ensemble import (
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

from model_registry.api.config.settings import settings
from model_registry.api.models.prediction_request import PredictionRequest
import logging

from model_registry.api.utils.project_loader import get_project_folder_from_id
logger = logging.getLogger(__name__)


class ModelPredictor:
    """
    Class to encapsulate ML model prediction logic.
    """

    def __init__(self, model, input_scaler=None, output_scaler=None, outputs=None):
        self.model = model
        self.input_scaler = input_scaler
        self.output_scaler = output_scaler
        self.outputs = outputs

    def predict(self, request: PredictionRequest):
        input_data = request.req.get("input_data", {})
        feature_names = list(input_data.keys())
        features_df = pd.DataFrame([input_data], columns=feature_names)
        print("THE MODEL IS ...")
        print(self.model)

        # Preprocessing depending on model type
        if isinstance(self.model, (DecisionTreeRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor, RandomForestRegressor)):
            scaled_features = features_df
        elif isinstance(self.model, SVR):
            scaled_features = self.input_scaler.transform(features_df)
        elif isinstance(self.model, tf.keras.Model):
            scaled_features = self.input_scaler.transform(features_df)
            scaled_features = scaled_features.reshape((scaled_features.shape[0], 1, scaled_features.shape[1]))
        else:
            raise HTTPException(status_code=400, detail="Unsupported model type")

        prediction = self.model.predict(scaled_features)

        # Rescale if needed
        if self.output_scaler is not None:
            if isinstance(self.model, SVR):
                prediction = self.output_scaler.inverse_transform(prediction.reshape(-1, 1)).ravel()
            else:
                prediction = self.output_scaler.inverse_transform(prediction)

        return {
            "output_model": [
                {
                    "metadata": self.outputs,
                    "prediction": prediction.tolist()
                }
            ]
        }

    def _proxy_to_r_api(project_id: str, model_id: str, request: PredictionRequest):
        try:

            payload = request.dict()
            folder_project_id = get_project_folder_from_id(project_id)
            logger.debug("PATH_PROJECT_ID: " + folder_project_id)
            payload["project_id"] = folder_project_id
            payload["model_id"] = model_id

            response = requests.post(settings.R_API_URL, json=payload, timeout=30)
            response.raise_for_status()
            r_data = response.json()
            #logger.info(f"Received response from R API for project '{project_id}', model '{model_id}': {r_data}")
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


    def create_predictor(model, input_scaler=None, output_scaler=None, outputs=None):
        """
        Factory function to create a ModelPredictor instance."""
        return ModelPredictor(model, input_scaler, output_scaler, outputs)