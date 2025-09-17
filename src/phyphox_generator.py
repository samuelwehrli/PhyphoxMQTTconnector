import xml.etree.ElementTree as ET
from io import BytesIO

# --- Constants ---
BASE_PHYPHOX_FILE_PATH = "templates/mqtt_connector_base.phyphox"
PHYPHOX_NAMESPACE = "http://phyphox.org/xml"

# --- Private Helper Functions ---

def _parse_base_file():
    """Parses the base phyphox file and returns the tree, root, and namespace."""
    ET.register_namespace("", PHYPHOX_NAMESPACE)
    tree = ET.parse(BASE_PHYPHOX_FILE_PATH)
    root = tree.getroot()
    ns = {'p': PHYPHOX_NAMESPACE}
    return tree, root, ns

def _set_title(root, ns, exp_id):
    """Sets the experiment title."""
    title_element = root.find('p:title', ns)
    if title_element is not None:
        title_element.text = f"MQTT-Connect {exp_id}"

def _set_mqtt_connection(root, ns, address, topic, interval):
    """Configures the MQTT connection settings."""
    connection_element = root.find('p:network/p:connection', ns)
    if connection_element is not None:
        connection_element.set('address', address)
        connection_element.set('sendTopic', topic)
        connection_element.set('interval', str(interval))
    return connection_element

def _update_info_view(root, ns, address, topic, rate, interval, enable_light, enable_pressure):
    """Updates the info view with the current settings in a single, compact line."""
    info_element = root.find('p:views/p:view/p:info', ns)
    if info_element is not None:
        # Ensure the element has no text content from previous attempts
        info_element.text = None

        parts = [
            f"server={address}",
            f"topic={topic}",
            f"rate={rate}Hz",
            f"interval={interval}s"
        ]

        enabled_sensors = []
        if enable_light:
            enabled_sensors.append("Light")
        if enable_pressure:
            enabled_sensors.append("Pressure")

        if enabled_sensors:
            parts.append(f"add_sensors=[{', '.join(enabled_sensors)}]")

        info_text = "; ".join(parts)
        info_element.set('label', info_text)


def _set_all_sensor_rates(root, ns, rate):
    """Sets the sampling rate for all existing sensors."""
    for sensor in root.findall('p:input/p:sensor', ns):
        sensor.set('rate', str(rate))

def _add_light_sensor(root, ns, rate, connection_element):
    """Dynamically adds the light sensor elements to the XML tree."""
    # 1. Add data container
    data_containers_element = root.find('p:data-containers', ns)
    if data_containers_element is not None:
        ET.SubElement(
            data_containers_element, 'container',
            {'size': '1', 'static': 'false'}
        ).text = 'Light'

    # 2. Add sensor input
    input_element = root.find('p:input', ns)
    if input_element is not None:
        light_sensor_el = ET.SubElement(
            input_element, 'sensor',
            {'rate': str(rate), 'average': 'false', 'type': 'light'}
        )
        ET.SubElement(light_sensor_el, 'output', {'component': 'x'}).text = 'Light'

    # 3. Add network send rule
    if connection_element is not None:
        ET.SubElement(
            connection_element, 'send',
            {'clear': 'false', 'id': 'Light', 'type': 'buffer', 'datatype': 'number'}
        ).text = 'Light'

def _add_pressure_sensor(root, ns, rate, connection_element):
    """Dynamically adds the pressure sensor elements to the XML tree."""
    # 1. Add data container
    data_containers_element = root.find('p:data-containers', ns)
    if data_containers_element is not None:
        ET.SubElement(
            data_containers_element, 'container',
            {'size': '1', 'static': 'false'}
        ).text = 'Pressure'

    # 2. Add sensor input
    input_element = root.find('p:input', ns)
    if input_element is not None:
        pressure_sensor_el = ET.SubElement(
            input_element, 'sensor',
            {'rate': str(rate), 'average': 'false', 'type': 'pressure'}
        )
        ET.SubElement(pressure_sensor_el, 'output', {'component': 'x'}).text = 'Pressure'

    # 3. Add network send rule
    if connection_element is not None:
        ET.SubElement(
            connection_element, 'send',
            {'clear': 'false', 'id': 'Pressure', 'type': 'buffer', 'datatype': 'number'}
        ).text = 'Pressure'

def _convert_tree_to_bytes(tree):
    """Converts the final XML tree to a byte stream for download."""
    output_buffer = BytesIO()
    tree.write(output_buffer, encoding='utf-8', xml_declaration=True)
    return output_buffer.getvalue()

# --- Public Main Function ---

def generate_phyphox_file(address, topic, rate, interval, exp_id, enable_light, enable_pressure):
    """
    Parses the base phyphox file, updates it with user settings,
    and returns the modified XML content as bytes.
    """
    try:
        tree, root, ns = _parse_base_file()

        _set_title(root, ns, exp_id)
        connection_element = _set_mqtt_connection(root, ns, address, topic, interval)
        _set_all_sensor_rates(root, ns, rate)
        _update_info_view(root, ns, address, topic, rate, interval, enable_light, enable_pressure)
        
        if enable_light:
            _add_light_sensor(root, ns, rate, connection_element)

        if enable_pressure:
            _add_pressure_sensor(root, ns, rate, connection_element)
            
        return _convert_tree_to_bytes(tree)
        
    except FileNotFoundError:
        return f"Error: The base file '{BASE_PHYPHOX_FILE_PATH}' was not found."
    except Exception as e:
        return f"An error occurred while generating the file: {e}"
