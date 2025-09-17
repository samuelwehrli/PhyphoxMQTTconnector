import streamlit as st
import xml.etree.ElementTree as ET
from io import BytesIO
import datetime
import pytz

st.set_page_config(
    page_title="Phyphox MQTT Connector Configurator",
    page_icon="⚙️",
    layout="centered"
)

st.title("Phyphox MQTT Connector Configurator")

st.write(
    "Configure your Phyphox MQTT experiment below and download the customized file."
)

# --- Configuration Inputs ---
st.header("Experiment Configuration")

# Timezone selection
timezones = pytz.all_timezones
default_tz_index = timezones.index('Europe/Zurich') if 'Europe/Zurich' in timezones else 0
selected_timezone = st.selectbox("Select your timezone", timezones, index=default_tz_index)

# Generate timestamp based on selected timezone
tz = pytz.timezone(selected_timezone)
default_timestamp = datetime.datetime.now(tz).strftime("%d%m%y-%H%M")
experiment_id = st.text_input("Experiment ID (for filename and title)", default_timestamp)

st.header("MQTT Configuration")
mqtt_address = st.text_input("Server Address", "test.mosquitto.org:1883")
mqtt_topic = st.text_input("Topic", "zhaw/pcls/wehs/phyphox")

st.header("Sensor and Network Configuration")
sensor_rate = st.number_input("Sensor Rate (Hz)", min_value=1, max_value=100, value=10, step=1)
network_interval = st.number_input("Network Interval (s)", min_value=0.1, max_value=10.0, value=0.1, step=0.1, format="%.1f")


# --- XML Modification Logic ---
def generate_phyphox_file(address, topic, rate, interval, exp_id):
    """
    Parses the base phyphox file, updates it with user settings,
    and returns the modified XML content as bytes.
    """
    # Register namespace to avoid clunky prefixes in output
    ET.register_namespace("", "http://phyphox.org/xml")
    
    tree = ET.parse(base_phyphox_file_path)
    root = tree.getroot()
    
    # The namespace is required for find()
    ns = {'p': 'http://phyphox.org/xml'}
    
    # Find and update the title
    title_element = root.find('p:title', ns)
    if title_element is not None:
        title_element.text = f"MQTT-Connect {exp_id}"
    
    # Find and update the network connection settings
    connection_element = root.find('p:network/p:connection', ns)
    if connection_element is not None:
        connection_element.set('address', address)
        connection_element.set('sendTopic', topic)
        connection_element.set('interval', str(interval))
        
    # Find and update the info text view
    info_element = root.find('p:views/p:view/p:info', ns)
    if info_element is not None:
        info_text = (
            f"MQTT Address: {address}\n"
            f"MQTT Topic: {topic}\n"
            f"Sensor Rate: {rate} Hz\n"
            f"Network Interval: {interval} s"
        )
        info_element.set('label', info_text)

    # Find and update all sensor rates
    for sensor in root.findall('p:input/p:sensor', ns):
        sensor.set('rate', str(rate))
        
    # Convert the modified XML tree to a string, then to bytes
    output_buffer = BytesIO()
    tree.write(output_buffer, encoding='utf-8', xml_declaration=True)
    return output_buffer.getvalue()


# Path to the base phyphox file
base_phyphox_file_path = "mqtt_connector_base.phyphox"

try:
    # Generate the file content on-the-fly based on user input
    modified_phyphox_content = generate_phyphox_file(
        mqtt_address,
        mqtt_topic,
        sensor_rate,
        network_interval,
        experiment_id
    )

    st.header("Download")
    download_filename = f"MQTT-Connect_{experiment_id}.phyphox"
    st.download_button(
        label="Download customized .phyphox file",
        data=modified_phyphox_content,
        file_name=download_filename,
        mime="application/octet-stream"
    )
except FileNotFoundError:
    st.error(f"Error: The base file '{base_phyphox_file_path}' was not found.")
except Exception as e:
    st.error(f"An error occurred while generating the file: {e}")
