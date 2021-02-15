import serial, serial.tools.list_ports  # COM port communication
import sys                              # Exiting if no port is availableimport time

run = True

def on_close(event):
    global run
    run = False

# Find ports
available_ports = [comport.device for comport in serial.tools.list_ports.comports()]
print(available_ports)
port = -1
# Choose port
if len(available_ports) == 0:
    print("No connected device detected")
elif len(available_ports) == 1:
    print("One device detected")
    port = 0
else:
    print(f"{len(available_ports)} deviced detected:")
    for i,p in enumerate(available_ports):
        print(f"  {i+1}: {p}")
    while port < 0 or port >= len(available_ports):
        try:
            port = int(input("Select a port:"))-1
        except ValueError:
            print(f"Must be an integer from 1 to {len(available_ports)}")
if port == -1:
    sys.exit()
print(f"Port selected: {available_ports[port]}")


# Open port
stamp_last = 0
stamp_update_last = 0
with serial.Serial(available_ports[port], 9600, timeout=1) as ser:
    # Short delay between opening port and sending message
    time.sleep(2)

    # Write several commands
    bytes_to_write = bytearray([
        0b00000000, # Set servo 0 to...
        0b00001000, # ...8
        0b00000101, # Set servo 5 to...
        0b11111111, # ...255
        0b10010010, # Configuration 18
        0b00001000, # invalid code
        0b01111000  # invalid code
        ])
    ser.write(bytes_to_write)
    """
    ser.write(bytearray([0b00000000]));  # Set servo 0 to...
    ser.write(bytearray([0b00001000]));  # ...8
    ser.write(bytearray([0b00000101]));  # Set servo 5 to...
    ser.write(bytearray([0b11111111]));  # ...255
    ser.write(bytearray([0b10010010]));  # Configuration 18
    ser.write(bytearray([0b00001000]));  # invalid code
    ser.write(bytearray([0b01111000]));  # invalid code
    """
    # Display any received (non-blank) messages
    while True:
        msg = ser.readline()
        if msg!=b'':
            print(str(msg)[2:-5])
