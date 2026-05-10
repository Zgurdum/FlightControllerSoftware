"""
Main GUI application for flight controller configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging

try:
    # Package import (works if launched as module)
    from .flight_controller import FlightControllerInterface
except ImportError:
    # Script import (works with: python src/gui_main.py)
    from flight_controller import FlightControllerInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlightControllerGUI:
    """Main GUI for flight controller software"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("F722 Flight Controller Configuration")
        self.root.geometry("1000x700")
        
        self.fc = FlightControllerInterface()
        self.update_thread = None
        self.stop_update = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create GUI widgets"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(conn_frame, text="Serial Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_var = tk.StringVar(value="COM3")
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, width=15)
        self.port_combo.grid(row=0, column=1, padx=5)
        
        self.refresh_btn = ttk.Button(conn_frame, text="Refresh Ports", command=self._refresh_ports)
        self.refresh_btn.grid(row=0, column=2, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self._connect)
        self.connect_btn.grid(row=0, column=3, padx=5)
        
        self.status_label = ttk.Label(conn_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        # Device info frame
        info_frame = ttk.LabelFrame(self.root, text="Device Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.info_text = tk.Text(info_frame, height=4, width=80, state=tk.DISABLED)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Telemetry tab
        self._create_telemetry_tab()
        
        # Sensors tab
        self._create_sensors_tab()
        
        # Calibration tab
        self._create_calibration_tab()
        
        # Configure tab
        self._create_configure_tab()

        # Motor test tab
        self._create_motor_test_tab()

        # Betaflight-style options tabs
        self._create_pid_tab()
        self._create_rates_tab()
        self._create_modes_tab()
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.fps_label = ttk.Label(status_frame, text="FPS: 0")
        self.fps_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def _create_telemetry_tab(self):
        """Create telemetry display tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Telemetry")
        
        # Motor speeds
        motor_frame = ttk.LabelFrame(tab, text="Motor Speeds", padding=10)
        motor_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.motor_labels = []
        for i in range(4):
            label = ttk.Label(motor_frame, text=f"Motor {i+1}: 0 rpm")
            label.pack(side=tk.LEFT, padx=20)
            self.motor_labels.append(label)
        
        # RC Channels
        rc_frame = ttk.LabelFrame(tab, text="RC Channels", padding=10)
        rc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.rc_labels = []
        for i in range(6):
            label = ttk.Label(rc_frame, text=f"CH{i+1}: 1500")
            label.pack(side=tk.LEFT, padx=20)
            self.rc_labels.append(label)
        
        # Battery info
        batt_frame = ttk.LabelFrame(tab, text="Battery", padding=10)
        batt_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.voltage_label = ttk.Label(batt_frame, text="Voltage: 0.0V")
        self.voltage_label.pack(side=tk.LEFT, padx=20)
        
        self.current_label = ttk.Label(batt_frame, text="Current: 0.0A")
        self.current_label.pack(side=tk.LEFT, padx=20)
        
        self.mah_label = ttk.Label(batt_frame, text="mAh: 0")
        self.mah_label.pack(side=tk.LEFT, padx=20)
    
    def _create_sensors_tab(self):
        """Create sensor data display tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sensors")
        
        # Gyro
        gyro_frame = ttk.LabelFrame(tab, text="Gyroscope (°/s)", padding=10)
        gyro_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.gyro_labels = []
        for axis in ['X', 'Y', 'Z']:
            label = ttk.Label(gyro_frame, text=f"{axis}: 0.0")
            label.pack(side=tk.LEFT, padx=20)
            self.gyro_labels.append(label)
        
        # Accelerometer
        accel_frame = ttk.LabelFrame(tab, text="Accelerometer (g)", padding=10)
        accel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.accel_labels = []
        for axis in ['X', 'Y', 'Z']:
            label = ttk.Label(accel_frame, text=f"{axis}: 0.0")
            label.pack(side=tk.LEFT, padx=20)
            self.accel_labels.append(label)
        
        # Magnetometer
        mag_frame = ttk.LabelFrame(tab, text="Magnetometer", padding=10)
        mag_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.mag_labels = []
        for axis in ['X', 'Y', 'Z']:
            label = ttk.Label(mag_frame, text=f"{axis}: 0")
            label.pack(side=tk.LEFT, padx=20)
            self.mag_labels.append(label)
    
    def _create_calibration_tab(self):
        """Create calibration tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Calibration")
        
        info_label = ttk.Label(tab, text="Sensor Calibration", font=("Arial", 12, "bold"))
        info_label.pack(pady=20)
        
        info_text = tk.Text(tab, height=5, width=70, state=tk.DISABLED)
        info_text.pack(padx=20, pady=10)
        
        button_frame = ttk.Frame(tab)
        button_frame.pack(pady=20)
        
        self.accel_cal_btn = ttk.Button(button_frame, text="Calibrate Accelerometer", 
                                        command=self._calibrate_accel)
        self.accel_cal_btn.pack(side=tk.LEFT, padx=10)
        
        self.mag_cal_btn = ttk.Button(button_frame, text="Calibrate Magnetometer", 
                                      command=self._calibrate_mag)
        self.mag_cal_btn.pack(side=tk.LEFT, padx=10)
    
    def _create_configure_tab(self):
        """Create configuration tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Configure")
        
        config_frame = ttk.LabelFrame(tab, text="Flight Controller Settings", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic system configuration options (UI first, wiring can be expanded per command support).
        self.arming_disabled_var = tk.BooleanVar(value=False)
        self.airmode_var = tk.BooleanVar(value=True)
        self.anti_gravity_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(config_frame, text="Arming Disabled", variable=self.arming_disabled_var).pack(anchor=tk.W, pady=4)
        ttk.Checkbutton(config_frame, text="Air Mode", variable=self.airmode_var).pack(anchor=tk.W, pady=4)
        ttk.Checkbutton(config_frame, text="Anti-Gravity", variable=self.anti_gravity_var).pack(anchor=tk.W, pady=4)
        
        self.save_btn = ttk.Button(config_frame, text="Save Configuration", 
                                   command=self._save_config)
        self.save_btn.pack(pady=20)

    def _create_motor_test_tab(self):
        """Create motor test tab with per-motor sliders."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Motor Test")

        warning = (
            "Warning: Remove props before motor testing. Keep battery disconnected unless needed."
        )
        ttk.Label(tab, text=warning, foreground="red").pack(anchor=tk.W, padx=10, pady=8)

        self.motor_test_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            tab,
            text="I confirm props are removed and I want to enable motor test",
            variable=self.motor_test_enabled,
            command=self._toggle_motor_test,
        ).pack(anchor=tk.W, padx=10, pady=6)

        sliders_frame = ttk.LabelFrame(tab, text="Motor PWM (1000-2000)", padding=10)
        sliders_frame.pack(fill=tk.X, padx=10, pady=10)

        self.motor_test_vars = [tk.IntVar(value=1000) for _ in range(4)]
        self.motor_test_sliders = []
        self.motor_test_value_labels = []

        for idx in range(4):
            ttk.Label(sliders_frame, text=f"Motor {idx + 1}").grid(row=idx, column=0, padx=8, pady=8, sticky=tk.W)

            slider = ttk.Scale(
                sliders_frame,
                from_=1000,
                to=2000,
                orient=tk.HORIZONTAL,
                length=450,
                command=lambda value, i=idx: self._on_motor_slider_change(i, value),
            )
            slider.set(1000)
            slider.grid(row=idx, column=1, padx=8, pady=8)
            self.motor_test_sliders.append(slider)

            value_label = ttk.Label(sliders_frame, text="1000", width=6)
            value_label.grid(row=idx, column=2, padx=8, pady=8)
            self.motor_test_value_labels.append(value_label)

        actions = ttk.Frame(tab)
        actions.pack(fill=tk.X, padx=10, pady=10)

        self.apply_motor_btn = ttk.Button(actions, text="Apply Motor Values", command=self._apply_motor_test_values)
        self.apply_motor_btn.pack(side=tk.LEFT, padx=6)

        self.stop_all_motors_btn = ttk.Button(actions, text="Stop All Motors", command=self._stop_all_motors)
        self.stop_all_motors_btn.pack(side=tk.LEFT, padx=6)

        self.motor_test_status = ttk.Label(actions, text="Motor test disabled")
        self.motor_test_status.pack(side=tk.LEFT, padx=12)

        self._set_motor_test_widgets_state(enabled=False)

    def _set_motor_test_widgets_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        for slider in self.motor_test_sliders:
            slider.configure(state=state)
        self.apply_motor_btn.configure(state=state)
        self.stop_all_motors_btn.configure(state=state)

    def _toggle_motor_test(self):
        enabled = self.motor_test_enabled.get()
        self._set_motor_test_widgets_state(enabled)
        if enabled:
            self.motor_test_status.config(text="Motor test enabled")
        else:
            self._stop_all_motors()
            self.motor_test_status.config(text="Motor test disabled")

    def _on_motor_slider_change(self, index: int, value: str):
        pwm = int(float(value))
        self.motor_test_vars[index].set(pwm)
        self.motor_test_value_labels[index].config(text=str(pwm))

    def _apply_motor_test_values(self):
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected to flight controller")
            return

        if not self.motor_test_enabled.get():
            messagebox.showwarning("Motor Test", "Enable motor test first")
            return

        motor_values = [var.get() for var in self.motor_test_vars]
        if self.fc.set_motor_test_values(motor_values):
            self.motor_test_status.config(text=f"Applied: {motor_values}")
        else:
            messagebox.showerror("Motor Test", "Failed to send motor values")

    def _stop_all_motors(self):
        for idx, slider in enumerate(self.motor_test_sliders):
            slider.set(1000)
            self.motor_test_vars[idx].set(1000)
            self.motor_test_value_labels[idx].config(text="1000")

        if self.fc.connected:
            self.fc.set_motor_test_values([1000, 1000, 1000, 1000])

    def _create_pid_tab(self):
        """Create PID tuning tab (Betaflight style)."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="PID Tuning")

        axes = ["Roll", "Pitch", "Yaw"]
        defaults = {
            "Roll": (42, 85, 35),
            "Pitch": (46, 90, 38),
            "Yaw": (40, 85, 0),
        }

        self.pid_vars = {}
        for axis in axes:
            frame = ttk.LabelFrame(tab, text=f"{axis} PID", padding=10)
            frame.pack(fill=tk.X, padx=10, pady=5)

            p_var = tk.IntVar(value=defaults[axis][0])
            i_var = tk.IntVar(value=defaults[axis][1])
            d_var = tk.IntVar(value=defaults[axis][2])
            self.pid_vars[axis.lower()] = {"p": p_var, "i": i_var, "d": d_var}

            ttk.Label(frame, text="P").grid(row=0, column=0, padx=8)
            ttk.Scale(frame, from_=0, to=200, variable=p_var, orient=tk.HORIZONTAL, length=200).grid(row=0, column=1, padx=8)
            ttk.Label(frame, textvariable=p_var, width=4).grid(row=0, column=2, padx=8)

            ttk.Label(frame, text="I").grid(row=0, column=3, padx=8)
            ttk.Scale(frame, from_=0, to=200, variable=i_var, orient=tk.HORIZONTAL, length=200).grid(row=0, column=4, padx=8)
            ttk.Label(frame, textvariable=i_var, width=4).grid(row=0, column=5, padx=8)

            ttk.Label(frame, text="D").grid(row=0, column=6, padx=8)
            ttk.Scale(frame, from_=0, to=200, variable=d_var, orient=tk.HORIZONTAL, length=200).grid(row=0, column=7, padx=8)
            ttk.Label(frame, textvariable=d_var, width=4).grid(row=0, column=8, padx=8)

        ttk.Button(tab, text="Apply PID (Preview)", command=self._apply_pid_preview).pack(pady=12)

    def _create_rates_tab(self):
        """Create rates/expo tab (Betaflight style)."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Rates")

        self.rate_vars = {
            "rc_rate": tk.DoubleVar(value=1.00),
            "super_rate": tk.DoubleVar(value=0.70),
            "expo": tk.DoubleVar(value=0.15),
        }

        frame = ttk.LabelFrame(tab, text="Rate Profile", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame, text="RC Rate").grid(row=0, column=0, sticky=tk.W, padx=8, pady=6)
        ttk.Scale(frame, from_=0.1, to=2.5, variable=self.rate_vars["rc_rate"], orient=tk.HORIZONTAL, length=350).grid(row=0, column=1, padx=8)
        ttk.Label(frame, textvariable=self.rate_vars["rc_rate"], width=6).grid(row=0, column=2, padx=8)

        ttk.Label(frame, text="Super Rate").grid(row=1, column=0, sticky=tk.W, padx=8, pady=6)
        ttk.Scale(frame, from_=0.0, to=1.0, variable=self.rate_vars["super_rate"], orient=tk.HORIZONTAL, length=350).grid(row=1, column=1, padx=8)
        ttk.Label(frame, textvariable=self.rate_vars["super_rate"], width=6).grid(row=1, column=2, padx=8)

        ttk.Label(frame, text="Expo").grid(row=2, column=0, sticky=tk.W, padx=8, pady=6)
        ttk.Scale(frame, from_=0.0, to=1.0, variable=self.rate_vars["expo"], orient=tk.HORIZONTAL, length=350).grid(row=2, column=1, padx=8)
        ttk.Label(frame, textvariable=self.rate_vars["expo"], width=6).grid(row=2, column=2, padx=8)

        ttk.Button(tab, text="Apply Rates (Preview)", command=self._apply_rates_preview).pack(pady=12)

    def _create_modes_tab(self):
        """Create modes tab (Betaflight style)."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Modes")

        mode_frame = ttk.LabelFrame(tab, text="Mode Mapping", padding=10)
        mode_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.mode_vars = {
            "arm": tk.BooleanVar(value=True),
            "angle": tk.BooleanVar(value=False),
            "horizon": tk.BooleanVar(value=False),
            "beeper": tk.BooleanVar(value=False),
            "flip_over_after_crash": tk.BooleanVar(value=False),
        }

        ttk.Checkbutton(mode_frame, text="ARM", variable=self.mode_vars["arm"]).pack(anchor=tk.W, pady=4)
        ttk.Checkbutton(mode_frame, text="ANGLE", variable=self.mode_vars["angle"]).pack(anchor=tk.W, pady=4)
        ttk.Checkbutton(mode_frame, text="HORIZON", variable=self.mode_vars["horizon"]).pack(anchor=tk.W, pady=4)
        ttk.Checkbutton(mode_frame, text="BEEPER", variable=self.mode_vars["beeper"]).pack(anchor=tk.W, pady=4)
        ttk.Checkbutton(mode_frame, text="FLIP OVER AFTER CRASH", variable=self.mode_vars["flip_over_after_crash"]).pack(anchor=tk.W, pady=4)

        ttk.Button(tab, text="Apply Modes (Preview)", command=self._apply_modes_preview).pack(pady=12)
    
    def _refresh_ports(self):
        """Refresh list of available serial ports"""
        ports = self.fc.serial.list_ports()
        port_names = [p['port'] for p in ports]
        self.port_combo['values'] = port_names
        if port_names:
            self.port_combo.current(0)
    
    def _connect(self):
        """Connect to flight controller"""
        if self.fc.connected:
            self.fc.disconnect()
            self.connect_btn.config(text="Connect")
            self.status_label.config(text="Status: Disconnected", foreground="red")
            self.stop_update = True
            return
        
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "Please select a serial port")
            return
        
        if self.fc.connect(port):
            self.connect_btn.config(text="Disconnect")
            self.status_label.config(text="Status: Connected", foreground="green")
            self._update_device_info()
            self.stop_update = False
            self._start_telemetry_update()
        else:
            messagebox.showerror("Connection Error", f"Failed to connect to {port}")
    
    def _update_device_info(self):
        """Update device information display"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        
        info = self.fc.device_info
        device_type = info.get('fc_variant') or info.get('type') or info.get('board_id') or 'Unknown'
        firmware_version = info.get('fc_version') or info.get('version') or 'Unknown'
        msp_version = info.get('api_version') or info.get('msp_version') or 'Unknown'
        board_id = info.get('board_id', 'Unknown')
        build_info = info.get('build_info', 'Unknown')

        text = (
            f"Device Type: {device_type}\n"
            f"Firmware Version: {firmware_version}\n"
            f"MSP Version: {msp_version}\n"
            f"Board ID: {board_id}\n"
            f"Build Info: {build_info}"
        )
        
        self.info_text.insert("1.0", text)
        self.info_text.config(state=tk.DISABLED)
    
    def _start_telemetry_update(self):
        """Start telemetry update thread"""
        if self.update_thread is None or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self._telemetry_loop, daemon=True)
            self.update_thread.start()
    
    def _telemetry_loop(self):
        """Continuously update telemetry"""
        frame_count = 0
        import time
        
        while not self.stop_update and self.fc.connected:
            try:
                self.fc.get_telemetry()
                self._update_display()
                frame_count += 1
                time.sleep(0.05)  # 20 Hz update rate
            except Exception as e:
                logger.error(f"Telemetry update error: {e}")
                break
    
    def _update_display(self):
        """Update GUI display with telemetry data"""
        try:
            # Update motors
            for i, speed in enumerate(self.fc.motor_speeds[:4]):
                self.motor_labels[i].config(text=f"Motor {i+1}: {speed} pwm")
            
            # Update RC channels
            for i, channel in enumerate(self.fc.rc_channels[:6]):
                self.rc_labels[i].config(text=f"CH{i+1}: {channel}")
            
            # Update sensors
            if self.fc.sensor_data:
                gyro = self.fc.sensor_data.get('gyro', {})
                for i, axis in enumerate(['x', 'y', 'z']):
                    self.gyro_labels[i].config(text=f"{axis.upper()}: {gyro.get(axis, 0):.2f}")
                
                acc = self.fc.sensor_data.get('accelerometer', {})
                for i, axis in enumerate(['x', 'y', 'z']):
                    self.accel_labels[i].config(text=f"{axis.upper()}: {acc.get(axis, 0):.2f}")
                
                mag = self.fc.sensor_data.get('magnetometer', {})
                for i, axis in enumerate(['x', 'y', 'z']):
                    self.mag_labels[i].config(text=f"{axis.upper()}: {mag.get(axis, 0)}")
            
            # Update battery
            if 'vbat' in self.fc.status_data:
                self.voltage_label.config(text=f"Voltage: {self.fc.status_data['vbat']:.1f}V")
            if 'amperage' in self.fc.status_data:
                self.current_label.config(text=f"Current: {self.fc.status_data['amperage']:.1f}A")
            if 'mah' in self.fc.status_data:
                self.mah_label.config(text=f"mAh: {self.fc.status_data['mah']}")
        
        except Exception as e:
            logger.error(f"Display update error: {e}")
    
    def _calibrate_accel(self):
        """Calibrate accelerometer"""
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected to flight controller")
            return
        
        if messagebox.askokcancel("Calibration", "Place drone on level surface and click OK"):
            self.fc.calibrate_accelerometer()
            messagebox.showinfo("Success", "Accelerometer calibrated")
    
    def _calibrate_mag(self):
        """Calibrate magnetometer"""
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected to flight controller")
            return
        
        if messagebox.askokcancel("Calibration", "Rotate drone slowly in all directions and click OK"):
            self.fc.calibrate_magnetometer()
            messagebox.showinfo("Success", "Magnetometer calibrated")
    
    def _save_config(self):
        """Save configuration"""
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected to flight controller")
            return
        
        self.fc.save_configuration()
        messagebox.showinfo("Success", "Configuration saved")

    def _apply_pid_preview(self):
        """Preview action for PID tuning UI."""
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected to flight controller")
            return

        messagebox.showinfo("PID Tuning", "PID UI is active. MSP write support can be enabled next.")

    def _apply_rates_preview(self):
        """Preview action for rates UI."""
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected to flight controller")
            return

        messagebox.showinfo("Rates", "Rates UI is active. MSP write support can be enabled next.")

    def _apply_modes_preview(self):
        """Preview action for modes UI."""
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected to flight controller")
            return

        messagebox.showinfo("Modes", "Modes UI is active. MSP write support can be enabled next.")
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "F722 Flight Controller Configuration\nVersion 1.0\n\nCustom drone programming software")
    
    def on_closing(self):
        """Handle window close"""
        self.stop_update = True
        if self.fc.connected:
            self.fc.disconnect()
        self.root.destroy()


def main():
    root = tk.Tk()
    gui = FlightControllerGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
