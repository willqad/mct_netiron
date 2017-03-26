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

from netmiko import ConnectHandler
from lib.prep_vars import PrepVars, Vrrpe
from st2actions.runners.pythonrunner import Action


class CreatePim(PrepVars,Vrrpe, Action):

    def __init__(self):
        super(CreatePim, self).__init__()

    def run(self):
        devices = self.mct_devices(self)
        for device in devices:
            net_connect = ConnectHandler(**device)
            net_connect.enable()
            net_connect.config_mode(config_command='configure terminal')
            net_connect.send_command_timing('interface loopback 10')
            net_connect.send_command_timing('port-name PIM ANYCAST')
            if device ==devices[0]:
                net_connect.send_command_timing('ip address 1.32.1.17/32')
            else:
                net_connect.send_command_timing('ip address 1.32.1.18/32')
            net_connect.send_command_timing('ip pim-sparse')
            net_connect.send_command_timing('interface loopback 11')
            net_connect.send_command_timing('port-name PIM ANYCAST')
            net_connect.send_command_timing('ip address 1.32.1.55/32')
            net_connect.send_command_timing('ip pim-sparse')
            net_connect.send_command_timing('ip access-list standard anycast-rp-routers')
            net_connect.send_command_timing('sequence 10 permit host 1.32.1.17')
            net_connect.send_command_timing('sequence 20 permit host 1.32.1.18')
            net_connect.send_command_timing('exit')
            net_connect.send_command_timing('ip multicast-routing')
            net_connect.send_command_timing('rp-address 1.32.1.55')
            net_connect.send_command_timing('anycast-rp 1.32.1.55 anycast-rp-routers')

