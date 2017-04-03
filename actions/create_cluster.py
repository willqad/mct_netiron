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


class CreateCluster(PrepVars):
    def __init__(self, config=None):
        super(CreateCluster, self).__init__(config=config)

    def run(self):
        names = self.vlans().__getitem__(0)
        sw1p, sw2p = self.lags().__getitem__(0), self.lags().__getitem__(1)
        devices = self.mct_devices()
        peers = self.sessionips()
        for device in devices:
            net_connect = ConnectHandler(**device)
            net_connect.enable()
            net_connect.config_mode(config_command='configure terminal')
            print("creating MCT cluster on ID 1...")
            net_connect.send_command_timing('cluster "MCT" 1')
            net_connect.send_command_timing('rbridge-id {0}'.format("1" if device == devices[0] else "2"))
            net_connect.send_command_timing('session-vlan {0}'.format(self.session_vlan))
            net_connect.send_command_timing('keep-alive-vlan {0}'.format(self.kalive_vlan))
            for vlan in self.vlans():
                net_connect.send_command_timing('member-vlan {0}'.format(vlan))
            net_connect.send_command_timing('icl ICL ethernet {0}'.format(self.icl1_sw1 if device ==
                                                                    devices[0]else self.icl1_sw2))
            net_connect.send_command_timing('peer {0} rbridge-id {1} icl ICL'.
                                            format(peers['session_ip2'] if device == devices[0]
                                            else peers['session_ip1'], "2" if device == devices[1]
                                            else "1"))
            net_connect.send_command_timing('deploy')

            # ##### Creating and deploying clients #####
            for name, port, rid in zip(names, sw1p if device == devices[0] else sw2p,
                                       range(10, 10 + len(sw1p))):
                print("creating client {0}...".format(name))
                net_connect.send_command_timing('client "{0}" ethernet {1}'.format(name, port))
                net_connect.send_command_timing('rbridge-id {0}'.format(rid))
                net_connect.send_command_timing('deploy')
            print("writing memory...")
            net_connect.send_command_timing('write memory')
