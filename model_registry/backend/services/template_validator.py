"""Template-based model validation using JSON Schema.

Provides validation for model payloads against STAMM (Standard for Transfer,
Analysis and Management of Models) compliant JSON schemas. Each algorithm
family has a corresponding schema that specifies required/optional fields,
hyperparameters, and their constraints.

Schemas are stored in model_registry/backend/model_templates/families/ and
referenced by the algorithm field in the model payload.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

try:
    import jsonschema
    from jsonschema import Draft202012Validator, ValidationError
except ImportError:
    jsonschema = None
    ValidationError = Exception


logger = logging.getLogger(__name__)

# All 18 STAMM algorithm families supported
SUPPORTED_ALGORITHMS = {
    "decision_tree",
    "random_forest",
    "gradient_boosting",
    "ensemble",
    "svm",
    "linear_regression",
    "logistic_regression",
    "neural_network",
    "rnn",
    "cnn",
    "transformer",
    "gaussian_process",
    "pls",
    "pca",
    "kmeans",
    "cubist",
    "m5",
    "custom",
}


class TemplateValidationError(Exception):
    """Raised when model payload fails schema validation."""

    def __init__(self, algorithm: str, errors: List[str]):
        self.algorithm = algorithm
        self.errors = errors
        message = f"Template validation failed for algorithm '{algorithm}':\n" + \
                  "\n".join(f"  - {err}" for err in errors)
        super().__init__(message)


class TemplateValidator:
    """Validates model configurations against STAMM-compliant JSON schemas."""

    def __init__(self, schemas_dir: Optional[str] = None):
        """Initialize validator with path to schemas directory.

        Args:
            schemas_dir: Path to model_templates/families/ directory.
                        If None, attempts to auto-detect from package structure.
        """
        if schemas_dir is None:
            # Auto-detect: assume this file is at backend/services/template_validator.py
            backend_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            schemas_dir = os.path.join(backend_dir, "model_templates", "families")

        self.schemas_dir = schemas_dir
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._validators: Dict[str, Draft202012Validator] = {}

        if jsonschema is None:
            logger.warning(
                "jsonschema library not installed. "
                "Template validation will be skipped. "
                "Install with: pip install jsonschema"
            )

    def _load_schema(self, algorithm: str) -> Optional[Dict[str, Any]]:
        """Load schema file for given algorithm (cached).

        Args:
            algorithm: Algorithm name (e.g., 'random_forest')

        Returns:
            Schema dict, or None if not found/jsonschema unavailable
        """
        if not jsonschema:
            return None

        if algorithm in self._schemas:
            return self._schemas[algorithm]

        schema_file = os.path.join(self.schemas_dir, f"{algorithm}.schema.json")
        if not os.path.exists(schema_file):
            logger.warning(f"Schema file not found: {schema_file}")
            return None

        try:
            with open(schema_file, "r") as f:
                schema = json.load(f)
                self._schemas[algorithm] = schema
                return schema
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load schema {schema_file}: {e}")
            return None

    def _get_validator(self, algorithm: str) -> Optional[Draft202012Validator]:
        """Get or create validator for given algorithm.

        Args:
            algorithm: Algorithm name

        Returns:
            Validator instance, or None if schema unavailable
        """
        if algorithm in self._validators:
            return self._validators[algorithm]

        schema = self._load_schema(algorithm)
        if schema is None:
            return None

        validator = Draft202012Validator(schema)
        self._validators[algorithm] = validator
        return validator

    def validate(self, payload: Dict[str, Any]) -> None:
        """Validate model payload against its algorithm's schema.

        Args:
            payload: Model creation payload with 'algorithm' field

        Raises:
            TemplateValidationError: If validation fails
            ValueError: If algorithm not specified or not supported
        """
        if not jsonschema:
            logger.debug("jsonschema not available; skipping template validation")
            return

        algorithm = payload.get("algorithm")
        if not algorithm:
            raise ValueError("Model payload must include 'algorithm' field")

        if algorithm not in SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Unsupported algorithm '{algorithm}'. "
                f"Must be one of: {', '.join(sorted(SUPPORTED_ALGORITHMS))}"
            )

        validator = self._get_validator(algorithm)
        if validator is None:
            logger.warning(
                f"Schema not available for algorithm '{algorithm}'. "
                "Skipping template validation."
            )
            return

        # Collect all validation errors
        errors: List[str] = []
        for error in validator.iter_errors(payload):
            # Format error message with JSON path
            path = ".".join(str(p) for p in error.absolute_path) or "root"
            msg = f"{path}: {error.message}"
            errors.append(msg)

        if errors:
            raise TemplateValidationError(algorithm, errors)

    def validate_batch(self, payloads: List[Dict[str, Any]]) -> Dict[int, List[str]]:
        """Validate multiple payloads, collecting errors for each.

        Useful for batch operations where partial failures are acceptable.

        Args:
            payloads: List of model payloads

        Returns:
            Dict mapping payload index to list of error messages.
            Empty dict if all payloads are valid.
        """
        failures: Dict[int, List[str]] = {}

        for i, payload in enumerate(payloads):
            try:
                self.validate(payload)
            except TemplateValidationError as e:
                failures[i] = e.errors
            except (ValueError, Exception) as e:
                failures[i] = [str(e)]

        return failures

    def get_schema_info(self, algorithm: str) -> Optional[Dict[str, Any]]:
        """Get schema info for given algorithm (for UI/documentation).

        Args:
            algorithm: Algorithm name

        Returns:
            Schema dict, or None if not available
        """
        return self._load_schema(algorithm)

    def list_available_algorithms(self) -> List[str]:
        """List all supported algorithm families.

        Returns:
            Sorted list of algorithm names
        """
        return sorted(SUPPORTED_ALGORITHMS)


# Module-level singleton instance
_validator_instance: Optional[TemplateValidator] = None


def get_validator() -> TemplateValidator:
    """Get or create module-level validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = TemplateValidator()
    return _validator_instance


def validate_model_payload(payload: Dict[str, Any]) -> None:
    """Convenience function to validate payload using module-level validator.

    Args:
        payload: Model creation payload

    Raises:
        TemplateValidationError: If validation fails
        ValueError: If algorithm not specified or not supported
    """
    get_validator().validate(payload)
