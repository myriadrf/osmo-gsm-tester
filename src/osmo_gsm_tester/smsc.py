# osmo_gsm_tester: smsc interface
#
# Copyright (C) 2016-2017 by sysmocom - s.f.m.c. GmbH
#
# Author: Pau Espin Pedrol <pespin@sysmocom.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from . import log, config

class Smsc:

    SMSC_POLICY_CLOSED = 'closed'
    SMSC_POLICY_ACCEPT_ALL = 'accept-all'

    def __init__(self, smpp_addr_port):
        self.addr_port = smpp_addr_port
        self.policy = self.SMSC_POLICY_CLOSED
        self.esmes = []

    def get_config(self):
        values = { 'smsc': { 'policy': self.policy } }
        esme_list = []
        for esme in self.esmes:
            esme_list.append(esme.conf_for_smsc())
        config.overlay(values, dict(smsc=dict(esme_list=esme_list)))
        return values

    def esme_add(self, esme):
        if esme.system_id == '':
            raise log.Error('esme system_id cannot be empty')
        self.esmes.append(esme)
        esme.set_smsc(self)

    def set_smsc_policy(self, smsc_policy):
        self.policy = smsc_policy

# vim: expandtab tabstop=4 shiftwidth=4
