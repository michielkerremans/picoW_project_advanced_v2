import sys
from machine import Pin
from lm_settings import load_SensorArray
from lm_sensor import Sensor

# s = Sensor(14, 13, "FRONT")  # FRONT

sa = load_SensorArray()
with open("calibration.txt", "r") as f:
    content = f.read()
if content and content != "":
    for sensor in sa.sensors:
        index = content.find(sensor.id)
        if index != -1:
            end_index = content.find("\n", index)
            sensor.distance_to_floor_in_cm = content[index + len(sensor.id) + 2:end_index].strip()

while True:
    cmd = input("> ")
    if cmd == "exit":
        print("Exiting...")
        sys.exit(0)
    elif cmd == "measure":
        print("Measuring sensor...")
        sa.sensors[0].measure_and_update()
        dic = sa.sensors[0].distance_in_cm
        lic = sa.sensors[0].length_in_cm
        print("Distance in cm: " + str(dic) + ".\r\n")
        print("Length in cm: " + str(lic) + ".\r\n")
    elif cmd == "calibrate": # axis diff doesn't get changed here with new dtfic value -> only in calibrate_all, no writing to file here -> no specific change possible 
        print("Calibrating sensor...")
        sa.sensors[0].calibrate()
        dtfic = sa.sensors[0].distance_to_floor_in_cm
        print("Distance to floor in cm: " + str(dtfic) + ".\r\n")
    elif cmd == "measure all":
        print("Measuring all sensors...")
        sa.measure_all()
        ml = sa.max_length
        mls = sa.max_length_sensor
        if (mls is not None):
            mlsid = mls.id
        print("Max length in cm: " + str(ml) + ".\r\n")
        print("Max length sensor ID: " + str(mlsid) + ".\r\n")
    elif cmd == "calibrate all":
        print("Calibrating all sensors...")
        sa.calibrate_all()
        fbd = sa.front_back_diff
        lrd = sa.left_right_diff
        yac = sa.y_axis_calibrated
        xac = sa.x_axis_calibrated
        if (yac):
            print("Front-back diff in cm: " + str(fbd) + ".\r\n")
        else:
            print("Front-back diff in cm: Not calibrated.\r\n")
        if (xac):
            print("Left-right diff in cm: " + str(lrd) + ".\r\n")
        else:
            print("Left-right diff in cm: Not calibrated.\r\n")
        with open("calibration.txt", "w") as f:
            f.write("")
        for sensor in sa.sensors:
            print(f"{sensor.id}: {sensor.distance_to_floor_in_cm} cm.")
            with open("calibration.txt", "a") as f:
                f.write(f"{sensor.id}: {sensor.distance_to_floor_in_cm}\n")
    elif "multishot" in cmd:
        shots = 3 # Default value
        sc = cmd.split()
        for part in sc:
            if part != "multishot":
                try:
                    shots = int(part)
                except ValueError:
                    pass
        print(f"Shots: {shots}.")
        print("Measuring all sensors multiple times...")
        sa.update_all(shots)
        aml = sa.average_max_length
        print("Average max length in cm: " + str(aml) + ".\r\n")
    elif "stabilize" in cmd:
        shots = 3 # Default value
        sc = cmd.split()
        for part in sc:
            if part != "stabilize":
                try:
                    shots = int(part)
                except ValueError:
                    pass
        print(f"Shots: {shots}.")
        print("Calibrating all sensors multiple times...")
        sa.stabilize(shots)
        afbd = sa.average_front_back_diff
        alrd = sa.average_left_right_diff
        yac = sa.y_axis_calibrated
        xac = sa.x_axis_calibrated
        if (yac):
            print("Average front-back diff in cm: " + str(afbd) + ".\r\n")
        else:
            print("Average front-back diff in cm: Not calibrated.\r\n")
        if (xac):
            print("Average left-right diff in cm: " + str(alrd) + ".\r\n")
        else:
            print("Average left-right diff in cm: Not calibrated.\r\n")
        with open("calibration.txt", "w") as f:
            f.write("")
        for sensor in sa.sensors:
            print(f"{sensor.id}: {sensor.distance_to_floor_in_cm} cm.")
            with open("calibration.txt", "a") as f:
                f.write(f"{sensor.id}: {sensor.distance_to_floor_in_cm}\n")
