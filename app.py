import streamlit as st

st.set_page_config(
    page_title="Phyphox MQTT Connector Download",
    page_icon="📥",
    layout="centered"
)

st.title("Phyphox MQTT Connector")
st.write(
    "Click the button below to download the `.phyphox` file for the MQTT Connector experiment."
)

# Path to the phyphox file
phyphox_file_path = "mqtt_connector_v2.phyphox"

try:
    with open(phyphox_file_path, "r", encoding="utf-8") as f:
        phyphox_file_content = f.read()

    st.download_button(
        label="Download mqtt_connector_v2.phyphox",
        data=phyphox_file_content,
        file_name="mqtt_connector_v2.phyphox",
        mime="application/xml"
    )
except FileNotFoundError:
    st.error(f"Error: The file '{phyphox_file_path}' was not found.")
