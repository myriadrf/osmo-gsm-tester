# osmo_gsm_tester: specifics for running an osmo-bsc
#
# Copyright (C) 2016-2017 by sysmocom - s.f.m.c. GmbH
#
# Author: Neels Hofmeyr <neels@hofmeyr.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import pprint

from . import log, util, config, template, process, osmo_ctrl, pcap_recorder

class OsmoBsc(log.Origin):
    suite_run = None
    ip_address = None
    run_dir = None
    config_file = None
    process = None
    bts = None
    encryption = None
    mgw = None

    def __init__(self, suite_run, msc, mgw, ip_address):
        super().__init__(log.C_RUN, 'osmo-bsc_%s' % ip_address.get('addr'))
        self.suite_run = suite_run
        self.ip_address = ip_address
        self.bts = []
        self.msc = msc
        self.mgw = mgw

    def start(self):
        self.log('Starting osmo-bsc')
        self.run_dir = util.Dir(self.suite_run.get_test_run_dir().new_dir(self.name()))
        self.configure()

        inst = util.Dir(os.path.abspath(self.suite_run.trial.get_inst('osmo-bsc')))

        binary = inst.child('bin', 'osmo-bsc')
        if not os.path.isfile(binary):
            raise RuntimeError('Binary missing: %r' % binary)
        lib = inst.child('lib')
        if not os.path.isdir(lib):
            raise RuntimeError('No lib/ in %r' % inst)

        iface = util.ip_to_iface(self.addr())
        pcap_recorder.PcapRecorder(self.suite_run, self.run_dir.new_dir('pcap'), iface,
                                   'host %s and port not 22' % self.addr())

        env = { 'LD_LIBRARY_PATH': util.prepend_library_path(lib) }

        self.dbg(run_dir=self.run_dir, binary=binary, env=env)
        self.process = process.Process(self.name(), self.run_dir,
                                       (binary, '-c',
                                        os.path.abspath(self.config_file)),
                                       env=env)
        self.suite_run.remember_to_stop(self.process)
        self.process.launch()

    def configure(self):
        self.config_file = self.run_dir.new_file('osmo-bsc.cfg')
        self.dbg(config_file=self.config_file)

        values = dict(bsc=config.get_defaults('bsc'))
        config.overlay(values, self.suite_run.config())
        config.overlay(values, dict(bsc=dict(ip_address=self.ip_address)))
        config.overlay(values, self.mgw.conf_for_client())

        bts_list = []
        for bts in self.bts:
            bts_list.append(bts.conf_for_bsc())
        config.overlay(values, dict(bsc=dict(net=dict(bts_list=bts_list))))

        # runtime parameters:
        if self.encryption is not None:
            encryption_vty = util.encryption2osmovty(self.encryption)
        else:
            encryption_vty = util.encryption2osmovty(values['bsc']['net']['encryption'])
        config.overlay(values, dict(bsc=dict(net=dict(encryption=encryption_vty))))

        self.dbg('BSC CONFIG:\n' + pprint.pformat(values))

        with open(self.config_file, 'w') as f:
            r = template.render('osmo-bsc.cfg', values)
            self.dbg(r)
            f.write(r)

    def addr(self):
        return self.ip_address.get('addr')

    def set_encryption(self, val):
        self.encryption = val

    def bts_add(self, bts):
        self.bts.append(bts)
        bts.set_bsc(self)

    def running(self):
        return not self.process.terminated()

# vim: expandtab tabstop=4 shiftwidth=4
