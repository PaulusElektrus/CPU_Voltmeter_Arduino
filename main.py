import json
import os
import time

from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

import serial
import serial.tools.list_ports


def get_local_json_contents(json_filename):
    """
    Returns the contents of a (local) JSON file

    :param json_filename: the filename (as a string) of the local JSON file
    :returns: the data of the JSON file
    """

    try:
        with open(json_filename) as json_file:
            try:
                data = json.load(json_file)
            except ValueError:
                print('Contents of "' + json_filename + '" are not valid JSON')
                raise
    except IOError:
        print('An error occurred while reading "' + json_filename + '"')
        raise
    return data


def get_json_contents(json_url):
    """
    Return the contents of a (remote) JSON file

    :param json_url: the url (as a string) of the remote JSON file
    :returns: the data of the JSON file
    """

    data = None

    req = Request(json_url)
    try:
        response = urlopen(req).read()
    except HTTPError as e:
        print("HTTPError " + str(e.code))
    except URLError as e:
        print("URLError " + str(e.reason))
    else:
        try:
            data = json.loads(response.decode("utf-8"))
        except ValueError:
            print("Invalid JSON contents")
    return data


def find_in_data(ohw_data, name):
    """
    Search in the OpenHardwareMonitor data for a specific node, recursively

    :param ohw_data:    OpenHardwareMonitor data object
    :param name:        Name of node to search for
    :returns:           The found node, or -1 if no node was found
    """
    if ohw_data["Text"] == name:
        # The node we are looking for is this one
        return ohw_data
    elif len(ohw_data["Children"]) > 0:
        # Look at the node's children
        for child in ohw_data["Children"]:
            if child["Text"] == name:
                # This child is the one we're looking for
                return child
            else:
                # Look at this children's children
                result = find_in_data(child, name)
                if result != -1:
                    # Node with specified name was found
                    return result
    # When this point is reached, nothing was found in any children
    return -1


def get_hardware_info(ohw_ip, ohw_port, cpu_name):
    """
    Get hardware info from OpenHardwareMonitor's web server and format it
    """

    ohw_json_url = "http://" + ohw_ip + ":" + ohw_port + "/data.json"

    # Get data from OHW's data json file
    data_json = get_json_contents(ohw_json_url)

    # Get info for CPU
    cpu_data = find_in_data(data_json, cpu_name)
    cpu_load = find_in_data(cpu_data, "CPU Total")

    # Get CPU total load, and remove ".0 %" from the end
    cpu_load_value = cpu_load["Value"][:-4]

    return cpu_load_value


def main():
    # Get serial ports
    ports = list(serial.tools.list_ports.comports())

    # Load config JSON
    cd = os.path.join(os.getcwd(), os.path.dirname(__file__))
    __location__ = os.path.realpath(cd)
    config = get_local_json_contents(os.path.join(__location__, "config.json"))

    # If there is only 1 serial port (so it is the Arduino) connect to that one
    if len(ports) == 1:
        # Connect to the port
        port = ports[0][0]
        print("Only 1 port found: " + port + ". Connecting to it...")
        ser = serial.Serial(port)

        while True:
            # Get current info
            my_info = get_hardware_info(
                config["ohw_ip"],
                config["ohw_port"],
                config["cpu_name"],
            )

            # print(arduino_str)
            ser.write(my_info.encode())

            # Wait until refreshing Arduino again
            time.sleep(2)
        ser.close()
    else:
        print("Number of ports is not 1, can't connect!")


if __name__ == "__main__":
    main()
