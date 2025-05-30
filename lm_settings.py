from lm_sensor import Sensor, SensorArray

def load_SensorArray():
    print("Loading SensorArray...")

    sensor_array = []

    sensor_array.append(Sensor(14, 13, "FRONT")) # FRONT
    sensor_array.append(Sensor(20, 21, "LEFT")) # LEFT
    sensor_array.append(Sensor(10, 11, "MIDDLE")) # MIDDLE
    sensor_array.append(Sensor(8, 7, "RIGHT")) # RIGHT
    sensor_array.append(Sensor(3, 2, "BACK")) # BACK

    sa = SensorArray(sensor_array)

    return sa