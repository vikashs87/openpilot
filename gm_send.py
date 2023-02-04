#!/usr/bin/env python3
import os
import sys
import time
import argparse
from subprocess import check_output, CalledProcessError
from panda import Panda
from panda.python.uds import UdsClient, MessageTimeoutError, SESSION_TYPE, DTC_GROUP_TYPE
from opendbc.can.packer import CANPacker
from selfdrive.car.gm.gmcan import create_steering_control

panda = Panda()
panda.set_safety_mode(Panda.SAFETY_ALLOUTPUT, 1)
packer = CANPacker("gm_global_a_powertrain_generated")

DT_CTRL = 0.01  # 100Hz
send_rate = DT_CTRL

recv_rate = .5  # 2Hz

idx = 0
last_steer_time = 0
last_param_read_time = 0
last_can_recv_time = 0
last_send_one_fast = True

temp_send_msgs = 0
temp_send_rate = (1 / 1000)  # 3ms faults, 4ms faults, 5ms took 4 to fault, testing 6ms

while True:
  now = time.perf_counter()
  if (now - last_param_read_time) > 3:  # 1 second
    last_param_read_time = now
    try:
      with open('/data/send_rate', 'r') as f:
        send_rate = float(f.read().strip())
    except:
      pass

    try:
      with open('/data/temp_send_rate', 'r') as f:
        temp_send_rate = float(f.read().strip())
    except:
      pass

  _send_rate = send_rate
  if temp_send_msgs != 0:
    _send_rate = temp_send_rate
  if (now - last_steer_time) > _send_rate:
    temp_send_msgs = max(0, temp_send_msgs - 1)
    last_steer_time = now
    counter = idx % 4
    addr, _, dat, bus = create_steering_control(packer, bus=0, apply_steer=0, idx=counter, lkas_active=False)
    panda.can_send(addr, dat, bus)
    idx += 1
    send_one_fast = os.path.exists('/data/send_one_fast')
    if send_one_fast and not last_send_one_fast:
      temp_send_msgs = 1
      #time.sleep(3 / 1000)
      #counter = idx % 4
      #addr, _, dat, bus = create_steering_control(packer, bus=0, apply_steer=0, idx=counter, lkas_active=False)
      #panda.can_send(addr, dat, bus)
      #idx += 1
    last_send_one_fast = send_one_fast

  if (now - last_can_recv_time) > recv_rate:
    last_can_recv_time = now
    msgs = panda.can_recv()
    for address, _, dat, bus in msgs:
      if address == 388 and bus == 0:
        torque_delivered_status = (dat[0] >> 3) & 0x7
        if torque_delivered_status == 3:
          print("LKAS FAULT! SENT:", idx)
