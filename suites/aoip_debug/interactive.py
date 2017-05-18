#!/usr/bin/env python3
from osmo_gsm_tester.test import *
hlr = suite.hlr()
bts = suite.bts()
mgcpgw = suite.mgcpgw(bts_ip=bts.remote_addr())
msc = suite.msc(hlr, mgcpgw)
bsc = suite.bsc(msc)
modems = suite.modems(int(prompt('How many modems?')))

hlr.start()
msc.start()

bsc.bts_add(bts)
bsc.start()

bts.start()

for m in modems:
  hlr.subscriber_add(m)
  m.connect(bsc)

while True:
  cmd = prompt('Enter command: (q)uit (s)ms (g)et-registered (w)ait-registered')
  cmd = cmd.strip().lower()

  if not cmd:
    continue
  if 'quit'.startswith(cmd):
    break
  elif 'wait-registered'.startswith(cmd):
    try:
      wait(msc.subscriber_attached, *modems)
    except Timeout:
      print('Timeout while waiting for registration.')
  elif 'get-registered'.startswith(cmd):
    print(msc.imsi_list_attached())
    print('RESULT: %s' %
       ('All modems are registered.' if msc.subscriber_attached(*modems)
        else 'Some modem(s) not registered yet.'))
  elif 'sms'.startswith(cmd):
    for mo in modems:
      for mt in modems:
        mo.sms_send(mt.msisdn, 'to ' + mt.name())
