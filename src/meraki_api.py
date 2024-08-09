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

from typing import ClassVar, Optional

import meraki

from config.config import c


class MERAKI_API(object):
    """
    Meraki API Class, includes various methods to interact with Meraki API
    """
    _instance: ClassVar[Optional['MERAKI_API']] = None

    def __init__(self):
        """
        Initialize the Meraki class: dashboard sdk instance
        """
        self.org_id = c.ORG_ID
        self.retry_429_count = 25
        self.dashboard = meraki.DashboardAPI(api_key=c.MERAKI_API_KEY, suppress_logging=True,
                                             caller=c.APP_NAME, maximum_retries=self.retry_429_count)
        self.net_name_to_ids = self.network_name_to_id()

    @classmethod
    def get_instance(cls):
        """
        Get Singleton instance of Meraki Class
        :return: Singleton instance of Meraki Class
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def network_name_to_id(self) -> dict:
        """
        Return dict of Network Names to ID (useful for translation of raw config to IDs)
        :return: Dict mapping of network name to network id
        """
        # Get Org Networks (Appliance Only!)
        networks = self.dashboard.organizations.getOrganizationNetworks(self.org_id, total_pages='all',
                                                                        productTypes=['appliance'])

        net_name_to_id = {}
        for network in networks:
            net_name_to_id[network['name']] = network['id']

        return net_name_to_id

    def update_network_appliance_port(self, net_id: str, port_id: str, port_config: dict) -> tuple[
        str | None, dict | str]:
        """
        Update Network Appliance Port, return response or (error code, error message)
        https://developer.cisco.com/meraki/api-v1/update-network-appliance-port/
        :param port_id: Appliance Port Number
        :param net_id: Network ID containing Appliance
        :param port_config: Update Network Appliance Port payload
        :return: Error Code (if relevant), Response (or Error Message)
        """
        try:
            response = self.dashboard.appliance.updateNetworkAppliancePort(net_id, port_id, **port_config)
            return None, response
        except meraki.APIError as e:
            return e.status, str(e)
        except Exception as e:
            # SDK Error
            return "500", str(e)


meraki_api = MERAKI_API.get_instance()  # Singleton instance of MERAKI_API
