# UI
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext
# pySerial
import serial, serial.tools.list_ports
# Threading
from threading import Thread
from queue import Queue
# Converting struct data
import struct
# Graph plotting
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
# Temporary plot
import numpy as np

"""

This code was written for Python 3.8
The pySerial module is used to communicate through serial
tkinter is used to create the gui
Serial data from the connected device is treated as text

"""

# Custom class to allow a data graph to be displayed
class GraphDisplayFrame(tk.Frame):
    def __init__(self, title, master, **kwargs):
        # "title" will display in label on first row of frame
        # Graph will display on second row of frame
        super().__init__(master, **kwargs)
        ttk.Label(self, text=title).grid(row=0, column=0, sticky='nsew')

        # Maximum length of data storage lists
        self._max_data_elements = 200
        # Data storage lists
        self._data_x = []
        self._data_y = []
        # Flag for checking whether or not display needs to be updated
        self._dirty_data = False

        # Create figure + axis, get canvas and add to frame
        self._fig = Figure(figsize=(4,3), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._ax.plot(self._data_x, self._data_y)
        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().grid(row=1, column=0, sticky='nsew')

    # Add a data point to the data display lists
    def append_data(self, x, y):
        self._dirty_data = True
        self._data_x.append(x)
        self._data_y.append(y)
        # Crop list if too long
        if len(self._data_x) > self._max_data_elements:
            self._data_x = self._data_x[-self._max_data_elements:]
            self._data_y = self._data_y[-self._max_data_elements:]

    # Update display
    # Note - this must be called in the main thread
    def update_display(self):
        # Early return if no changes to display
        if not self._dirty_data:
            return
        # Early return if too few data points
        if len(self._data_x) < 2:
            return
        # Clear graph, plot new graph, update canvas
        self._ax.clear()
        self._ax.plot(self._data_x, self._data_y)
        self._canvas.draw()
        self._dirty_data = False

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
        # Note : Text insertion must be performed inside main loop
        #    process_log will call itself on repeat
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

        # Start graph update process loop
        # Note : canvas.draw() call must be performed inside main loop
        #    update_graph_display will call itself on repeat
        self.update_graph_display()
        
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

        # Queries
        self._fquery = tk.Frame(self, relief='groove', bd=1)
        self._fquery.grid(row=0, column=3, sticky='nsew')
        ttk.Label(self._fquery, text="Queries").grid(row=0, column=0, sticky='nsew')
        self._bquerypositions = ttk.Button(self._fquery, text="Positions", command=self.query_positions)
        self._bquerypositions.grid(row=1, column=0, sticky='nsew')
        self._bquerylimits = ttk.Button(self._fquery, text="Limits", command=self.query_limits)
        self._bquerylimits.grid(row=2, column=0, sticky='nsew')
        self._bqueryforce = ttk.Button(self._fquery, text="Force", command=self.query_force)
        self._bqueryforce.grid(row=3, column=0, sticky='nsew')

        # Log display
        self._foutput = tk.Frame(self, relief='groove', bd=1)
        self._foutput.grid(row=1, column=0, columnspan=4, sticky='nsew')
        ttk.Label(self._foutput, text="Log").grid(row=0, column=0, sticky='nsew')
        self._stoutput = tk.scrolledtext.ScrolledText(self._foutput, wrap=tk.WORD, width=60, height=10)
        self._stoutput.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self._autoscroll = tk.IntVar(self, 1)
        self._cbautoscroll = ttk.Checkbutton(self._foutput, text="Auto-scroll", variable=self._autoscroll)
        self._cbautoscroll.grid(row=0, column=1, sticky='nse')
        self._showcommandbytes = tk.IntVar(self, 0)
        self._cbshowcommandbytes = ttk.Checkbutton(self._foutput, text="Display sent command bytes", variable=self._showcommandbytes)
        self._cbshowcommandbytes.grid(row=2, column=0, sticky='nsew')
        self._displayforcereadings = tk.IntVar(self, 0)
        self._cbdisplayforcereadings = ttk.Checkbutton(self._foutput, text="Display force readings", variable=self._displayforcereadings)
        self._cbdisplayforcereadings.grid(row=3, column=0, sticky='nsew')

        self._stoutput.insert(tk.END, "Connect to a device to start.\n")

        # Force readings
        self._fforcegraph = GraphDisplayFrame("Force Display", self, relief='groove', bd=1)
        self._fforcegraph.grid(row=0, column=4, rowspan=2, sticky='nsew')
        self._btoggleforce = ttk.Button(self._fforcegraph, text="Toggle Force Data Stream", command=self.toggle_force_data_stream)
        self._btoggleforce.grid(row=2, column=0, sticky='nsew')

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
        servo_value = min(max(0, servo_value), 180)     # Limit to 1 byte size
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

    # Sends position query byte command
    def query_positions(self):
        command = 0b00001000
        self.send_command(command)

    # Sends limit query byte command
    def query_limits(self):
        command = 0b00001001
        self.send_command(command)

    # Sends force reading query byte command
    def query_force(self):
        command = 0b00001010
        self.send_command(command)

    # Sends command to enable/disable stream of force readings
    def toggle_force_data_stream(self):
        command = 0b00001011
        self.send_command(command)

    # Sends byte command to connected device
    def send_command(self, command):
        if self.ser.is_open:
            try:
                # Log command in format 0bxxxxxxxx
                if self._showcommandbytes.get():
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
                msg = self.ser.read()
                if msg != b'':
                    self.handle_message(msg[0])
            except (serial.serialutil.SerialException, TypeError, AttributeError) as e:
                self.log("Error raised in listener thread - is the hand connected?")
                raise e
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

    # Updates graph on repeat
    def update_graph_display(self):
        # Update graph display
        self._fforcegraph.update_display()
        # Call again after 100ms
        self.after(100, self.update_graph_display)

    # Message byte received from serial port
    # Handle the byte based on the message specification
    def handle_message(self, message):
        """

        If first bit is 1 then message is string
            Remaining bits specify string length - 1
            Next [length] bytes are characters
        If first 5 bits are 0 then message is for servo position
            Remaining bits specify which servo
            Next byte specifies position
        If message is 0b00001000 then message is for all servo positions
            Next 6 bytes are position for servos 0 to 5
        If message is 0b00001001 then message is for all servo limits
            Next 12 bytes specify limits
            Order is min 0, max 0, min 1, max 1, etc
        If message is 0b00001010 then message is raw force reading
            Next byte specifies reading
        """
        print(f"Got message {message}")
        if message >> 7 == 1:
            # String
            self.receive_char_array(message)
        elif message >> 3 == 0b00000:
            # Servo position
            self.receive_servo_position(message)
        elif message == 0b00001000:
            # All servo positions
            self.receive_all_servo_positions()
        elif message == 0b00001001:
            # All servo limits
            self.receive_all_servo_limits()
        elif message == 0b00001010:
            # Raw force reading
            self.receive_raw_force()
        print(f"Handled message {message}")

    # Read a character array from the serial port
    def receive_char_array(self, message):
        # Array length = last 7 bits of message + 1
        length = (message - 0b10000000) + 1
        # Read directly from serial port, cast to string, remove surrounding characters
        text = str(self.ser.read(length))[2:-1]
        self.log(f"> \"{text}\"")

    # Read a single servo position
    def receive_servo_position(self, message):
        # Servo number = message as prefix is all 0
        servo_num = message - 0b00000000
        # Position is following byte
        pos = self.read_one_byte()
        self.log(f"> Servo {servo_num} position : {pos}")

    # Read all servo positions
    def receive_all_servo_positions(self):
        # Following 6 bytes correspond to positions for servos 0 to 5
        out = "Servo positions : "
        for i in range(6):
            pos = self.read_one_byte()
            out += f"{pos} "
        self.log(f"> {out}")

    # Read all servo limits
    def receive_all_servo_limits(self):
        # Following 12 bytes correspond to servo limits
        # Order is min 0, max 0, min 1, max 1, etc.
        out = "Servo limits : "
        for i in range(6):
            l_min = self.read_one_byte()
            l_max = self.read_one_byte()
            out += f"({l_min},{l_max}) "
        self.log(f"> {out}")

    # Read a raw force reading
    def receive_raw_force(self):
        # Force reading is 6 bytes
        # 4 bytes - unsigned long timestamp
        # 2 bytes - unsigned short reading
        # Data is in little endian order
        data = self.ser.read(6)
        timestamp, raw_force = struct.unpack(f'<LH', data)
        if self._displayforcereadings.get():
            self.log(f"> Raw force : {raw_force} at {timestamp}")
        # Add reading to force graph
        self._fforcegraph.append_data(timestamp/1000.0, raw_force)

    # Helper function to read 1 byte from the serial port
    # Will not return until a byte has been received
    def read_one_byte(self):
        byte = b''
        while byte == b'':
            byte = self.ser.read()
        # ser.read() returns a byte array - take only first value
        return byte[0]


# Instantiate application and run
app = HandControlApplication()
app.mainloop()
