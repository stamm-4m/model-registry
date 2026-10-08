# Variables and configurations for the MQTT consumer

import os


MQTT_HOST = os.getenv("MQTT_HOST", "stamm-model-registry")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv(
    "MQTT_TOPIC",
    "bioind4/research/Biogasbucket/#",
)
MQTT_CLIENT_ID = os.getenv(
    "MQTT_CLIENT_ID",
    "stamm-mqtt-consumer",
)
MQTT_USERNAME = os.getenv(
    "MQTT_USERNAME",
    "stamm-mqtt-consumer"
)
MQTT_PASSWORD = os.getenv(
    "MQTT_PASSWORD",
    "other_secure_password"
)