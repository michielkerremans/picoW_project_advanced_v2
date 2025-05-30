from machine import Pin, UART
from lm_settings import load_SensorArray

uart = UART(0, baudrate = 9600, tx = Pin(0), rx = Pin(1))
uart.init(bits = 8, parity = None, stop = 2)

buffer = ""

sa = load_SensorArray()
for sensor in sa.sensors:
    print(f"Sensor: {sensor}")

def uart_callback(data):
    global buffer, sa
    data = uart.read()
    if data == b'\r':
        print(f"\r")
        #print(f"{buffer}\r")
        uart.write("\r\n") #
        if buffer == "measure":
            sa.sensors[1].measure()
            dic = sa.sensors[1].distance_in_cm
            uart.write("Distance in cm: " + str(dic) + ".\r\n")
        elif buffer == "measure all":
            sa.measure_all()
            md = sa.min_distance
            mdsi = sa.min_distance_sensor_index
            ml = sa.max_length
            uart.write("Min distance in cm: " + str(md) + ".\r\n")
            uart.write("Min distance sensor index: " + str(mdsi) + ".\r\n")
            uart.write("Max length in cm: " + str(ml) + ".\r\n")
        elif buffer == "calibrate all":
            sa.calibrate_all()
            fbd = sa.front_back_diff
            lrd = sa.left_right_diff
            yac = sa.y_axis_calibrated
            xac = sa.x_axis_calibrated
            uart.write("Front-back diff in cm: " + str(fbd) + ".\r\n")
            uart.write("Left-right diff in cm: " + str(lrd) + ".\r\n")
            uart.write("Y-axis calibrated: " + str(yac) + ".\r\n")
            uart.write("X-axis calibrated: " + str(xac) + ".\r\n")
        elif "multishot" in buffer:
            shots = 1
            sb = buffer.split()
            for part in sb:
                if part != "multishot":
                    try:
                        shots = int(part)
                    except TypeError:
                        pass
            print(f"Shots: {shots}")
            sa.update_all(shots)
            amd = sa.average_min_distance
            aml = sa.average_max_length
            uart.write("Average min distance in cm: " + str(amd) + ".\r\n")
            uart.write("Average max length in cm: " + str(aml) + ".\r\n")
        elif "stabilize" in buffer:
            shots = 1
            sb = buffer.split()
            for part in sb:
                if part != "stabilize":
                    try:
                        shots = int(part)
                    except TypeError:
                        pass
            print(f"Shots: {shots}")
            sa.stabilize(shots)
            afbd = sa.average_front_back_diff
            alrd = sa.average_left_right_diff
            uart.write("Average front-back diff in cm: " + str(afbd) + ".\r\n")
            uart.write("Average left-right diff in cm: " + str(alrd) + ".\r\n")
        uart.write("\r\n") #
        buffer = ""
    elif data == b'\x7f': # backspace (Michiel)
        buffer = buffer[:-1]
    else:
        buffer += data.decode('utf-8')


uart.irq(handler = uart_callback, trigger = UART.IRQ_RXIDLE, hard = False)

