from picozero import DistanceSensor
from time import sleep

class Sensor: # geen overerving van DistanceSensor want fout mbt verplichte definitie _pin_nums -> kan later nog
    id = "none"

    def __init__(self, echo_pin, trigger_pin, num_of_shots = 1, delay = 0.3, max_distance_in_cm = 300):
        self.num_of_shots = num_of_shots
        self.delay = delay
        self.max_distance_in_cm = max_distance_in_cm
        if type(echo_pin) is int and type(trigger_pin) is int: 
            self.ds = DistanceSensor(echo = echo_pin, trigger = trigger_pin, max_distance = 3)
            try:
                self.ds.distance
            except Exception as e:
                print(f"Error while trying to measure distance with given parameters: {e}.")
                raise  # fout opnieuw gegooid -> instantie niet aangemaakt
            self.id = str(id)
        else:
            raise TypeError("Parameters echo_pin en trigger_pin have to be of type 'int'.")

    delay = 0.3

    def _distance_in_cm(self):
        sleep(self.delay)
        distance = self.ds.distance
        if distance is None:
            return -1 # No distance measured, return -1 to indicate error
        elif distance * 100 > self.max_distance_in_cm:
            return -2 # Distance exceeds maximum, return -2 to indicate error
        else:
            return distance * 100

    num_of_shots = 1

    def _average_distance_in_cm(self):
        measured = False
        distance = 0
        for _ in range(self.num_of_shots):
            ds = self._distance_in_cm()
            if ds > -1:
                measured = True
                distance += ds / self.num_of_shots # Average distance
        return distance if measured else -3 # No valid measurements, return -3 to indicate error

    @property
    def distance_in_cm(self): # Same as ds.distance, but with averaging over multiple shots and error handling
        if self.num_of_shots == 1:
            return self._distance_in_cm()
        else:
            return self._average_distance_in_cm()

    max_distance_in_cm = 300
    distance_to_floor_in_cm = max_distance_in_cm  # Default value

    def calibrate(self):
        self.distance_to_floor_in_cm = self.max_distance_in_cm  # Reset to default value
        distance = self.distance_in_cm
        if distance > 0 and distance <= self.max_distance_in_cm:
            self.distance_to_floor_in_cm = distance

    length_in_cm = 0

    def measure(self):
        distance = self.distance_in_cm
        if distance > -1: # 0 is a valid distance, -1 is an error
            self.length_in_cm = self.distance_to_floor_in_cm - distance
        else:
            self.length_in_cm = distance # Error handling: if distance is -1 or -2 or -3

class SensorArray:
    sensors = []
    sensor_id = 0

    def add(self, sensor):
        if isinstance(sensor, Sensor):
            self.sensor_id += 1
            sensor.id = f"{self.sensor_id}"
            self.sensors.append(sensor)
        else:
            raise TypeError("Parameter has to be of type 'Sensor'.")

    max_length = 0
    max_length_id = None

    def measure(self):
        self.max_length = -1  # Initialize to -1 to indicate no valid measurements yet
        self.max_length_id = None
        for sensor in self.sensors:
            sensor.measure()
            if sensor.length_in_cm > self.max_length:
                self.max_length = sensor.length_in_cm
                self.max_length_id = sensor.id
        self.print_measurements()

    measurements_file = "measurements.txt"

    def print_measurements(self):
        buffer = []
        buffer.append("Measurements:")
        buffer.append(f"Number of sensors: {len(self.sensors)}")
        for sensor in self.sensors:
            buffer.append(f"Sensor ID: {sensor.id}, Length: {sensor.length_in_cm:.2f} cm")
        buffer.append("Maximum Length:")
        buffer.append(f"Sensor ID: {self.max_length_id}, Length: {self.max_length:.2f} cm")
        try:
            with open(self.measurements_file, "w") as f:
                f.write("\n".join(buffer))
        except:
            print('\n'.join(buffer))

    front_back_diff = -1
    left_right_diff = -1

    def calibrate(self):
        calibrated = True # Assume all sensors calibrate successfully
        for sensor in self.sensors:
            sensor.calibrate()
            if sensor.distance_to_floor_in_cm < 0:
                calibrated = False # Calibration failed for at least one sensor
        if calibrated and len(self.sensors) == 5:
            self.front_back_diff = self.sensors[0].distance_to_floor_in_cm - self.sensors[4].distance_to_floor_in_cm
            self.left_right_diff = self.sensors[1].distance_to_floor_in_cm - self.sensors[3].distance_to_floor_in_cm
        self.print_calibration()

    calibration_file = "calibration.txt"

    def print_calibration(self):
        buffer = []
        buffer.append("Calibration:")
        buffer.append(f"Number of sensors: {len(self.sensors)}")
        for sensor in self.sensors:
            buffer.append(f"Sensor ID: {sensor.id}, Distance to floor: {sensor.distance_to_floor_in_cm:.2f} cm")
        if self.front_back_diff != -1 and self.left_right_diff != -1:
            buffer.append(f"Front-Back Difference: {self.front_back_diff:.2f} cm")
            buffer.append(f"Left-Right Difference: {self.left_right_diff:.2f} cm")
        else:
            buffer.append("Calibration failed or not enough sensors.")
        try:
            with open(self.calibration_file, "w") as f:
                f.write("\n".join(buffer))
        except:
            print('\n'.join(buffer))