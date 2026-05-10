"""
Main GUI application for F722 Flight Controller Configuration
Features: Telemetry, Sensors, PID, Rates, Modes, Motor Test, Profiles, Community Board, Tunes Library
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import threading
import time
import logging

try:
    from .flight_controller import FlightControllerInterface
    from .drone_visualizer import create_visualizer
    from .profiles_manager import ProfilesManager, Profile
    from .tunes_manager import TunesManager, Tune
    from .community_board import CommunityBoard
except ImportError:
    from flight_controller import FlightControllerInterface
    from drone_visualizer import create_visualizer
    from profiles_manager import ProfilesManager, Profile
    from tunes_manager import TunesManager, Tune
    from community_board import CommunityBoard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Theme colors
BG      = "#1c1c2e"
BG2     = "#252540"
BG3     = "#2e2e4a"
BORDER  = "#3a3a5c"
ACCENT  = "#7c3aed"
ACCENT2 = "#06b6d4"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
DANGER  = "#ef4444"
TEXT    = "#e2e8f0"
TEXT2   = "#94a3b8"
WHITE   = "#ffffff"


def apply_dark_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=BG, foreground=TEXT, fieldbackground=BG3,
                    bordercolor=BORDER, darkcolor=BG, lightcolor=BG2,
                    troughcolor=BG2, font=("Segoe UI", 10))
    style.map(".", background=[("active", BG3), ("disabled", BG)])
    style.configure("TFrame", background=BG)
    style.configure("TLabelframe", background=BG, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=BG, foreground=ACCENT, font=("Segoe UI", 10, "bold"))
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("TButton", background=BG3, foreground=TEXT, bordercolor=BORDER,
                    focusthickness=0, relief="flat", padding=(10, 6))
    style.map("TButton", background=[("active", ACCENT), ("pressed", "#5b21b6")],
              foreground=[("active", WHITE)])
    style.configure("Accent.TButton", background=ACCENT, foreground=WHITE,
                    font=("Segoe UI", 10, "bold"), padding=(12, 7))
    style.map("Accent.TButton", background=[("active", "#6d28d9"), ("pressed", "#5b21b6")])
    style.configure("Danger.TButton", background=DANGER, foreground=WHITE, padding=(10, 6))
    style.map("Danger.TButton", background=[("active", "#dc2626")])
    style.configure("Success.TButton", background=SUCCESS, foreground=WHITE, padding=(10, 6))
    style.map("Success.TButton", background=[("active", "#16a34a")])
    style.configure("TNotebook", background=BG, bordercolor=BG, tabmargins=(0, 0, 0, 0))
    style.configure("TNotebook.Tab", background=BG2, foreground=TEXT2, padding=(14, 8),
                    font=("Segoe UI", 9, "bold"))
    style.map("TNotebook.Tab", background=[("selected", BG3), ("active", BG3)],
              foreground=[("selected", WHITE), ("active", TEXT)])
    style.configure("TEntry", fieldbackground=BG3, foreground=TEXT, bordercolor=BORDER,
                    insertcolor=TEXT, padding=(6, 4))
    style.configure("TCombobox", fieldbackground=BG3, foreground=TEXT, background=BG2,
                    arrowcolor=TEXT2, bordercolor=BORDER)
    style.map("TCombobox", fieldbackground=[("readonly", BG3)])
    style.configure("TScale", background=BG, troughcolor=BG3, sliderlength=16, borderwidth=0)
    style.configure("TCheckbutton", background=BG, foreground=TEXT)
    style.map("TCheckbutton", background=[("active", BG)])
    style.configure("TScrollbar", background=BG2, troughcolor=BG, arrowcolor=TEXT2, bordercolor=BG)
    style.map("TScrollbar", background=[("active", BG3)])
    root.configure(bg=BG)


def dark_text(parent, **kwargs):
    defaults = dict(bg=BG3, fg=TEXT, insertbackground=TEXT, selectbackground=ACCENT,
                    selectforeground=WHITE, relief="flat", bd=0, font=("Segoe UI", 10), padx=8, pady=6)
    defaults.update(kwargs)
    return tk.Text(parent, **defaults)


def card(parent, title="", **kwargs):
    return ttk.LabelFrame(parent, text=title, **kwargs)


class FlightControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("F722 Flight Controller  —  Pro Edition")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 650)
        apply_dark_theme(self.root)
        self.fc = FlightControllerInterface()
        self.visualizer = create_visualizer()
        self.profiles_mgr = ProfilesManager()
        self.tunes_mgr = TunesManager()
        self.community = CommunityBoard()
        self.update_thread = None
        self.stop_update = False
        self._selected_tune = None
        self._profile_cache = []
        self._tune_cache = []
        self._build_ui()

    def _build_ui(self):
        self._build_header()
        self._build_notebook()
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG2, pady=8)
        hdr.pack(fill=tk.X, side=tk.TOP)
        tk.Label(hdr, text="  F722  CONFIGURATOR", bg=BG2, fg=ACCENT,
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT, padx=(16, 30))
        tk.Label(hdr, text="Port:", bg=BG2, fg=TEXT2, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.port_var = tk.StringVar(value="COM3")
        self.port_combo = ttk.Combobox(hdr, textvariable=self.port_var, width=10)
        self.port_combo.pack(side=tk.LEFT, padx=(0, 6))
        self._refresh_ports()
        ttk.Button(hdr, text="Refresh", command=self._refresh_ports).pack(side=tk.LEFT, padx=(0, 12))
        self.connect_btn = ttk.Button(hdr, text="Connect", style="Accent.TButton", command=self._connect)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 20))
        self.status_var = tk.StringVar(value="  Disconnected")
        self.status_label = tk.Label(hdr, textvariable=self.status_var, bg=BG2, fg=DANGER,
                                     font=("Segoe UI", 10, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=(0, 20))
        self.device_var = tk.StringVar(value="No device")
        tk.Label(hdr, textvariable=self.device_var, bg=BG2, fg=TEXT2, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.profile_pill_var = tk.StringVar(value="No Profile")
        tk.Label(hdr, textvariable=self.profile_pill_var, bg=BG2, fg=ACCENT2,
                 font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT, padx=16)
        tk.Label(hdr, text="Pilot:", bg=BG2, fg=TEXT2, font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=(0, 4))

    def _build_notebook(self):
        nb_frame = tk.Frame(self.root, bg=BG)
        nb_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 0))
        self.notebook = ttk.Notebook(nb_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self._create_telemetry_tab()
        self._create_sensors_tab()
        self._create_motor_test_tab()
        self._create_pid_tab()
        self._create_rates_tab()
        self._create_modes_tab()
        self._create_calibration_tab()
        self._create_configure_tab()
        self._create_profiles_tab()
        self._create_community_tab()
        self._create_tunes_tab()

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=BG2, height=26)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.fps_var = tk.StringVar(value="50 Hz telemetry")
        tk.Label(bar, textvariable=self.fps_var, bg=BG2, fg=TEXT2, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=12)
        tk.Label(bar, text="F722 Pro Edition  v2.0", bg=BG2, fg=TEXT2, font=("Segoe UI", 8)).pack(side=tk.RIGHT, padx=12)

    # ── Telemetry Tab ──────────────────────────────────────────────────────────
    def _create_telemetry_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Telemetry  ")
        top = tk.Frame(tab, bg=BG)
        top.pack(fill=tk.X, padx=12, pady=8)
        mf = card(top, "Motor Speeds (PWM)", padding=12)
        mf.pack(fill=tk.X, pady=(0, 8))
        self.motor_labels = []
        for i in range(4):
            col = tk.Frame(mf, bg=BG)
            col.pack(side=tk.LEFT, expand=True)
            tk.Label(col, text=f"M{i+1}", bg=BG, fg=TEXT2, font=("Segoe UI", 8)).pack()
            lbl = tk.Label(col, text="1000", bg=BG, fg=ACCENT2, font=("Consolas", 18, "bold"))
            lbl.pack()
            self.motor_labels.append(lbl)
        rcf = card(top, "RC Channels", padding=12)
        rcf.pack(fill=tk.X, pady=(0, 8))
        self.rc_labels = []
        for i in range(8):
            col = tk.Frame(rcf, bg=BG)
            col.pack(side=tk.LEFT, expand=True)
            tk.Label(col, text=f"CH{i+1}", bg=BG, fg=TEXT2, font=("Segoe UI", 8)).pack()
            lbl = tk.Label(col, text="1500", bg=BG, fg=TEXT, font=("Consolas", 14, "bold"))
            lbl.pack()
            self.rc_labels.append(lbl)
        bf = card(top, "Battery", padding=12)
        bf.pack(fill=tk.X)
        brow = tk.Frame(bf, bg=BG)
        brow.pack()
        self.voltage_label = tk.Label(brow, text="0.0 V", bg=BG, fg=SUCCESS, font=("Consolas", 20, "bold"))
        self.voltage_label.pack(side=tk.LEFT, padx=30)
        self.current_label = tk.Label(brow, text="0.0 A", bg=BG, fg=WARNING, font=("Consolas", 20, "bold"))
        self.current_label.pack(side=tk.LEFT, padx=30)
        self.mah_label = tk.Label(brow, text="0 mAh", bg=BG, fg=TEXT2, font=("Consolas", 14))
        self.mah_label.pack(side=tk.LEFT, padx=30)

    # ── Sensors Tab ────────────────────────────────────────────────────────────
    def _create_sensors_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Sensors  ")
        vf = tk.Frame(tab, bg=BG2, pady=6)
        vf.pack(fill=tk.X, padx=12, pady=(8, 4))
        tk.Label(vf, text="3D Orientation", bg=BG2, fg=TEXT2, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=12)
        self.viz_btn = ttk.Button(vf, text="Launch 3D Visualizer", style="Accent.TButton", command=self._launch_visualizer)
        self.viz_btn.pack(side=tk.LEFT, padx=8)
        ttk.Button(vf, text="Stop", command=self._stop_visualizer).pack(side=tk.LEFT)
        self.viz_status_label = tk.Label(vf, text="Not running", bg=BG2, fg=TEXT2, font=("Segoe UI", 9))
        self.viz_status_label.pack(side=tk.LEFT, padx=12)
        row = tk.Frame(tab, bg=BG)
        row.pack(fill=tk.X, padx=12, pady=4)
        def sensor_card(parent, title, axes, attr_name):
            f = card(parent, title, padding=12)
            f.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
            labels = []
            for axis in axes:
                col = tk.Frame(f, bg=BG)
                col.pack(side=tk.LEFT, expand=True)
                tk.Label(col, text=axis, bg=BG, fg=TEXT2, font=("Segoe UI", 8, "bold")).pack()
                lbl = tk.Label(col, text="0.00", bg=BG, fg=WHITE, font=("Consolas", 14, "bold"))
                lbl.pack()
                labels.append(lbl)
            setattr(self, attr_name, labels)
        sensor_card(row, "Gyroscope (deg/s)", ["X", "Y", "Z"], "gyro_labels")
        sensor_card(row, "Accelerometer (g)", ["X", "Y", "Z"], "accel_labels")
        sensor_card(row, "Magnetometer", ["X", "Y", "Z"], "mag_labels")

    # ── Motor Test Tab ─────────────────────────────────────────────────────────
    def _create_motor_test_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Motor Test  ")
        warn = tk.Frame(tab, bg="#3b0a0a", pady=8)
        warn.pack(fill=tk.X, padx=12, pady=(8, 4))
        tk.Label(warn, text="WARNING: Remove propellers before using motor test!",
                 bg="#3b0a0a", fg=DANGER, font=("Segoe UI", 11, "bold")).pack()
        self.motor_test_enabled = tk.BooleanVar(value=False)
        chk = tk.Frame(tab, bg=BG)
        chk.pack(padx=12, pady=8, anchor=tk.W)
        ttk.Checkbutton(chk, text="I confirm props are removed — enable motor test",
                        variable=self.motor_test_enabled, command=self._toggle_motor_test).pack(side=tk.LEFT)
        sf = card(tab, "Motor PWM Control (1000 to 2000)", padding=14)
        sf.pack(fill=tk.X, padx=12, pady=4)
        self.motor_test_vars = [tk.IntVar(value=1000) for _ in range(4)]
        self.motor_test_sliders = []
        self.motor_test_value_labels = []
        for idx in range(4):
            row = tk.Frame(sf, bg=BG)
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=f"  M{idx+1}", bg=BG, fg=TEXT2, width=4, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
            slider = ttk.Scale(row, from_=1000, to=2000, orient=tk.HORIZONTAL, length=500,
                               command=lambda v, i=idx: self._on_motor_slider_change(i, v))
            slider.set(1000)
            slider.pack(side=tk.LEFT, padx=8)
            self.motor_test_sliders.append(slider)
            vl = tk.Label(row, text="1000", bg=BG, fg=ACCENT2, font=("Consolas", 12, "bold"), width=5)
            vl.pack(side=tk.LEFT)
            self.motor_test_value_labels.append(vl)
        btns = tk.Frame(tab, bg=BG)
        btns.pack(fill=tk.X, padx=12, pady=10)
        self.apply_motor_btn = ttk.Button(btns, text="Apply Values", style="Accent.TButton",
                                          command=self._apply_motor_test_values)
        self.apply_motor_btn.pack(side=tk.LEFT, padx=6)
        self.stop_all_motors_btn = ttk.Button(btns, text="Stop All", style="Danger.TButton",
                                              command=self._stop_all_motors)
        self.stop_all_motors_btn.pack(side=tk.LEFT, padx=6)
        self.motor_test_status = tk.Label(btns, text="Motor test disabled", bg=BG, fg=TEXT2, font=("Segoe UI", 9))
        self.motor_test_status.pack(side=tk.LEFT, padx=16)
        self._set_motor_test_widgets_state(False)

    def _set_motor_test_widgets_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        for slider in self.motor_test_sliders:
            slider.configure(state=state)
        self.apply_motor_btn.configure(state=state)
        self.stop_all_motors_btn.configure(state=state)

    def _toggle_motor_test(self):
        enabled = self.motor_test_enabled.get()
        self._set_motor_test_widgets_state(enabled)
        self.motor_test_status.config(
            text="Motor test ENABLED — be careful!" if enabled else "Motor test disabled",
            fg=WARNING if enabled else TEXT2)

    def _on_motor_slider_change(self, index, value):
        pwm = int(float(value))
        self.motor_test_vars[index].set(pwm)
        self.motor_test_value_labels[index].config(text=str(pwm))

    def _apply_motor_test_values(self):
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected to flight controller")
            return
        motor_values = [var.get() for var in self.motor_test_vars]
        if self.fc.set_motor_test_values(motor_values):
            self.motor_test_status.config(text=f"Applied: {motor_values}", fg=SUCCESS)
        else:
            messagebox.showerror("Motor Test", "Failed to send motor values")

    def _stop_all_motors(self):
        for idx, slider in enumerate(self.motor_test_sliders):
            slider.set(1000)
            self.motor_test_vars[idx].set(1000)
            self.motor_test_value_labels[idx].config(text="1000")
        if self.fc.connected:
            self.fc.set_motor_test_values([1000, 1000, 1000, 1000])
        self.motor_test_status.config(text="All motors stopped", fg=SUCCESS)

    # ── PID Tab ────────────────────────────────────────────────────────────────
    def _create_pid_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  PID Tuning  ")
        axes = ["Roll", "Pitch", "Yaw"]
        defaults = {"Roll": (42, 85, 35), "Pitch": (46, 90, 38), "Yaw": (40, 85, 0)}
        self.pid_vars = {}
        for axis in axes:
            f = card(tab, f"{axis} PID", padding=12)
            f.pack(fill=tk.X, padx=12, pady=5)
            p_var = tk.IntVar(value=defaults[axis][0])
            i_var = tk.IntVar(value=defaults[axis][1])
            d_var = tk.IntVar(value=defaults[axis][2])
            self.pid_vars[axis.lower()] = {"p": p_var, "i": i_var, "d": d_var}
            for col_idx, (label, var, color) in enumerate(
                    [("P", p_var, ACCENT), ("I", i_var, ACCENT2), ("D", d_var, SUCCESS)]):
                tk.Label(f, text=label, bg=BG, fg=color, font=("Segoe UI", 10, "bold"), width=3).grid(
                    row=0, column=col_idx*3, padx=(16, 4))
                ttk.Scale(f, from_=0, to=200, variable=var, orient=tk.HORIZONTAL, length=220).grid(
                    row=0, column=col_idx*3+1, padx=4)
                tk.Label(f, textvariable=var, bg=BG, fg=color, font=("Consolas", 10, "bold"), width=4).grid(
                    row=0, column=col_idx*3+2, padx=(0, 20))
        ttk.Button(tab, text="Apply PID (Preview)", style="Accent.TButton",
                   command=self._apply_pid_preview).pack(pady=14)

    # ── Rates Tab ──────────────────────────────────────────────────────────────
    def _create_rates_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Rates  ")
        self.rate_vars = {"rc_rate": tk.DoubleVar(value=1.00),
                          "super_rate": tk.DoubleVar(value=0.70),
                          "expo": tk.DoubleVar(value=0.15)}
        params = [("RC Rate", "rc_rate", 0.1, 2.5, ACCENT),
                  ("Super Rate", "super_rate", 0.0, 1.0, ACCENT2),
                  ("Expo", "expo", 0.0, 1.0, SUCCESS)]
        f = card(tab, "Rate Profile", padding=16)
        f.pack(fill=tk.X, padx=12, pady=10)
        for row_idx, (name, key, lo, hi, col) in enumerate(params):
            tk.Label(f, text=name, bg=BG, fg=col, font=("Segoe UI", 10), width=12, anchor=tk.W).grid(
                row=row_idx, column=0, padx=10, pady=8, sticky=tk.W)
            ttk.Scale(f, from_=lo, to=hi, variable=self.rate_vars[key], orient=tk.HORIZONTAL, length=400).grid(
                row=row_idx, column=1, padx=8)
            tk.Label(f, textvariable=self.rate_vars[key], bg=BG, fg=col, font=("Consolas", 10), width=6).grid(
                row=row_idx, column=2, padx=8)
        ttk.Button(tab, text="Apply Rates (Preview)", style="Accent.TButton",
                   command=self._apply_rates_preview).pack(pady=14)

    # ── Modes Tab ──────────────────────────────────────────────────────────────
    def _create_modes_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Modes  ")
        self.mode_vars = {"arm": tk.BooleanVar(value=True), "angle": tk.BooleanVar(value=False),
                          "horizon": tk.BooleanVar(value=False), "beeper": tk.BooleanVar(value=False),
                          "flip_over_after_crash": tk.BooleanVar(value=False)}
        f = card(tab, "Mode Mapping", padding=16)
        f.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        modes = [("ARM", "arm", "Arm / disarm the flight controller"),
                 ("ANGLE (Stabilized)", "angle", "Self-leveling mode"),
                 ("HORIZON (Semi-stable)", "horizon", "Mix of acro and angle modes"),
                 ("BEEPER", "beeper", "Trigger the FC buzzer"),
                 ("FLIP OVER AFTER CRASH", "flip_over_after_crash", "Reverse motors to flip drone")]
        for label, key, desc in modes:
            row = tk.Frame(f, bg=BG)
            row.pack(fill=tk.X, pady=4)
            ttk.Checkbutton(row, text=label, variable=self.mode_vars[key]).pack(side=tk.LEFT)
            tk.Label(row, text=f"  — {desc}", bg=BG, fg=TEXT2, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        ttk.Button(tab, text="Apply Modes (Preview)", style="Accent.TButton",
                   command=self._apply_modes_preview).pack(pady=14)

    # ── Calibration Tab ────────────────────────────────────────────────────────
    def _create_calibration_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Calibration  ")
        f = card(tab, "Sensor Calibration", padding=20)
        f.pack(fill=tk.X, padx=12, pady=12)
        tk.Label(f, text="Calibrate your sensors before first flight for best accuracy.",
                 bg=BG, fg=TEXT2, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 14))
        btns = tk.Frame(f, bg=BG)
        btns.pack(anchor=tk.W)
        ttk.Button(btns, text="Calibrate Accelerometer", style="Accent.TButton",
                   command=self._calibrate_accel).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Calibrate Magnetometer",
                   command=self._calibrate_mag).pack(side=tk.LEFT, padx=6)
        tk.Label(tab, text="Accel: Place drone flat on a level surface.\n"
                           "Mag: Rotate drone slowly through all orientations.",
                 bg=BG, fg=TEXT2, font=("Segoe UI", 9), justify=tk.LEFT).pack(
            anchor=tk.W, padx=24, pady=12)

    # ── Configure Tab ──────────────────────────────────────────────────────────
    def _create_configure_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Configure  ")
        f = card(tab, "Flight Controller Settings", padding=16)
        f.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.arming_disabled_var = tk.BooleanVar(value=False)
        self.airmode_var = tk.BooleanVar(value=True)
        self.anti_gravity_var = tk.BooleanVar(value=True)
        opts = [("Arming Disabled", self.arming_disabled_var, "Prevent arming until resolved"),
                ("Air Mode", self.airmode_var, "Keep motors active at zero throttle"),
                ("Anti-Gravity", self.anti_gravity_var, "Boost I-term during throttle changes")]
        for label, var, desc in opts:
            row = tk.Frame(f, bg=BG)
            row.pack(fill=tk.X, pady=6)
            ttk.Checkbutton(row, text=label, variable=var).pack(side=tk.LEFT)
            tk.Label(row, text=f"  — {desc}", bg=BG, fg=TEXT2, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        ttk.Button(f, text="Save Configuration", style="Accent.TButton",
                   command=self._save_config).pack(anchor=tk.W, pady=20)

    # ── Profiles Tab ───────────────────────────────────────────────────────────
    def _create_profiles_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Profiles  ")
        pane = tk.PanedWindow(tab, orient=tk.HORIZONTAL, bg=BORDER, sashwidth=2, sashrelief="flat")
        pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        # Left panel
        left = tk.Frame(pane, bg=BG, width=260)
        pane.add(left, minsize=220)
        tk.Label(left, text="SAVED PROFILES", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=12, pady=(10, 4))
        lb_frame = tk.Frame(left, bg=BG)
        lb_frame.pack(fill=tk.BOTH, expand=True, padx=12)
        sb = ttk.Scrollbar(lb_frame, orient=tk.VERTICAL)
        self.profile_listbox = tk.Listbox(lb_frame, yscrollcommand=sb.set, bg=BG3, fg=TEXT,
                                          selectbackground=ACCENT, selectforeground=WHITE,
                                          relief="flat", font=("Segoe UI", 10), activestyle="none",
                                          borderwidth=0, highlightthickness=0)
        sb.config(command=self.profile_listbox.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.profile_listbox.pack(fill=tk.BOTH, expand=True)
        self.profile_listbox.bind("<<ListboxSelect>>", self._on_profile_select)
        btns_left = tk.Frame(left, bg=BG)
        btns_left.pack(fill=tk.X, padx=12, pady=8)
        ttk.Button(btns_left, text="Load", command=self._load_selected_profile).pack(side=tk.LEFT, padx=3)
        ttk.Button(btns_left, text="Delete", style="Danger.TButton",
                   command=self._delete_selected_profile).pack(side=tk.LEFT, padx=3)
        # Right panel
        right = tk.Frame(pane, bg=BG)
        pane.add(right, minsize=400)
        tk.Label(right, text="PROFILE EDITOR", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=16, pady=(10, 4))
        form = card(right, "", padding=16)
        form.pack(fill=tk.X, padx=12, pady=4)
        self.pf_name_var = tk.StringVar()
        self.pf_callsign_var = tk.StringVar()
        self.pf_fctype_var = tk.StringVar(value="F722")
        self.pf_bio_var = tk.StringVar()
        for label, var in [("Name", self.pf_name_var), ("Callsign", self.pf_callsign_var),
                            ("FC Type", self.pf_fctype_var), ("Bio", self.pf_bio_var)]:
            row = tk.Frame(form, bg=BG)
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=label, bg=BG, fg=TEXT2, font=("Segoe UI", 9),
                     width=12, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        color_row = tk.Frame(form, bg=BG)
        color_row.pack(fill=tk.X, pady=4)
        tk.Label(color_row, text="Avatar Color", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9), width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.pf_color_var = tk.StringVar(value=ACCENT)
        self.pf_color_btn = tk.Button(color_row, text="  Choose  ", bg=ACCENT, fg=WHITE,
                                      relief="flat", command=self._pick_profile_color, cursor="hand2")
        self.pf_color_btn.pack(side=tk.LEFT)
        tk.Label(right, text="Notes", bg=BG, fg=TEXT2, font=("Segoe UI", 9)).pack(
            anchor=tk.W, padx=28, pady=(10, 2))
        self.pf_notes_text = dark_text(right, height=5)
        self.pf_notes_text.pack(fill=tk.X, padx=12, pady=(0, 8))
        btn_row = tk.Frame(right, bg=BG)
        btn_row.pack(fill=tk.X, padx=12, pady=4)
        ttk.Button(btn_row, text="Save Profile", style="Accent.TButton",
                   command=self._save_profile).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="New Profile", command=self._new_profile_form).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Set Active", style="Success.TButton",
                   command=self._set_profile_active).pack(side=tk.LEFT, padx=4)
        self._refresh_profile_list()

    def _refresh_profile_list(self):
        self.profile_listbox.delete(0, tk.END)
        self._profile_cache = self.profiles_mgr.list_profiles()
        active = self.profiles_mgr.get_active()
        for p in self._profile_cache:
            marker = "● " if (active and active.callsign == p.callsign) else "  "
            self.profile_listbox.insert(tk.END, f"{marker}{p.callsign}  —  {p.name}")

    def _on_profile_select(self, event=None):
        sel = self.profile_listbox.curselection()
        if not sel:
            return
        p = self._profile_cache[sel[0]]
        self.pf_name_var.set(p.name)
        self.pf_callsign_var.set(p.callsign)
        self.pf_fctype_var.set(p.fc_type)
        self.pf_bio_var.set(p.bio)
        self.pf_color_var.set(p.avatar_color)
        self.pf_color_btn.config(bg=p.avatar_color)
        self.pf_notes_text.delete("1.0", tk.END)
        self.pf_notes_text.insert("1.0", p.notes)

    def _pick_profile_color(self):
        result = colorchooser.askcolor(color=self.pf_color_var.get(), title="Pick Avatar Color")
        if result and result[1]:
            self.pf_color_var.set(result[1])
            self.pf_color_btn.config(bg=result[1])

    def _save_profile(self):
        name = self.pf_name_var.get().strip()
        cs = self.pf_callsign_var.get().strip().upper()
        if not name or not cs:
            messagebox.showwarning("Profiles", "Name and callsign are required.")
            return
        notes = self.pf_notes_text.get("1.0", tk.END).strip()
        p = Profile(name=name, callsign=cs, bio=self.pf_bio_var.get().strip(),
                    fc_type=self.pf_fctype_var.get().strip() or "F722",
                    avatar_color=self.pf_color_var.get(), notes=notes)
        if self.profiles_mgr.save(p):
            self._refresh_profile_list()
            messagebox.showinfo("Profiles", f"Profile '{cs}' saved.")
        else:
            messagebox.showerror("Profiles", "Failed to save profile.")

    def _new_profile_form(self):
        self.pf_name_var.set("")
        self.pf_callsign_var.set("")
        self.pf_fctype_var.set("F722")
        self.pf_bio_var.set("")
        self.pf_color_var.set(ACCENT)
        self.pf_color_btn.config(bg=ACCENT)
        self.pf_notes_text.delete("1.0", tk.END)

    def _load_selected_profile(self):
        sel = self.profile_listbox.curselection()
        if not sel:
            messagebox.showinfo("Profiles", "Select a profile from the list.")
            return
        self._on_profile_select()

    def _delete_selected_profile(self):
        sel = self.profile_listbox.curselection()
        if not sel:
            return
        p = self._profile_cache[sel[0]]
        if messagebox.askyesno("Delete Profile", f"Delete profile '{p.callsign}'?"):
            self.profiles_mgr.delete(p.callsign)
            self._refresh_profile_list()

    def _set_profile_active(self):
        cs = self.pf_callsign_var.get().strip().upper()
        if not cs:
            messagebox.showwarning("Profiles", "Save a profile first.")
            return
        p = self.profiles_mgr.load(cs)
        if not p:
            messagebox.showwarning("Profiles", "Save the profile before setting it active.")
            return
        self.profiles_mgr.set_active(p)
        self.profile_pill_var.set(f"{p.callsign}  ({p.name})")
        self._refresh_profile_list()
        messagebox.showinfo("Profiles", f"Active pilot: {p.callsign}")

    # ── Community Tab ──────────────────────────────────────────────────────────
    def _create_community_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Community  ")
        hdr = tk.Frame(tab, bg=BG2, pady=8)
        hdr.pack(fill=tk.X, padx=12, pady=(8, 4))
        tk.Label(hdr, text="Community Board", bg=BG2, fg=WHITE,
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=12)
        self.board_count_var = tk.StringVar(value=f"{len(self.community.get_all())} messages")
        tk.Label(hdr, textvariable=self.board_count_var, bg=BG2, fg=TEXT2,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=8)
        search_row = tk.Frame(tab, bg=BG)
        search_row.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(search_row, text="Search:", bg=BG, fg=TEXT2, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.board_search_var = tk.StringVar()
        self.board_search_var.trace_add("write", lambda *_: self._refresh_board())
        ttk.Entry(search_row, textvariable=self.board_search_var, width=30).pack(side=tk.LEFT, padx=6)
        ttk.Button(search_row, text="Refresh", command=self._refresh_board).pack(side=tk.LEFT, padx=6)
        feed_frame = tk.Frame(tab, bg=BG)
        feed_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)
        vsb = ttk.Scrollbar(feed_frame, orient=tk.VERTICAL)
        self.board_canvas = tk.Canvas(feed_frame, bg=BG, yscrollcommand=vsb.set, highlightthickness=0)
        vsb.config(command=self.board_canvas.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.board_canvas.pack(fill=tk.BOTH, expand=True)
        self.board_inner = tk.Frame(self.board_canvas, bg=BG)
        self._board_window = self.board_canvas.create_window((0, 0), window=self.board_inner, anchor="nw")
        self.board_inner.bind("<Configure>", lambda e: (
            self.board_canvas.configure(scrollregion=self.board_canvas.bbox("all")),
            self.board_canvas.itemconfig(self._board_window, width=self.board_canvas.winfo_width())))
        self.board_canvas.bind("<Configure>", lambda e:
            self.board_canvas.itemconfig(self._board_window, width=e.width))
        self.board_canvas.bind("<MouseWheel>",
            lambda e: self.board_canvas.yview_scroll(-1*(e.delta//120), "units"))
        compose = card(tab, "Post a Message", padding=12)
        compose.pack(fill=tk.X, padx=12, pady=8)
        compose_top = tk.Frame(compose, bg=BG)
        compose_top.pack(fill=tk.X, pady=(0, 6))
        tk.Label(compose_top, text="Post as:", bg=BG, fg=TEXT2, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.board_callsign_var = tk.StringVar(value="YOUR_CALLSIGN")
        ttk.Entry(compose_top, textvariable=self.board_callsign_var, width=14).pack(side=tk.LEFT, padx=6)
        self.board_msgtype_var = tk.StringVar(value="text")
        type_frame = tk.Frame(compose_top, bg=BG)
        type_frame.pack(side=tk.LEFT, padx=12)
        for label, val in [("Text", "text"), ("Tip", "tip"), ("Share Tune", "tune_share")]:
            ttk.Radiobutton(type_frame, text=label, variable=self.board_msgtype_var, value=val).pack(side=tk.LEFT, padx=4)
        self.board_msg_text = dark_text(compose, height=3)
        self.board_msg_text.pack(fill=tk.X, pady=(0, 6))
        btn_row = tk.Frame(compose, bg=BG)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Send Message", style="Accent.TButton",
                   command=self._post_message).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Share Current Tune",
                   command=self._share_tune_in_board).pack(side=tk.LEFT, padx=4)
        self._refresh_board()

    def _refresh_board(self):
        for w in self.board_inner.winfo_children():
            w.destroy()
        query = self.board_search_var.get().strip() if hasattr(self, "board_search_var") else ""
        messages = self.community.search(query) if query else self.community.get_recent(100)
        if not messages:
            tk.Label(self.board_inner, text="No messages yet. Be the first to post!",
                     bg=BG, fg=TEXT2, font=("Segoe UI", 10)).pack(pady=20)
            return
        type_colors = {"welcome": ACCENT2, "tip": SUCCESS, "tune_share": WARNING, "text": TEXT}
        type_icons = {"welcome": "[WELCOME] ", "tip": "[TIP] ", "tune_share": "[TUNE] ", "text": ""}
        for msg in reversed(messages):
            bubble = tk.Frame(self.board_inner, bg=BG2, padx=12, pady=8)
            bubble.pack(fill=tk.X, padx=6, pady=3)
            hrow = tk.Frame(bubble, bg=BG2)
            hrow.pack(fill=tk.X)
            av = tk.Label(hrow, text=msg.callsign[:2], bg=msg.avatar_color, fg=WHITE,
                          font=("Segoe UI", 9, "bold"), width=4, relief="flat", padx=2)
            av.pack(side=tk.LEFT, padx=(0, 8))
            tc = type_colors.get(msg.msg_type, TEXT)
            icon = type_icons.get(msg.msg_type, "")
            tk.Label(hrow, text=f"{icon}{msg.callsign}  ({msg.author})",
                     bg=BG2, fg=tc, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            tk.Label(hrow, text=msg.timestamp, bg=BG2, fg=TEXT2, font=("Segoe UI", 8)).pack(side=tk.RIGHT)
            tk.Label(bubble, text=msg.content, bg=BG2, fg=TEXT, font=("Segoe UI", 10),
                     wraplength=700, justify=tk.LEFT, anchor=tk.W).pack(fill=tk.X, pady=(4, 0))
            tk.Frame(self.board_inner, bg=BORDER, height=1).pack(fill=tk.X, padx=6)
        self.board_count_var.set(f"{len(self.community.get_all())} messages")
        self.board_canvas.after(50, lambda: self.board_canvas.yview_moveto(1.0))

    def _post_message(self):
        cs = self.board_callsign_var.get().strip().upper()
        content = self.board_msg_text.get("1.0", tk.END).strip()
        if not cs or cs == "YOUR_CALLSIGN":
            messagebox.showwarning("Community", "Set your callsign before posting.")
            return
        if not content:
            messagebox.showwarning("Community", "Message cannot be empty.")
            return
        active = self.profiles_mgr.get_active()
        author = active.name if active else cs
        color = active.avatar_color if active else ACCENT
        self.community.post(author, cs, content, self.board_msgtype_var.get(), color)
        self.board_msg_text.delete("1.0", tk.END)
        self._refresh_board()

    def _share_tune_in_board(self):
        cs = self.board_callsign_var.get().strip().upper()
        if not cs or cs == "YOUR_CALLSIGN":
            messagebox.showwarning("Community", "Set your callsign before sharing.")
            return
        pid = self._get_current_pid()
        rates = self._get_current_rates()
        content = (
            f"Sharing my current tune:\n"
            f"Roll  P:{pid['roll']['p']} I:{pid['roll']['i']} D:{pid['roll']['d']} | "
            f"Pitch P:{pid['pitch']['p']} I:{pid['pitch']['i']} D:{pid['pitch']['d']} | "
            f"Yaw  P:{pid['yaw']['p']} I:{pid['yaw']['i']} D:{pid['yaw']['d']}\n"
            f"RC Rate: {rates['rc_rate']:.2f}  Super: {rates['super_rate']:.2f}  Expo: {rates['expo']:.2f}"
        )
        active = self.profiles_mgr.get_active()
        author = active.name if active else cs
        color = active.avatar_color if active else ACCENT
        self.community.post(author, cs, content, "tune_share", color)
        self._refresh_board()
        messagebox.showinfo("Community", "Tune shared to the board!")

    # ── Tunes Tab ──────────────────────────────────────────────────────────────
    def _create_tunes_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Tunes Library  ")
        pane = tk.PanedWindow(tab, orient=tk.HORIZONTAL, bg=BORDER, sashwidth=2)
        pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        # Left
        left = tk.Frame(pane, bg=BG, width=280)
        pane.add(left, minsize=230)
        tk.Label(left, text="AVAILABLE TUNES", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=12, pady=(10, 4))
        filter_row = tk.Frame(left, bg=BG)
        filter_row.pack(fill=tk.X, padx=12, pady=(0, 6))
        tk.Label(filter_row, text="Filter:", bg=BG, fg=TEXT2, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.tune_filter_var = tk.StringVar()
        self.tune_filter_var.trace_add("write", lambda *_: self._refresh_tune_list())
        ttk.Entry(filter_row, textvariable=self.tune_filter_var, width=18).pack(side=tk.LEFT, padx=4)
        lb_frame = tk.Frame(left, bg=BG)
        lb_frame.pack(fill=tk.BOTH, expand=True, padx=12)
        vsb = ttk.Scrollbar(lb_frame, orient=tk.VERTICAL)
        self.tune_listbox = tk.Listbox(lb_frame, yscrollcommand=vsb.set, bg=BG3, fg=TEXT,
                                       selectbackground=ACCENT, selectforeground=WHITE, relief="flat",
                                       font=("Segoe UI", 10), activestyle="none",
                                       borderwidth=0, highlightthickness=0)
        vsb.config(command=self.tune_listbox.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tune_listbox.pack(fill=tk.BOTH, expand=True)
        self.tune_listbox.bind("<<ListboxSelect>>", self._on_tune_select)
        tune_btns = tk.Frame(left, bg=BG)
        tune_btns.pack(fill=tk.X, padx=12, pady=8)
        ttk.Button(tune_btns, text="Import (.json)", command=self._import_tune).pack(side=tk.LEFT, padx=3)
        ttk.Button(tune_btns, text="Delete", style="Danger.TButton",
                   command=self._delete_selected_tune).pack(side=tk.LEFT, padx=3)
        # Right
        right = tk.Frame(pane, bg=BG)
        pane.add(right, minsize=420)
        tk.Label(right, text="TUNE DETAILS", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=16, pady=(10, 4))
        detail = card(right, "", padding=16)
        detail.pack(fill=tk.X, padx=12, pady=4)
        self.tune_name_var = tk.StringVar(value="Select a tune")
        self.tune_author_var = tk.StringVar(value="—")
        self.tune_fc_var = tk.StringVar(value="—")
        self.tune_tags_var = tk.StringVar(value="")
        for label, var, fg_color in [("Name", self.tune_name_var, WHITE),
                                     ("Author", self.tune_author_var, ACCENT2),
                                     ("FC Type", self.tune_fc_var, TEXT),
                                     ("Tags", self.tune_tags_var, WARNING)]:
            row = tk.Frame(detail, bg=BG)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, bg=BG, fg=TEXT2, font=("Segoe UI", 9), width=10, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, textvariable=var, bg=BG, fg=fg_color, font=("Segoe UI", 10, "bold"), anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(right, text="Description", bg=BG, fg=TEXT2, font=("Segoe UI", 9)).pack(
            anchor=tk.W, padx=28, pady=(8, 2))
        self.tune_desc_label = tk.Label(right, text="", bg=BG, fg=TEXT, font=("Segoe UI", 9),
                                         wraplength=380, justify=tk.LEFT, anchor=tk.W)
        self.tune_desc_label.pack(anchor=tk.W, padx=28)
        tk.Label(right, text="PID Preview", bg=BG, fg=TEXT2, font=("Segoe UI", 9, "bold")).pack(
            anchor=tk.W, padx=28, pady=(12, 2))
        self.tune_pid_text = dark_text(right, height=4, state=tk.DISABLED, font=("Consolas", 10))
        self.tune_pid_text.pack(fill=tk.X, padx=12, pady=(0, 4))
        act = tk.Frame(right, bg=BG)
        act.pack(fill=tk.X, padx=12, pady=10)
        ttk.Button(act, text="Load Tune into PID/Rates", style="Accent.TButton",
                   command=self._load_selected_tune).pack(side=tk.LEFT, padx=4)
        ttk.Button(act, text="Save Current as Tune",
                   command=self._save_current_as_tune).pack(side=tk.LEFT, padx=4)
        ttk.Button(act, text="Export Tune (.json)",
                   command=self._export_selected_tune).pack(side=tk.LEFT, padx=4)
        self._refresh_tune_list()

    def _refresh_tune_list(self):
        self.tune_listbox.delete(0, tk.END)
        query = self.tune_filter_var.get().strip().lower() if hasattr(self, "tune_filter_var") else ""
        self._tune_cache = self.tunes_mgr.list_tunes()
        if query:
            self._tune_cache = [t for t in self._tune_cache
                                if query in t.name.lower() or any(query in tag for tag in t.tags)
                                or query in t.author.lower()]
        for t in self._tune_cache:
            marker = "[built-in]  " if t.builtin else "[custom]   "
            self.tune_listbox.insert(tk.END, f"{marker}{t.name}  ({t.author})")

    def _on_tune_select(self, event=None):
        sel = self.tune_listbox.curselection()
        if not sel:
            return
        t = self._tune_cache[sel[0]]
        self._selected_tune = t
        self.tune_name_var.set(t.name)
        self.tune_author_var.set(t.author)
        self.tune_fc_var.set(t.fc_type)
        self.tune_tags_var.set("  ".join(f"#{tag}" for tag in t.tags))
        self.tune_desc_label.config(text=t.description)
        self.tune_pid_text.config(state=tk.NORMAL)
        self.tune_pid_text.delete("1.0", tk.END)
        self.tune_pid_text.insert("1.0", t.get_pid_summary())
        self.tune_pid_text.config(state=tk.DISABLED)

    def _load_selected_tune(self):
        if not self._selected_tune:
            messagebox.showinfo("Tunes", "Select a tune first.")
            return
        t = self._selected_tune
        for axis in ["roll", "pitch", "yaw"]:
            if axis in t.pid and axis in self.pid_vars:
                self.pid_vars[axis]["p"].set(t.pid[axis].get("p", 42))
                self.pid_vars[axis]["i"].set(t.pid[axis].get("i", 85))
                self.pid_vars[axis]["d"].set(t.pid[axis].get("d", 35))
        self.rate_vars["rc_rate"].set(t.rates.get("rc_rate", 1.0))
        self.rate_vars["super_rate"].set(t.rates.get("super_rate", 0.7))
        self.rate_vars["expo"].set(t.rates.get("expo", 0.15))
        messagebox.showinfo("Tunes", f"Tune '{t.name}' loaded into PID & Rates tabs.")

    def _save_current_as_tune(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Current Tune")
        dialog.configure(bg=BG)
        dialog.geometry("400x280")
        dialog.grab_set()
        tk.Label(dialog, text="Save Current PID & Rates as a Tune",
                 bg=BG, fg=WHITE, font=("Segoe UI", 11, "bold")).pack(pady=12)
        fields = {}
        for label, default in [("Tune Name", "My Tune"), ("Author", "Me"), ("Tags (comma-sep)", "custom")]:
            row = tk.Frame(dialog, bg=BG)
            row.pack(fill=tk.X, padx=20, pady=4)
            tk.Label(row, text=label, bg=BG, fg=TEXT2, width=18, anchor=tk.W,
                     font=("Segoe UI", 9)).pack(side=tk.LEFT)
            var = tk.StringVar(value=default)
            ttk.Entry(row, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)
            fields[label] = var
        tk.Label(dialog, text="Description", bg=BG, fg=TEXT2, font=("Segoe UI", 9)).pack(anchor=tk.W, padx=20)
        desc_text = dark_text(dialog, height=3)
        desc_text.pack(fill=tk.X, padx=20, pady=(2, 8))
        def _do_save():
            tune_name = fields["Tune Name"].get().strip()
            if not tune_name:
                messagebox.showwarning("Tunes", "Name is required.", parent=dialog)
                return
            tags = [t.strip() for t in fields["Tags (comma-sep)"].get().split(",") if t.strip()]
            tune = Tune({"name": tune_name, "author": fields["Author"].get().strip() or "Me",
                         "description": desc_text.get("1.0", tk.END).strip(),
                         "fc_type": "F722", "tags": tags,
                         "pid": self._get_current_pid(), "rates": self._get_current_rates(),
                         "builtin": False})
            if self.tunes_mgr.save_tune(tune):
                self._refresh_tune_list()
                dialog.destroy()
                messagebox.showinfo("Tunes", f"Tune '{tune_name}' saved!")
            else:
                messagebox.showerror("Tunes", "Failed to save tune.", parent=dialog)
        ttk.Button(dialog, text="Save", style="Accent.TButton", command=_do_save).pack(pady=4)

    def _import_tune(self):
        path = filedialog.askopenfilename(title="Import Tune",
            filetypes=[("JSON Tune", "*.json"), ("All Files", "*.*")])
        if path:
            tune = self.tunes_mgr.import_from_file(path)
            if tune:
                self._refresh_tune_list()
                messagebox.showinfo("Tunes", f"Imported tune '{tune.name}'.")
            else:
                messagebox.showerror("Tunes", "Failed to import tune.")

    def _export_selected_tune(self):
        if not self._selected_tune:
            messagebox.showinfo("Tunes", "Select a tune to export.")
            return
        t = self._selected_tune
        safe = t.name.replace(" ", "_").replace("/", "_")
        path = filedialog.asksaveasfilename(title="Export Tune", defaultextension=".json",
            initialfile=f"{safe}_tune.json", filetypes=[("JSON Tune", "*.json")])
        if path:
            if self.tunes_mgr.export_to_file(t, path):
                messagebox.showinfo("Tunes", f"Exported to:\n{path}")
            else:
                messagebox.showerror("Tunes", "Export failed.")

    def _delete_selected_tune(self):
        sel = self.tune_listbox.curselection()
        if not sel:
            return
        t = self._tune_cache[sel[0]]
        if t.builtin:
            messagebox.showinfo("Tunes", "Built-in tunes cannot be deleted.")
            return
        if messagebox.askyesno("Delete Tune", f"Delete tune '{t.name}'?"):
            self.tunes_mgr.delete_tune(t)
            self._refresh_tune_list()

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _get_current_pid(self):
        return {axis: {k: self.pid_vars[axis][k].get() for k in ("p", "i", "d")}
                for axis in ("roll", "pitch", "yaw")}

    def _get_current_rates(self):
        return {k: round(v.get(), 3) for k, v in self.rate_vars.items()}

    # ── Connection ─────────────────────────────────────────────────────────────
    def _refresh_ports(self):
        try:
            ports = self.fc.serial.list_ports()
            port_names = [p["port"] for p in ports]
            self.port_combo["values"] = port_names
            if port_names:
                self.port_combo.current(0)
        except Exception:
            pass

    def _connect(self):
        if self.fc.connected:
            self.fc.disconnect()
            self.connect_btn.config(text="Connect", style="Accent.TButton")
            self.status_var.set("  Disconnected")
            self.status_label.config(fg=DANGER)
            self.device_var.set("No device")
            self.stop_update = True
            return
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "Select a serial port first.")
            return
        if self.fc.connect(port):
            self.connect_btn.config(text="Disconnect")
            self.status_var.set("  Connected")
            self.status_label.config(fg=SUCCESS)
            self._update_device_info()
            self.stop_update = False
            self._start_telemetry_update()
        else:
            messagebox.showerror("Connection Error",
                                 f"Could not connect to {port}.\nCheck that no other software is using the port.")

    def _update_device_info(self):
        info = self.fc.device_info
        dev = info.get("fc_variant") or info.get("type") or info.get("board_id") or "Unknown"
        ver = info.get("fc_version") or info.get("version") or "?"
        self.device_var.set(f"{dev}  fw {ver}")

    def _start_telemetry_update(self):
        if self.update_thread is None or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self._telemetry_loop, daemon=True)
            self.update_thread.start()

    def _telemetry_loop(self):
        while not self.stop_update and self.fc.connected:
            try:
                self.fc.get_telemetry()
                self._update_display()
                time.sleep(0.02)
            except Exception as e:
                logger.error(f"Telemetry error: {e}")
                break

    def _update_display(self):
        try:
            for i, speed in enumerate(self.fc.motor_speeds[:4]):
                self.motor_labels[i].config(text=str(speed))
            for i, ch in enumerate(self.fc.rc_channels[:8]):
                if i < len(self.rc_labels):
                    self.rc_labels[i].config(text=str(ch))
            if self.fc.sensor_data:
                gyro = self.fc.sensor_data.get("gyro", {})
                for i, axis in enumerate(["x", "y", "z"]):
                    self.gyro_labels[i].config(text=f"{gyro.get(axis, 0):.2f}")
                if self.visualizer and self.visualizer.running:
                    self.visualizer.send_gyro_data(gyro)
                acc = self.fc.sensor_data.get("accelerometer", {})
                for i, axis in enumerate(["x", "y", "z"]):
                    self.accel_labels[i].config(text=f"{acc.get(axis, 0):.2f}")
                mag = self.fc.sensor_data.get("magnetometer", {})
                for i, axis in enumerate(["x", "y", "z"]):
                    self.mag_labels[i].config(text=str(mag.get(axis, 0)))
            if "vbat" in self.fc.status_data:
                v = self.fc.status_data["vbat"]
                color = SUCCESS if v >= 14.8 else (WARNING if v >= 13.5 else DANGER)
                self.voltage_label.config(text=f"{v:.1f} V", fg=color)
            if "amperage" in self.fc.status_data:
                self.current_label.config(text=f"{self.fc.status_data['amperage']:.1f} A")
            if "mah" in self.fc.status_data:
                self.mah_label.config(text=f"{self.fc.status_data['mah']} mAh")
        except Exception as e:
            logger.error(f"Display update error: {e}")

    # ── Calibration ────────────────────────────────────────────────────────────
    def _calibrate_accel(self):
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected.")
            return
        if messagebox.askokcancel("Calibration", "Place drone flat on level surface, then click OK."):
            self.fc.calibrate_accelerometer()
            messagebox.showinfo("Done", "Accelerometer calibrated.")

    def _calibrate_mag(self):
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected.")
            return
        if messagebox.askokcancel("Calibration", "Slowly rotate drone through all orientations, then click OK."):
            self.fc.calibrate_magnetometer()
            messagebox.showinfo("Done", "Magnetometer calibrated.")

    # ── Config Previews ────────────────────────────────────────────────────────
    def _save_config(self):
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected.")
            return
        self.fc.save_configuration()
        messagebox.showinfo("Success", "Configuration saved to EEPROM.")

    def _apply_pid_preview(self):
        messagebox.showinfo("PID", "PID values updated in UI. Connect FC to apply via MSP.")

    def _apply_rates_preview(self):
        messagebox.showinfo("Rates", "Rates updated in UI. Connect FC to apply via MSP.")

    def _apply_modes_preview(self):
        messagebox.showinfo("Modes", "Modes updated in UI. Connect FC to apply via MSP.")

    # ── Visualizer ─────────────────────────────────────────────────────────────
    def _launch_visualizer(self):
        if not self.fc.connected:
            messagebox.showerror("Error", "Not connected.")
            return
        if not self.visualizer:
            messagebox.showerror("Error", "3D visualization not available (vpython not installed).")
            return
        if not self.visualizer.running:
            if self.visualizer.start():
                self.viz_status_label.config(text="Running", fg=SUCCESS)
            else:
                messagebox.showerror("Error", "Failed to start visualizer.")

    def _stop_visualizer(self):
        if self.visualizer and self.visualizer.running:
            self.visualizer.stop()
            self.viz_status_label.config(text="Not running", fg=TEXT2)

    def on_closing(self):
        self.stop_update = True
        self._stop_visualizer()
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
