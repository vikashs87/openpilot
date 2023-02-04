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

DT_CTRL = 0.01

idx = 0
while True:
  counter = idx % 4
  addr, _, dat, bus = create_steering_control(packer, bus=0, apply_steer=0, idx=counter, lkas_active=False)
  panda.can_send(addr, dat, bus)
  idx += 1

  time.sleep(DT_CTRL)
