# Phyphox MQTT Connector Configurator

This is a Streamlit web application that allows you to dynamically configure and generate a `.phyphox` experiment file for sending sensor data to an MQTT server.

## Features

- **Dynamic Configuration**: Set MQTT server, topic, sensor rate, and network interval.
- **Customizable ID**: Assign a unique ID to each experiment, which is used for the filename and the in-app title.
- **Timezone Support**: Select your local timezone to ensure accurate timestamps.
- **Optional Sensors**: Easily enable or disable specific sensors (like the light sensor).
- **Instant Download**: Get your customized `.phyphox` file immediately.

## Project Structure

The project is organized to separate the user interface from the core logic:

```
/
├── templates/
│   └── mqtt_connector_base.phyphox   # The base template file
├── src/
│   └── phyphox_generator.py          # Contains all the XML generation logic
├── app.py                            # The main Streamlit application (UI only)
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## How to Run

1.  **Set up the environment**:
    It is recommended to use a virtual environment.

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit app**:
    ```bash
    streamlit run app.py
    ```

The application will open in a new browser tab.