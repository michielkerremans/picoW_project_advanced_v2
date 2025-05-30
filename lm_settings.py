from lm_sensor import Sensor, SensorArray

def load_SensorArray():
    sensor_array = []

    sensor_array.append(Sensor(2, 3))
    sensor_array.append(Sensor(2, 3))
    sensor_array.append(Sensor(2, 3))
    sensor_array.append(Sensor(2, 3))
    sensor_array.append(Sensor(2, 3))

    sa = SensorArray(sensor_array)

    return sa