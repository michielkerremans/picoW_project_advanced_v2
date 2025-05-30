from lm_sensor import Sensor, SensorArray

def load_SensorArray():
    print("Loading SensorArray...")

    sensor_array = []

    sensor_array.append(Sensor(14, 13))
    sensor_array.append(Sensor(14, 13))
    sensor_array.append(Sensor(14, 13))
    sensor_array.append(Sensor(14, 13))
    sensor_array.append(Sensor(14, 13))

    sa = SensorArray(sensor_array)

    return sa