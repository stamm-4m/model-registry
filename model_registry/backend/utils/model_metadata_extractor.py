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

    # Maps short codes that may appear in filenames (e.g. "CART", "RF")
    # to the canonical algorithm values accepted by the ``models.algorithm``
    # CHECK constraint in Postgres.
    ALGORITHM_MAP = {
        "rf": "random_forest",
        "randomforest": "random_forest",
        "random_forest": "random_forest",
        "cart": "decision_tree",
        "dt": "decision_tree",
        "decisiontree": "decision_tree",
        "decision_tree": "decision_tree",
        "gbm": "gradient_boosting",
        "gb": "gradient_boosting",
        "hgb": "gradient_boosting",
        "gradient_boosting": "gradient_boosting",
        "xgb": "gradient_boosting",
        "xgboost": "gradient_boosting",
        "svm": "svm",
        "svr": "svm",
        "lstm": "rnn",
        "rnn": "rnn",
        "gru": "rnn",
        "nn": "neural_network",
        "mlp": "neural_network",
        "ann": "neural_network",
    }

    # Pattern for the trailing algorithm token in filenames such as
    # ``0001_[python]_penicillin_RF.pkl`` or ``0004_[R]_penicillin_CART.rds``.
    ALGORITHM_PATTERN = re.compile(r"_([A-Za-z]+)$")

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.filename = os.path.basename(model_path)
        self.extension = self.filename.split(".")[-1].lower()

    # Allowed values for the ``models.status`` CHECK constraint.
    ALLOWED_STATUS = {"draft", "training", "trained", "deployed", "archived"}

    # Allowed values for the ``models.validation_status`` CHECK constraint.
    ALLOWED_VALIDATION_STATUS = {"pending", "approved", "rejected"}

    # Allowed values for the ``models.federation_role`` CHECK constraint
    # (NULL is also accepted; we default to NULL for non-federated models).
    ALLOWED_FEDERATION_ROLE = {"local_update", "aggregated_global"}

    # Allowed values for the ``models.algorithm`` CHECK constraint.
    ALLOWED_ALGORITHMS = {
        "decision_tree", "random_forest", "gradient_boosting", "ensemble",
        "svm", "linear_regression", "logistic_regression", "neural_network",
        "rnn", "cnn", "transformer", "gaussian_process", "pls", "pca",
        "kmeans", "custom",
    }

    def extract(self) -> dict:
        """Return all available metadata."""
        metadata = {
            "model_id": os.path.splitext(self.filename)[0],
            "model_file": self.filename,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "version": "1.0.0",
            "status": "draft",
            "validation_status": "pending",
            "federation_role": None,
            "language_name": self._extract_language(),
            "algorithm": self._extract_algorithm(),
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

    def _extract_algorithm(self) -> str:
        """
        Extract canonical algorithm name from filename.

        Looks at the trailing token before the extension (e.g. ``RF``,
        ``CART``, ``LSTM``) and maps it through ``ALGORITHM_MAP``. Falls
        back to ``"custom"`` when no match is found.
        """
        stem = os.path.splitext(self.filename)[0]
        match = self.ALGORITHM_PATTERN.search(stem)
        if match:
            token = match.group(1).lower()
            mapped = self.ALGORITHM_MAP.get(token)
            if mapped and mapped in self.ALLOWED_ALGORITHMS:
                return mapped
        return "custom"

