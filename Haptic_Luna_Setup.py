import RPi.GPIO as GPIO
import time
import serial
import config

# Haptic motor setup
HAPTIC_PIN = 27  # GPIO pin for the haptic motor
GPIO.setmode(GPIO.BCM)
GPIO.setup(HAPTIC_PIN, GPIO.OUT)
pwm = GPIO.PWM(HAPTIC_PIN, 100)  # PWM on the haptic motor pin at 100 Hz
pwm.start(0)  # Start with 0% duty cycle (off)

# Initialize the serial port for TF-Luna
ser = serial.Serial("/dev/serial0", 115200, timeout=0)  # Mini UART serial device

# Haptic Sensor Functions -------------------------------------------------------------------------------------

kill_Luna = False

def read_tfluna_data():
    """Reads and parses data from the TF-Luna."""
    while True:
        counter = ser.in_waiting  # Check bytes available in the buffer
        if counter > 8:  # TF-Luna sends 9-byte frames
            bytes_serial = ser.read(9)  # Read 9 bytes
            ser.reset_input_buffer()  # Clear buffer to avoid overflow

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:  # Validate frame header
                distance = bytes_serial[2] + bytes_serial[3] * 256  # Distance (cm)
                strength = bytes_serial[4] + bytes_serial[5] * 256  # Signal strength
                temperature = bytes_serial[6] + bytes_serial[7] * 256  # Temperature (raw)
                temperature = (temperature / 8.0) - 256.0  # Convert to Celsius
                return distance / 100.0, strength, temperature  # Convert distance to meters

def map_value(value, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another."""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def read_and_process_data():
    while True:
        distance, strength, temperature = read_tfluna_data()
        #print(f"Distance: {distance:.2f} m, Strength: {strength:.0f} / 65535, "f"Chip Temperature: {temperature:.1f} °C")
        
        if strength > config.min_certainty and distance < config.Lidar_distance_threshold:  # At least 70% certainty and 0.5 meters distance
            duty_cycle = map_value(distance, 0.1, 0.5, 100, 0)
            duty_cycle = max(0, min(100, duty_cycle))  # Clamp duty cycle between 0 and 100
            pwm.ChangeDutyCycle(duty_cycle)
        else:  # No vibration when conditions aren't met
            pwm.ChangeDutyCycle(0)
        
        time.sleep(0.1)  # Short delay for readability
        # Check for exit
        if kill_Luna:
            break