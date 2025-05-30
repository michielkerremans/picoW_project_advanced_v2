from picozero import DistanceSensor
from time import sleep

class Sensor: # geen overerving van DistanceSensor want fout mbt verplichte definitie _pin_nums -> kan later nog
    distance_in_cm = 0
    distance_to_floor_in_cm = 300
    length_in_cm = 0
   
    def __init__(self, echo_pin, trigger_pin):
        if type(echo_pin) is int and type(trigger_pin) is int: 
            self.ds = DistanceSensor(echo = echo_pin, trigger = trigger_pin, max_distance = 3)
            try:
                self.ds.distance
            except Exception as e:
                print(f"Error while trying to measure distance with given parameters: {e}.")
                raise  # fout opnieuw gegooid -> instantie niet aangemaakt
                #del self
                #print(f"Didn't find a distance sensor for given parameters (echo_pin & trigger_pin).")
        else:
            raise TypeError("Parameters echo_pin en trigger_pin have to be of type 'int'.")
            #del self
            #print(f"Sensor object deleted, parameters (echo_pin & trigger_pin) have to be of type int.")
    
    def measure(self):
        sleep(0.3)
        self.distance_in_cm = self.ds.distance * 100
        
    def calibrate(self):
        sleep(0.3)
        self.distance_to_floor_in_cm = self.ds.distance * 100
        
    def update(self):
        self.length_in_cm = self.distance_to_floor_in_cm - self.distance_in_cm
        
    def measure_and_update(self):
        self.measure()
        self.update()

class SensorArray:
    min_distance = 0
    min_distance_sensor = 0
    min_distance_sensor_index = 0
    max_length = 0
    left_right_diff = 0
    front_back_diff = 0
    x_axis_calibrated = False
    y_axis_calibrated = False
    average_min_distance = 0
    average_max_length = 0
    average_left_right_diff = 0
    average_front_back_diff = 0
    
    def __init__(self, sensor_array):
        if type(sensor_array) is list:
            if all(type(item) is Sensor for item in sensor_array):
                self.sensors = sensor_array
            else:
                raise TypeError("List elements of parameter all have to be of type 'Sensor'.")
                #del self
                #print(f"SensorArray object deleted, list elements were not all of type Sensor.")
        elif type(sensor_array) is Sensor:
            self.sensors = [sensor_array]
        else:
            raise TypeError("Parameter has to be of type 'Sensor'.")
            #del self
            #print(f"SensorArray object deleted, given parameter type was not Sensor.")
        
    def measure_all(self):
        i = 0
        for sensor in self.sensors:
            print(f"Index: {i}")
            print(f"Sensor: {sensor}")
            sensor.measure_and_update()
            print(f"Distance in cm: {sensor.distance_in_cm}")
            print(f"Length in cm: {sensor.length_in_cm}")
            if i == 0 or sensor.distance_in_cm < self.min_distance:
                self.min_distance = sensor.distance_in_cm
                self.min_distance_sensor = sensor
                self.min_distance_sensor_index = i
                self.max_length = sensor.length_in_cm
            print(f"New min distance: {self.min_distance}")
            i += 1

    def calibrate_all(self):
        for sensor in self.sensors:
            sensor.calibrate()
            print(f"{sensor.distance_to_floor_in_cm}")
        # normaal verandert aantal sensors van object niet (probleem bij lager aantal), maar voor de zekerheid:
        self.front_back_diff = 0
        self.left_right_diff = 0
        self.y_axis_calibrated = False
        self.x_axis_calibrated = False
        if len(self.sensors) > 1:
            self.front_back_diff = self.sensors[0].distance_to_floor_in_cm - self.sensors[len(self.sensors) - 1].distance_to_floor_in_cm
            self.y_axis_calibrated = True
            if len(self.sensors) > 3:
                self.left_right_diff = self.sensors[1].distance_to_floor_in_cm - self.sensors[len(self.sensors) - 2].distance_to_floor_in_cm
                self.x_axis_calibrated = True
            
    def update_all(self, shots):
        if type(shots) is int and shots != 0:
            total_min_distance = 0
            total_max_length = 0
            for s in range(shots):
                self.measure_all()
                total_min_distance += self.min_distance
                total_max_length += self.max_length
            self.average_min_distance = total_min_distance / shots
            self.average_max_length = total_max_length / shots
        else:
            print(f"Parameter 'shots' has to be an int and not 0.")
            
    def stabilize(self, shots):
        if type(shots) is int and shots != 0:
            total_front_back_diff = 0
            total_left_right_diff = 0
            for s in range(shots):
                self.calibrate_all()
                total_front_back_diff += self.front_back_diff
                total_left_right_diff += self.left_right_diff
            self.average_front_back_diff = total_front_back_diff / shots
            self.average_left_right_diff = total_left_right_diff / shots
        else:
            print(f"Parameter 'shots' has to be an int and not 0.")
