from machine import Pin, time_pulse_us
import utime

# Pin configuration
# Shared trigger pin for all sensors
TRIG_PIN = 2        # Physical pin 4 - shared trigger for all sensors

# Echo pins for all 5 sensors
ECHO_PIN_1 = 3      # Physical pin 5 - original sensor
ECHO_PIN_2 = 4      # New sensor
ECHO_PIN_3 = 5      # New sensor
ECHO_PIN_4 = 7      # New sensor
ECHO_PIN_5 = 8      # New sensor

CALIBRATE_BUTTON_PIN = 6  # Physical pin 9 - Button to calibrate the sensor
STATUS_LED_PIN = 10       # Physical pin 14 - LED to indicate program status

# Setup shared Trig pin
trig = Pin(TRIG_PIN, Pin.OUT)

# Setup Echo pins for all sensors
sensors = []
for i, echo_pin in enumerate([ECHO_PIN_1, ECHO_PIN_2, ECHO_PIN_3, ECHO_PIN_4, ECHO_PIN_5]):
    sensors.append({
        'id': i + 1,
        'echo': Pin(echo_pin, Pin.IN),
        'calibration': None
    })

calibration_button = Pin(CALIBRATE_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
status_led = Pin(STATUS_LED_PIN, Pin.OUT)

# Flash file to store calibration for all sensors
CALIBRATION_FILE = "calibration.txt"

def measure_distance(sensor):
    """Measure distance using the specified sensor"""
    # Ensure Trig is low
    trig.low()
    utime.sleep_us(10)
    
    # Send 10us pulse to Trig
    trig.high()
    utime.sleep_us(10)
    trig.low()
    
    # Measure the flight time of the Echo signal
    pulse_duration = time_pulse_us(sensor['echo'], 1, 30000)  # Timeout after 30ms
    
    # Calculate distance in millimeters
    distance_mm = (pulse_duration * 0.343) / 2  # divide by 2 for one-way distance
    return distance_mm

def send_packet(sensor_id, length, variation=0, status_code=0):
    """Send a packet with sensor ID and measurement data"""
    # Format packet with sensor ID included
    packet = f"\x0AS{sensor_id} L{int(length)} V{int(variation)} S{int(status_code)}\x0D"
    print(packet)  # Send packet over the serial connection

def save_calibration_to_flash():
    """Save calibration distances for all sensors to flash memory."""
    with open(CALIBRATION_FILE, "w") as f:
        for sensor in sensors:
            # Store calibration as sensor_id:calibration_value
            f.write(f"{sensor['id']}:{sensor['calibration'] or 0}\n")

def load_calibration_from_flash():
    """Load calibration distances for all sensors from flash memory."""
    try:
        with open(CALIBRATION_FILE, "r") as f:
            lines = f.readlines()
            for line in lines:
                if ':' in line:
                    sensor_id, cal_value = line.strip().split(':')
                    sensor_id = int(sensor_id)
                    cal_value = float(cal_value)
                    
                    # Only set if value is valid (non-zero)
                    if cal_value > 0 and 1 <= sensor_id <= len(sensors):
                        sensors[sensor_id-1]['calibration'] = cal_value
                        print(f"Loaded calibration for sensor {sensor_id}: {cal_value:.2f} mm")
    except (OSError, ValueError):
        print("No calibration found. Starting fresh.")

def flash_led(pattern):
    """Indicate a pattern on the LED."""
    for on_time, off_time in pattern:
        status_led.on()
        utime.sleep(on_time)
        status_led.off()
        utime.sleep(off_time)

def button_pressed(pin):
    """Callback for calibration button press."""
    # Calibrate all sensors when button is pressed
    all_valid = True
    
    # First, measure all distances
    for sensor in sensors:
        distance = measure_distance(sensor)
        if distance > 0:  # Valid distance
            sensor['calibration'] = distance
            print(f"Sensor {sensor['id']} calibration set to: {distance:.2f} mm")
        else:
            all_valid = False
            print(f"Sensor {sensor['id']} calibration failed")
    
    # Save calibrations if all were valid
    if all_valid:
        save_calibration_to_flash()
        # Indicate successful calibration with a double blink
        flash_led([(0.2, 0.2), (0.2, 0.2)])
    else:
        # Indicate partial success with a different pattern
        flash_led([(0.2, 0.2), (0.2, 0.2), (0.5, 0.5)])

# Attach interrupt to the button
calibration_button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

# Load calibration from flash on startup
load_calibration_from_flash()

# Main loop
while True:
    try:
        # Measure all sensors sequentially
        for sensor in sensors:
            current_distance = measure_distance(sensor)
            
            if sensor['calibration'] is not None:
                difference = sensor['calibration'] - current_distance
                send_packet(sensor['id'], length=difference)
                print(f"Sensor {sensor['id']} Distance: {current_distance:.2f} mm, Difference: {difference:.2f} mm")
            else:
                print(f"Sensor {sensor['id']} Distance: {current_distance:.2f} mm (No calibration set)")
                send_packet(sensor['id'], length=0, status_code=-4)  # Could not measure error
            
            # Important: add larger delay between sensor readings when using a shared trigger
            # This ensures echo signals don't interfere with each other
            utime.sleep_ms(100)
            
        # Normal operation: Single blink
        flash_led([(0.2, 1.8)])
        
    except OSError as exc:
        print("Measurement failed:", exc)
        # Send error for all sensors
        for sensor in sensors:
            send_packet(sensor['id'], length=0, status_code=-1)  # Unknown error
        
        # Error state: Rapid blink
        flash_led([(0.1, 0.1)] * 5)
        
    # Add a small delay between measurement cycles
    utime.sleep_ms(200)