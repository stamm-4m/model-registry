from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from model_registry.api.routers.instrument_readings_router import _measurement_row
from model_registry.api.models.instrument_reading import InstrumentReading
from model_registry.api.schemas.instrument_reading import (
    MQTTInstrumentMessage,
    MQTTMeasurement,
)


def test_mqtt_message_is_normalized_to_utc_and_preserves_payload():
    message = MQTTInstrumentMessage.model_validate(
        {
            "topic": (
                "prose_lab/research/Biogasbucket/example_instance_id/"
                "experiment/undefined/measurement/unknown"
            ),
            "instrument_id": "11111111-aaaa-bbbb-cccc-000000000001",
            "payload": [
                {
                    "measurement": "environment",
                    "tags": {"organisation": "prose_lab", "department": "research"},
                    "fields": {"pressure": 101.975, "ambient temp": 45.1},
                    "timestamp": 1758228856.467376,
                }
            ],
        }
    )

    item = message.payload[0]
    row = _measurement_row(message.topic, message.instrument_id, item)

    assert str(row.instrument_id) == "11111111-aaaa-bbbb-cccc-000000000001"
    assert any(
        foreign_key.target_fullname == "instruments.id"
        for foreign_key in InstrumentReading.__table__.c.instrument_id.foreign_keys
    )
    assert row.topic == message.topic
    assert row.measurement == "environment"
    assert row.time == datetime.fromtimestamp(1758228856.467376, tz=timezone.utc)
    assert row.payload == item.model_dump(mode="json")


def test_mqtt_message_accepts_a_single_measurement():
    message = MQTTInstrumentMessage.model_validate(
        {
            "topic": "prose_lab/research/Biogasbucket/device/measurement",
            "payload": {
                "measurement": "environment",
                "fields": {"pressure": 101.975},
                "timestamp": 1758228856,
            },
        }
    )

    assert isinstance(message.payload, MQTTMeasurement)


@pytest.mark.parametrize("timestamp", [float("nan"), float("inf"), 1e100])
def test_mqtt_message_rejects_invalid_timestamps(timestamp):
    with pytest.raises(ValidationError):
        MQTTMeasurement.model_validate(
            {
                "measurement": "environment",
                "fields": {},
                "timestamp": timestamp,
            }
        )
