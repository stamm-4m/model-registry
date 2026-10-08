# Connection and subscription to the MQTT broker
from model_registry.mqtt_consumer.config import MQTT_HOST, MQTT_PORT, MQTT_TOPIC, MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD
import paho.mqtt.client as mqtt

import os
import time


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker: {MQTT_HOST}:{MQTT_PORT}")

        result, mid = client.subscribe(MQTT_TOPIC, qos=1)

        if result == mqtt.MQTT_ERR_SUCCESS:
            print(f"Subscribed to: {MQTT_TOPIC}")
        else:
            print(f"Subscription failed: {result}")
    else:
        print(f"MQTT connection failed. Return code: {rc}")


def on_message(client, userdata, message):
    print("=" * 80)
    print(f"Topic: {message.topic}")
    print(f"QoS: {message.qos}")
    print(f"Payload: {message.payload.decode('utf-8')}")
    print("=" * 80)


def on_disconnect(client, userdata, rc):
    print(f"Disconnected from MQTT broker. Return code: {rc}")


def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION1,
        client_id=MQTT_CLIENT_ID,
        clean_session=False,
    )

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.reconnect_delay_set(
        min_delay=1,
        max_delay=30,
    )

    while True:
        try:
            print(
                f"Connecting to MQTT broker "
                f"{MQTT_HOST}:{MQTT_PORT}..."
            )

            client.username_pw_set(
                MQTT_USERNAME,
                MQTT_PASSWORD,
            )
            client.connect(
                MQTT_HOST,
                MQTT_PORT,
                keepalive=60,
            )

            client.loop_forever()

        except Exception as error:
            print(f"MQTT error: {error}")
            print("Retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()