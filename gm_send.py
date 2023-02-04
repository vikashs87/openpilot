#!/usr/bin/env python3
import sys
import time
import argparse
from subprocess import check_output, CalledProcessError
from panda import Panda
from panda.python.uds import UdsClient, MessageTimeoutError, SESSION_TYPE, DTC_GROUP_TYPE
from opendbc.can.packer import CANPacker
from selfdrive.car.gm.gmcan import create_steering_control

panda = Panda()
panda.set_safety_mode(Panda.SAFETY_ALLOUTPUT)
packer = CANPacker("gm_global_a_powertrain_generated")

DT_CTRL = 0.01  # 100Hz
send_rate = DT_CTRL

idx = 0
last_steer_time = 0
last_param_read_time = 0
while True:
  now = time.perf_counter()
  if (now - last_param_read_time) > 1:  # 1 second
    try:
      with open('/data/send_rate', 'r') as f:
        send_rate = float(f.read().strip())
    except:
      pass

  if (now - last_steer_time) > send_rate:
    last_steer_time = now
    counter = idx % 4
    addr, _, dat, bus = create_steering_control(packer, bus=0, apply_steer=0, idx=counter, lkas_active=False)
    panda.can_send(addr, dat, bus)
    idx += 1
