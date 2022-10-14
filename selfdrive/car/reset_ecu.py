from selfdrive.car.isotp_parallel_query import IsoTpParallelQuery
from system.swaglog import cloudlog


def reset_ecu(logcan, sendcan, bus=0, addr=0x7d0, timeout=0.1, debug=False):
  # ON GMLAN: This will only work if vehicle speed is 0 and engine is off
  cloudlog.warning(f"ecu reset {hex(addr)} ...")

  # $AE - DeviceControl Request SID
  # $FD - Gateway devices  # try $FE
  # $40 - ECU reset
  request = b"\xae\xfd\x40"

  query = IsoTpParallelQuery(sendcan, logcan, bus, [addr], [request], [b""], debug=debug)
  print(query.get_data(timeout))


if __name__ == "__main__":
  import time
  import cereal.messaging as messaging
  sendcan = messaging.pub_sock('sendcan')
  logcan = messaging.sub_sock('can')
  time.sleep(0.2)

  # GM EPS
  addr = 0x642 - 0x400

  reset_ecu(logcan, sendcan, bus=0, addr=addr, timeout=0.5, debug=True)
