import os
import re
from datetime import datetime


class ModelMetadataExtractor:
    """
    Extract metadata from a stored ML model file.

    Expected filename format (partial):
        <id>_[<language>]_rest_of_name.ext
    """

    MODEL_TYPE_MAP = {
        "pkl": "pickle",
        "joblib": "sklearn",
        "h5": "keras",
        "keras": "keras",
        "rds": "r_model",
        "r": "r_script"
    }

    SAFE_EXTENSIONS = {"pkl", "joblib"}

    LANGUAGE_PATTERN = re.compile(r"^\d+_\[(.*?)\]_")

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.filename = os.path.basename(model_path)
        self.extension = self.filename.split(".")[-1].lower()

    def extract(self) -> dict:
        """Return all available metadata."""
        metadata = {
            "model_id": os.path.splitext(self.filename)[0],
            "model_file": self.filename,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0.0",
            "status": "offline",
            "language_name": self._extract_language(),
        }

        return metadata

    def _extract_language(self) -> str | None:
        """
        Extract programming language from filename.

        Example:
            0009_[Python]_penicillin_LSTM_target_scaler.pkl → Python
        """
        match = self.LANGUAGE_PATTERN.search(self.filename)
        if match:
            return match.group(1).strip()
        return None

