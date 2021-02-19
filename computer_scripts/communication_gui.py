# UI
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext
# pySerial
import serial, serial.tools.list_ports
# Threading
from threading import Thread
from queue import Queue

"""

This code was written for Python 3.8
The pySerial module is used to communicate through serial
tkinter is used to create the gui
Serial data from the connected device is treated as text

"""

class HandControlApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_close)    # Set closing operation to custom method

        # Use a single serial instance instead of using context manager
        self.ser = serial.Serial()
        self.ser.baudrate = 9600
        self.ser.timeout = 1
        self.com_port_is_available = False  # Used for connect button
        # Listener thread management
        self.port_listener_thread = None    # Thread object
        self.port_listener_flag = False     # 
        self.log_queue = Queue()            # 

        # Start the log process loop
        self.process_log()

        # Drop-down menu options
        self.servo_names = ["Finger 0", "Finger 1", "Finger 2", "Finger 3", "Thumb 0", "Thumb 1"]
        self.servo_configs = [
            "Zeros",
            "Ascending",
            "Descending",
            "Alternating",
            "Invalid"
            ]

        # Create UI
        self.create_widgets()
        self.title("Hand Controller")

    # Exit button pressed
    def on_close(self):
        self.log("Stopping...")
        self.close_serial()
        self.destroy()

    # Create UI widgets
    def create_widgets(self):
        # COM port selection
        self._fconnect = tk.Frame(self, relief='groove', bd=1)
        self._fconnect.grid(row=0, column=0, sticky='nsew')
        ttk.Label(self._fconnect, text="Port Selection").grid(row=0, column=0, sticky='nsew')
        ports = self.get_available_ports()
        self._selected_port = tk.StringVar(self, ports[0])
        self._cbports = ttk.Combobox(self._fconnect, textvariable=self._selected_port, values=ports)
        self._cbports.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self._brefreshports = ttk.Button(self._fconnect, text="Refresh", command=self.refresh_ports)
        self._brefreshports.grid(row=2, column=0, sticky='nsew')
        self._bconnect = ttk.Button(self._fconnect, text="Connect", command=self.connect)
        self._bconnect.grid(row=2, column=1, sticky='nsew')

        # Single Servo Control
        self._fsinglecontrol = tk.Frame(self, relief='groove', bd=1)
        self._fsinglecontrol.grid(row=0, column=1, sticky='nsew')
        ttk.Label(self._fsinglecontrol, text="Individual Servo Control").grid(row=0, column=0, columnspan=2, sticky='nsew')
        self._selected_servo = tk.StringVar(self, self.servo_names[0])
        self._cbservoselection = ttk.Combobox(self._fsinglecontrol, textvariable=self._selected_servo, values=self.servo_names)
        self._cbservoselection.grid(row=1, column=1, sticky='nsew')
        self._sbservovalue = ttk.Spinbox(self._fsinglecontrol, from_=0, to=255)
        self._sbservovalue.set(0)
        self._sbservovalue.grid(row=2, column=1, sticky='nsew')
        self._bsetservovalue = ttk.Button(self._fsinglecontrol, text="Set", command=self.set_servo_value)
        self._bsetservovalue.grid(row=3, column=1, sticky='nsew')
        ttk.Label(self._fsinglecontrol, text="Servo").grid(row=1, column=0, sticky='nse')
        ttk.Label(self._fsinglecontrol, text="Value (0-255)").grid(row=2, column=0, sticky='nse')

        # Multiple Servo Control
        self._fmultiplecontrol = tk.Frame(self, relief='groove', bd=1)
        self._fmultiplecontrol.grid(row=0, column=2, sticky='nsew')
        ttk.Label(self._fmultiplecontrol, text="Configuration Control").grid(row=0, column=0, sticky='nsew')
        self._selected_config = tk.StringVar(self, self.servo_configs[0])
        self._cbconfigs = ttk.Combobox(self._fmultiplecontrol, textvariable=self._selected_config, values=self.servo_configs)
        self._cbconfigs.grid(row=1, column=0, sticky='nsew')
        self._bsetconfig = ttk.Button(self._fmultiplecontrol, text="Set", command=self.set_config)
        self._bsetconfig.grid(row=2, column=0, sticky='nsew')

        # Log display
        self._foutput = tk.Frame(self, relief='groove', bd=1)
        self._foutput.grid(row=1, column=0, columnspan=3, sticky='nsew')
        ttk.Label(self._foutput, text="Log").grid(row=0, column=0, sticky='nsew')
        self._stoutput = tk.scrolledtext.ScrolledText(self._foutput, wrap=tk.WORD, width=60, height=10)
        self._stoutput.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self._autoscroll = tk.IntVar(self, 1)
        self._cbautoscroll = ttk.Checkbutton(self._foutput, text="Auto-scroll", variable=self._autoscroll)
        self._cbautoscroll.grid(row=0, column=1, sticky='nse')

        self._stoutput.insert(tk.END, "Connect to a device to start.\n")

    # Get list of available ports
    def get_available_ports(self):
        available_ports = [comport.device for comport in serial.tools.list_ports.comports()]
        if len(available_ports) == 0:
            self.com_port_is_available = False
            return ["No device detected"]
        self.com_port_is_available = True
        return available_ports

    # Refresh the list of available ports
    def refresh_ports(self):
        ports = self.get_available_ports()
        self._cbports['values'] = ports
        self._cbports.current(0)

    # Connect to the device on the selected port
    def connect(self):
        # Disconnect serial port if already connected
        self.close_serial()
        if not self.com_port_is_available:
            self.log("No port to connect to")
            return
        # Obtain selected port
        port = self._selected_port.get()
        self.ser.port = port
        self.log(f"Connecting to {port}")
        # Connect to port and start listener thread
        try:
            self.ser.open()
            self.port_listener_flag = True
            self.port_listener_thread = Thread(target=self.listen_to_port)
            self.port_listener_thread.start()
        except serial.serialutil.SerialException:
            self.log(f"Failed to connect to port {port}")

    # Sends individual servo command (servo 0-5, value 0-255)
    def set_servo_value(self):
        # Obtain selected servo and value
        servo_name = self._selected_servo.get()
        selected_servo = self.servo_names.index(servo_name)
        servo_value = int(self._sbservovalue.get())
        servo_value = min(max(0, servo_value), 255)     # Limit to 1 byte size
        # Send single servo command
        servo_command = 0b00000000 | selected_servo     # Line unnecessary, but kept in case command format changes
        self.send_command(servo_command)                # Send servo to move
        self.send_command(servo_value)                  # Send value

    # Sends configuration byte command (0-127)
    def set_config(self):
        # Obtain selected configuration
        config_name = self._selected_config.get()
        selected_config = self.servo_configs.index(config_name)
        selected_config = min(max(0, selected_config), 127)     # Ensure config is value (0-127)
        # Create and send command
        config_command = 0b10000000 | selected_config           # First bit is 1, remaining are config
        self.send_command(config_command)

    # Sends byte command to connected device
    def send_command(self, command):
        if self.ser.is_open:
            try:
                # Log command in format 0bxxxxxxxx
                self.log(f"Sending byte {command:08b}")
                self.ser.write(bytearray([command]))
            except serial.serialutil.SerialException:
                self.log("Failed to send byte")
        else:
            self.log("Cannot send byte - port closed")

    # Serial port listener thread function
    def listen_to_port(self):
        self.log("Serial port listener started")
        # End when flag is set to false or exception raised
        while self.port_listener_flag:
            try:
                msg = self.ser.readline()
                if msg != b'':
                    self.log(f"> {str(msg)[2:-5]}")
            except (serial.serialutil.SerialException, TypeError, AttributeError):
                self.log("Error raised in listener thread - is the hand connected?")
                # TODO: Look more closely into why TypeError appears here
                # Seems to happen after message has been received and root is closed
                # May be due to port closing while self.ser.readline is executing?
                break
        self.log("Serial port listener stopped")

    # Closes serial port and stops listener thread
    def close_serial(self):
        self.port_listener_flag = False
        if self.port_listener_thread is not None:
            self.port_listener_thread.join()
            self.port_listener_thread = None
        if self.ser.is_open:
            self.ser.close()

    # Call log(text) to log any important information to gui
    # Text is printed to console and displayed in gui
    def log(self, text):
        self.log_queue.put(text)
        print(text)

    # Handles gui console
    def process_log(self):
        # Display all messages in queue
        while not self.log_queue.empty():
            text = self.log_queue.get()
            self._stoutput.insert(tk.END, '\n')
            self._stoutput.insert(tk.END, text)
            # Move scrollbar to bottom
            if self._autoscroll.get():
                self._stoutput.see(tk.END)
        # Call again after 50ms
        self.after(50, self.process_log)


# Instantiate application and run
app = HandControlApplication()
app.mainloop()
