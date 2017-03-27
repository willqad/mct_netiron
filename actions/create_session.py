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

__all__ = [
    'SessionRun'
]


class SessionRun(PrepVars):

    def __init__(self, config=None):
        super(SessionRun, self).__init__(config=config)

    def run(self):
        devices = self.mct_devices()
        for device in devices:
            net_connect = ConnectHandler(**device)
            net_connect.enable()
            net_connect.config_mode(config_command='config terminal')
            net_connect.send_command_timing('no route-only')
            # ##### Enabling ICL Ports #####
            print("enabling ICL Ports...")
            net_connect.send_command_timing('interface ethernet {0}'.format(self.icl1_sw1 if device == devices[0]
                                            else self.icl1_sw2))
            net_connect.send_command_timing('enable')
            net_connect.send_command_timing('no span')
            if len(self.session_list) > 5:
                net_connect.send_command_timing('interface ethernet {0}'.format(self.icl2_sw1 if device == devices[0]
                                                else self.icl2_sw2))
                net_connect.send_command_timing('enable')
                net_connect.send_command_timing('no span')
            else:
                continue
            if device == devices[0]:
                net_connect.send_command_timing('interface e {0}'.format(self.icl1_sw1))
                net_connect.send_command_timing('enable')
                net_connect.send_command_timing('exit')
                net_connect.send_command_timing('interface e {0}'.format(self.icl2_sw1))
                net_connect.send_command_timing('enable')
                net_connect.send_command_timing('exit')
            else:
                net_connect.send_command_timing('interface e {0}'.format(self.icl1_sw2))
                net_connect.send_command_timing('enable')
                net_connect.send_command_timing('exit')
                net_connect.send_command_timing('interface e {0}'.format(self.icl2_sw2))
                net_connect.send_command_timing('enable')
                net_connect.send_command_timing('exit')
            # ##### Create Link-Aggregation #####
            print("creating ICL link-aggregation...")
            net_connect.send_command_timing('lag ICL dynamic id 1')
            if len(self.session_list) > 5:
                net_connect.send_command_timing('ports ethernet {0} ethernet {1}'.format(self.icl1_sw1 if device ==
                                                devices[0] else self.icl1_sw2, self.icl2_sw1 if device == devices[0]
                                                else self.icl2_sw2))
                net_connect.send_command_timing('deploy')
                net_connect.send_command_timing(' port-name "To MCT peer" ethernet {0}'.format(self.icl1_sw1
                                                if device == devices[0] else self.icl1_sw2))
            else:
                net_connect.send_command_timing('ports ethernet{0}'.format(self.icl1_sw1 if device == devices[0]
                                                else self.icl1_sw2))
                net_connect.send_command_timing('primary-port {0}'.format(self.icl1_sw1 if device == devices[0]
                                                                          else self.icl1_sw2))
                net_connect.send_command_timing('deploy')
                net_connect.send_command_timing(' port-name "To MCT peer" ethernet{0}'.format(self.icl1_sw1
                                                if device == devices[0] else self.icl1_sw2))
            # ##### Tag Session Vlan #####
            print("tagging session vlan on ICL...")
            net_connect.send_command_timing('vlan {0} name Session-Vlan'.format(self.session_vlan))
            net_connect.send_command_timing('tagged ethernet {0}'.format(self.icl1_sw1 if device == devices[0]
                                                                         else self.icl1_sw2))
            net_connect.send_command_timing('router-interface ve {0}'.format(self.session_vlan))
            net_connect.send_command_timing('no spanning-tree')
            # ##### Tag the rest of the Vlans #####
            print ("tagging the rest of vlans on ICL...")
            for vlan in self.vlans():
                net_connect.send_command_timing('vlan {0}'.format(vlan))
                net_connect.send_command_timing('tagged e{0}'.format(self.icl1_sw1 if device == devices[0]
                                                                     else self.icl1_sw2))
                net_connect.send_command_timing('router-interface ve {0}'.format(vlan))
                net_connect.send_command_timing('no spanning-tree')
            # ##### assign the IP addresses for Ves #####
            print("assigning IP addresses for session virtual interface...")
            session_ips = self.sessionips()
            net_connect.send_command_timing('interface ve {0}'.format(self.session_vlan))
            net_connect.send_command_timing('ip address {0} {1}'.format(session_ips['session_ip1'] if device==devices[0]
                                            else session_ips['session_ip2'], self.session_subnet))
            print("writing memory...")
            net_connect.send_command_timing('write memory')
            return True, "Configuration of Session Vlan and lags has been done"
