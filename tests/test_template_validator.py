"""Tests for template validation module.

Quick tests to verify JSON Schema validation works as expected
before integrating with UI and callbacks.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from model_registry.backend.services.template_validator import (
    TemplateValidator,
    TemplateValidationError,
    validate_model_payload,
    get_validator,
)


def test_validator_initialization():
    """Test that validator initializes correctly."""
    print("TEST 1: Validator initialization...")
    validator = TemplateValidator()
    assert validator is not None
    print("✓ Validator initialized successfully")


def test_list_algorithms():
    """Test listing supported algorithms."""
    print("\nTEST 2: List supported algorithms...")
    validator = get_validator()
    algorithms = validator.list_available_algorithms()
    print(f"✓ Supported algorithms ({len(algorithms)}):")
    for algo in algorithms:
        print(f"  - {algo}")
    assert len(algorithms) == 18
    assert "random_forest" in algorithms
    assert "cubist" in algorithms
    assert "m5" in algorithms
    assert "custom" in algorithms


def test_validate_without_algorithm():
    """Test validation fails gracefully without algorithm."""
    print("\nTEST 3: Validation without algorithm field...")
    payload = {
        "name": "Test Model",
        "version": "1.0.0"
    }
    try:
        validate_model_payload(payload)
        print("✗ Should have raised ValueError")
        assert False
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")


def test_validate_with_unsupported_algorithm():
    """Test validation fails with unsupported algorithm."""
    print("\nTEST 4: Validation with unsupported algorithm...")
    payload = {
        "algorithm": "unknown_algo",
        "name": "Test Model"
    }
    try:
        validate_model_payload(payload)
        print("✗ Should have raised ValueError")
        assert False
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")


def test_validate_custom_algorithm():
    """Test validation with custom algorithm (should pass with no schema)."""
    print("\nTEST 5: Validation with custom algorithm...")
    payload = {
        "algorithm": "custom",
        "name": "Test Custom Model",
        "config": {
            "any_param": "any_value"
        }
    }
    try:
        validate_model_payload(payload)
        print("✓ Custom algorithm validated successfully (no schema required)")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise


def test_batch_validation():
    """Test batch validation with mixed results."""
    print("\nTEST 6: Batch validation...")
    validator = get_validator()
    payloads = [
        {"algorithm": "custom", "name": "Model 1"},
        {"algorithm": "unknown", "name": "Model 2"},  # Invalid
        {"name": "Model 3"},  # No algorithm
    ]
    failures = validator.validate_batch(payloads)
    print(f"✓ Batch validation completed with {len(failures)} failures:")
    for idx, errors in failures.items():
        print(f"  - Payload {idx}: {errors}")


def test_get_schema_info():
    """Test retrieving schema info for algorithms."""
    print("\nTEST 7: Get schema info...")
    validator = get_validator()
    
    # Try getting custom schema (should exist or be skipped)
    custom_schema = validator.get_schema_info("custom")
    if custom_schema:
        print(f"✓ Got schema for 'custom': {len(json.dumps(custom_schema))} bytes")
    else:
        print("✓ Schema for 'custom' not available (expected if templates not loaded)")


def test_validator_singleton():
    """Test that get_validator returns singleton."""
    print("\nTEST 8: Validator singleton behavior...")
    validator1 = get_validator()
    validator2 = get_validator()
    assert validator1 is validator2
    print("✓ get_validator returns singleton instance")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("TEMPLATE VALIDATOR TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_validator_initialization,
        test_list_algorithms,
        test_validate_without_algorithm,
        test_validate_with_unsupported_algorithm,
        test_validate_custom_algorithm,
        test_batch_validation,
        test_get_schema_info,
        test_validator_singleton,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
