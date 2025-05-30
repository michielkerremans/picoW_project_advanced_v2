import sys
from machine import Pin
from lm_settings import load_SensorArray

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
        sa.sensors[1].measure()
        dic = sa.sensors[1].distance_in_cm
        print("Distance in cm: " + str(dic) + ".\r\n")