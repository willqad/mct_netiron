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
from lib.prep_vars import Vrrpe,PrepVars


class CreateVrrpe(Vrrpe, PrepVars):

    def __init__(self, config=None):
        super(CreateVrrpe, self).__init__(config=config)

    def run(self):
        vrrpe = self.vdetails()
        devices = self.mct_devices()

        for device in devices:
            print('connecting to device...')
            net_connect = ConnectHandler(**device)
            print('connection successful')
            net_connect.enable()
            net_connect.config_mode(config_command='config terminal')
            net_connect.send_command_timing('router vrrp-extended')
            if device == devices[0]:
                for ve, subnet, ip, vip in zip(vrrpe['ve'], vrrpe['subnet'], vrrpe['sw1ip'], vrrpe['ip']):
                    print('configuring ve {0} and vrrp-e...'.format(ve))
                    net_connect.send_command_timing('interface ve {0}'.format(ve))
                    net_connect.send_command_timing('ip address {0}{1}'.format(ip,subnet))
                    net_connect.send_command_timing('ip vrrp-extended vrid {0}'.format(ve))
                    net_connect.send_command_timing('backup priority 110')
                    net_connect.send_command_timing('ip address {0}'.format(vip))
                    net_connect.send_command_timing('advertise backup')
                    net_connect.send_command_timing('short-path-forwarding')
                    net_connect.send_command_timing('activate')
            else:
                for ve, subnet, ip, vip in zip(vrrpe['ve'], vrrpe['subnet'], vrrpe['sw2ip'], vrrpe['ip']):
                    print('configuring ve {0} and vrrp-e...'.format(ve))
                    net_connect.send_command_timing('interface ve {0}'.format(ve))
                    net_connect.send_command_timing('ip address {0}{1}'.format(ip,subnet))
                    net_connect.send_command_timing('ip vrrp-extended vrid {0}'.format(ve))
                    net_connect.send_command_timing('backup priority 100')
                    net_connect.send_command_timing('ip address {0}'.format(vip))
                    net_connect.send_command_timing('advertise backup')
                    net_connect.send_command_timing('short-path-forwarding')
                    net_connect.send_command_timing('activate')
            print('configuring vrrp-e done...')
            print('writing memory...')
            net_connect.send_command_timing('writing memory...')
        return True
