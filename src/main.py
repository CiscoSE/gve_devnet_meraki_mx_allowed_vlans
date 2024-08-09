#!/usr/bin/env python3
"""
Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Trevor Maco <tmaco@cisco.com>"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import argparse
import csv
import os
import sys
import time

from config.config import c
from logger.logrr import lm
from meraki_api import meraki_api


def main():
    """
    Main Function, Update Network Appliance Ports across networks!
    :return:
    """
    lm.print_start_panel(app_name=c.APP_NAME)  # Print the start info message to console
    lm.print_config_table(config_instance=c)  # Print the config table

    # Set up argument parser (for ability to specify input file)
    parser = argparse.ArgumentParser(description='Process Appliance Port Configuration file.')
    parser.add_argument('-i', '--input', type=str, default=c.CSV_FILE_NAME, help='Input CSV File name (with extension)')
    args = parser.parse_args()

    # Get the input file name (either from CLI or config file)
    input_filename = args.input
    input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), input_filename)

    lm.p_panel(f"Read in Appliance Port Configs", title="Step 1")

    # Read in CSV of appliance port configs
    try:
        with open(input_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            appliance_port_configs = list(reader)
        lm.lnp(f"Read in {len(appliance_port_configs)} Appliance Port Configs", "success")
        time.sleep(1)
    except FileNotFoundError as e:
        lm.lnp(f"Appliance Port Configs File Not Found: {e}", "error")
        sys.exit(-1)

    # Apply Port Configurations
    lm.p_panel(f"Apply Appliance Port Configurations for Specified Networks", title="Step 2")

    with lm.yield_progress_instance() as progress:
        overall_progress = progress.add_task("Overall Progress", total=len(appliance_port_configs))
        counter = 1

        log_p = lm.yield_progress_logger_instance(console=progress.console)

        for appliance_port_config in appliance_port_configs:
            # Extract Network Name and Port ID
            net_name = appliance_port_config.get('Network Name', 'Unknown')
            port_id = appliance_port_config.get('portId', 'Unknown')

            log_p.info(f"Processing `{net_name}`, `port {port_id}` ({counter} of {len(appliance_port_configs)}):")

            # Update progress
            counter += 1
            progress.update(overall_progress, advance=1)

            # Sanity Check Network Name in Network Name to ID Mapping, extract ID
            if net_name not in meraki_api.net_name_to_ids or net_name == 'Unknown':
                log_p.error(f"Network Name `{net_name}` not Found in Network Name to ID Mapping\n")
                continue
            else:
                net_id = meraki_api.net_name_to_ids[net_name]
                del appliance_port_config['Network Name']

            # Check Port ID provided, extract value
            if 'portId' not in appliance_port_config or port_id == 'Unknown':
                log_p.error(f"Port ID Not Provided in Appliance Port Config: {appliance_port_config}\n")
                continue
            else:
                del appliance_port_config['portId']

            # Apply Port Configuration
            error, response = meraki_api.update_network_appliance_port(net_id, port_id, appliance_port_config)
            if error:
                log_p.error(f"Error Updating Appliance Port: {error} - {response}\n")
            else:
                log_p.info(f"Successfully Updated Appliance Port: {response}\n")
            time.sleep(0.3)

    # Ensure shutdown is called at the end to properly release resources
    lm.shutdown()


if __name__ == '__main__':
    main()
