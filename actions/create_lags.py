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


class CreateLag(PrepVars):

    def __init__(self, config=None):
        super(CreateLag, self).__init__(config=config)
        self.sw1p, self.sw2p = self.lags().__getitem__(0), self.lags().__getitem__(1)
        self.tvlans, self.utvlans = self.lags_vlans().__getitem__(1), self.lags_vlans().__getitem__(2)
        self.pnames = self.lags_vlans().__getitem__(0)

    def run(self):
        devices = self.mct_devices()

        for device in devices:
            net_connect = ConnectHandler(**device)
            net_connect.enable()
            net_connect.config_mode(config_command='config terminal')
            # ##### create lag ports #####
            for (port, name, idno) in zip(self.sw1p if device == devices[0] else self.sw2p, self.pnames,
                                          range(10, 10 + len(self.pnames))):
                print("creating CCEP on port {0}...".format(port))
                net_connect.send_command_timing((' lag {0} dynamic id {1}'.format(name, idno)))
                net_connect.send_command_timing('ports ethernet {0}'.format(port))
                net_connect.send_command_timing('primary-port {0}'.format(port))
                net_connect.send_command_timing('deploy')

            for key, port in zip(self.tvlans, self.sw1p if device == devices[0] else self.sw2p):
                if self.tvlans[key]:
                    for vlan in self.vlans[key]:
                        print ("tagging ports on vlan {0}...".format(vlan))
                        net_connect.send_command_timing('vlan {0}'.format(vlan))
                        net_connect.send_command_timing('tagged e{0}'.format(port))
                        net_connect.send_command_timing('no spanning-tree')
                else:
                    pass
            for port in zip(self.sw1p if device == devices[0] else self.sw2p):
                print('enabling ports...')
                net_connect.send_command_timing('interface e {0}'.format(port))
                net_connect.send_command_timing('enable')
                net_connect.send_command_timing('exit')
            print("writing memory...")
            net_connect.send_command_timing('write memory')
            return True
