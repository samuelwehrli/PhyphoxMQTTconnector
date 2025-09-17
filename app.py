import streamlit as st
import datetime
import pytz
from src.phyphox_generator import generate_phyphox_file

# --- Page Configuration ---
st.set_page_config(
    page_title="Phyphox MQTT Connector Configurator",
    page_icon="⚙️",
    layout="centered"
)

# --- UI Layout ---
st.title("Phyphox MQTT Connector Configurator")
st.write(
    "Configure your Phyphox MQTT-Connect experiment below and download the customized file."
)

# --- Main Configuration ---
st.header("MQTT Configuration")
mqtt_address = st.text_input("Server Address", "test.mosquitto.org:1883")
mqtt_topic = st.text_input("Topic", "zhaw/pcls/wehs/phyphox")

# --- Optional Sensors ---
st.header("Optional Sensors")
enable_light_sensor = st.checkbox("Enable Light Sensor (on some Android devices)")
enable_pressure_sensor = st.checkbox("Enable Pressure Sensor (Iphones & some Android devices)")

# --- Advanced Settings Expander ---
with st.expander("Advanced Settings"):
    st.subheader("Experiment Configuration")

    # Timezone selection
    timezones = pytz.all_timezones
    default_tz_index = timezones.index('Europe/Zurich') if 'Europe/Zurich' in timezones else 0
    selected_timezone = st.selectbox("Select your timezone", timezones, index=default_tz_index)

    # Generate timestamp based on selected timezone
    tz = pytz.timezone(selected_timezone)
    default_timestamp = datetime.datetime.now(tz).strftime("%d%m%y-%H%M")
    experiment_id = st.text_input("Experiment ID (for filename and title)", default_timestamp)

    st.subheader("Sensor and Network Configuration")
    sensor_rate = st.number_input("Sensor Rate (Hz)", min_value=1, max_value=100, value=10, step=1)
    network_interval = st.number_input("Network Interval (s)", min_value=0.1, max_value=10.0, value=0.1, step=0.1, format="%.1f")


# --- File Generation and Download ---

# Generate the file content on-the-fly based on user input
modified_phyphox_content = generate_phyphox_file(
    mqtt_address,
    mqtt_topic,
    sensor_rate,
    network_interval,
    experiment_id,
    enable_light_sensor,
    enable_pressure_sensor
)

st.header("Download")

# Check if the generator returned an error string
if isinstance(modified_phyphox_content, str) and modified_phyphox_content.startswith("Error:"):
    st.error(modified_phyphox_content)
else:
    download_filename = f"MQTT-Connect_{experiment_id}.phyphox"
    st.download_button(
        label="Download customized .phyphox file",
        data=modified_phyphox_content,
        file_name=download_filename,
        mime="application/octet-stream"
    )
