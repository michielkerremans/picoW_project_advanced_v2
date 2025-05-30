import sys
from machine import Pin
from lm_settings import load_SensorArray
from lm_sensor import Sensor

s = Sensor(14, 13)

sa = load_SensorArray()
for sensor in sa.sensors:
    print(f"Sensor: {sensor.distance_in_cm} cm.")

while True:
    cmd = input("> ")
    if cmd == "exit":
        print("Exiting...")
        sys.exit(0)
    elif cmd == "measure":
        print("Measuring distance...")
        s.measure()
        sa.sensors[1].measure()
        dic = sa.sensors[1].distance_in_cm
        print("Distance in cm: " + str(s.distance_in_cm) + ".\r\n")
    elif cmd == "measure all":
        print("Measuring all sensors...")
        for sensor in sa.sensors:
            sensor.measure()
            print(f"Sensor {sensor.id}: {sensor.distance_in_cm} cm.")