# Copyright 2017 Brocade Communications Systems, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from lib.prep_vars import PrepVars
from netmiko import ConnectHandler


class CreateKeepAlive(PrepVars):

    def __init__(self, config=None):
        super(CreateKeepAlive, self).__init__(config=config)

    def run(self):
        devices = self.mct_devices()
        try:
            print ("creating keep-alive link...")
            for device in devices:
                net_connect = ConnectHandler(**device)
                net_connect.enable()
                net_connect.config_mode(config_command='configure terminal')
                net_connect.send_command_timing('vlan 1')
                net_connect.send_command_timing(
                    'no untagged ethernet {0}'.format(self.kalive_port_sw1 if device == devices[0]
                                                      else self.kalive_port_sw2))
                net_connect.send_command_timing('vlan {0} name Keep-Alive'.format(self.kalive_vlan))
                net_connect.send_command_timing('untagged ethernet {0}'.format(self.kalive_port_sw1 if device == devices[0]
                                                else self.kalive_port_sw2))
                print("writing memory...")
                net_connect.send_command_timing("write memory")
            return True
        finally:
            pass
