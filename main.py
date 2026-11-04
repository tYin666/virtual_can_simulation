import time
import tkinter as tk
from tkinter import ttk


BACKGROUND = "#171a18"
PANEL = "#202421"
RAISED = "#262b27"
LINE = "#373d38"
TEXT = "#edf0e9"
MUTED = "#8c938b"
QUIET = "#5f665f"
ACID = "#c5f36b"
ORANGE = "#ff9a61"
MONO = ("DejaVu Sans Mono", 10)
SANS = ("DejaVu Sans", 10)


class SpeedLab(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CAN Speed Lab | ECU Simulator")
        self.geometry("1080x720")
        self.minsize(760, 600)
        self.configure(background=BACKGROUND)

        self.speed = tk.IntVar(value=0)
        self.sequence = 0
        self.streaming = False
        self.stream_job = None
        self.animation_job = None
        self.packet_position = 0
        self.packet_direction = 1
        self.bus_bounds = (0, 0)

        self._configure_styles()
        self._build_interface()
        self._update_speed()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Body.TFrame", background=BACKGROUND)
        style.configure("Title.TLabel", background=BACKGROUND, foreground=TEXT, font=("DejaVu Sans", 25, "bold"))
        style.configure("Eyebrow.TLabel", background=BACKGROUND, foreground=ORANGE, font=MONO)
        style.configure("PanelTitle.TLabel", background=PANEL, foreground="#b6bdb5", font=("DejaVu Sans Mono", 9))
        style.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=MONO)
        style.configure("Meta.TLabel", background=PANEL, foreground="#c9d0c8", font=("DejaVu Sans Mono", 9))
        style.configure("Speed.TLabel", background=PANEL, foreground=TEXT, font=("DejaVu Sans Mono", 48))
        style.configure("Unit.TLabel", background=PANEL, foreground=MUTED, font=MONO)
        style.configure("Accent.TButton", background=ACID, foreground="#1a2015", font=("DejaVu Sans", 9, "bold"), padding=(14, 9), borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#d7ff8e")])
        style.configure("Stop.TButton", background=PANEL, foreground=TEXT, font=("DejaVu Sans", 9, "bold"), padding=(14, 9), borderwidth=1)
        style.map("Stop.TButton", background=[("active", RAISED)])
        style.configure("Treeview", background="#1c201d", fieldbackground="#1c201d", foreground="#c8cec7", rowheight=36, borderwidth=0, font=("DejaVu Sans Mono", 9))
        style.configure("Treeview.Heading", background=PANEL, foreground=QUIET, relief="flat", font=("DejaVu Sans Mono", 8))
        style.map("Treeview", background=[("selected", "#333a32")], foreground=[("selected", TEXT)])

    def _build_interface(self):
        shell = ttk.Frame(self, style="Body.TFrame", padding=(28, 22))
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)

        header = tk.Frame(shell, bg=BACKGROUND)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)
        mark = tk.Label(header, text="CAN", bg=BACKGROUND, fg=ACID, font=("DejaVu Sans Mono", 10), padx=8, pady=7, highlightthickness=1, highlightbackground=ACID)
        mark.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 11))
        tk.Label(header, text="CAN SPEED LAB", bg=BACKGROUND, fg=TEXT, font=("DejaVu Sans", 10, "bold")).grid(row=0, column=1, sticky="sw")
        tk.Label(header, text="BENCH SIMULATOR / 01", bg=BACKGROUND, fg=MUTED, font=("DejaVu Sans Mono", 8)).grid(row=1, column=1, sticky="nw", pady=(2, 0))
        tk.Label(header, text="●  SIMULATION MODE     LOCAL SESSION", bg=BACKGROUND, fg=ACID, font=("DejaVu Sans Mono", 8)).grid(row=0, column=2, rowspan=2, sticky="e")

        title_block = tk.Frame(shell, bg=BACKGROUND)
        title_block.grid(row=1, column=0, sticky="ew", pady=(30, 20))
        tk.Label(title_block, text="SIGNAL BENCH / VEHICLE DYNAMICS", bg=BACKGROUND, fg=ORANGE, font=("DejaVu Sans Mono", 8)).pack(anchor="w")
        ttk.Label(title_block, text="Vehicle speed ECU", style="Title.TLabel").pack(anchor="w", pady=(6, 0))
        tk.Label(title_block, text="Adjust the signal value and watch the simulated bus update in real time.", bg=BACKGROUND, fg=MUTED, font=SANS).pack(anchor="w", pady=(5, 0))

        panels = tk.Frame(shell, bg=LINE, padx=1, pady=1)
        panels.grid(row=2, column=0, sticky="nsew")
        shell.rowconfigure(2, weight=1)
        panels.columnconfigure(0, weight=3, uniform="panels")
        panels.columnconfigure(1, weight=2, uniform="panels")
        panels.rowconfigure(0, weight=1)

        source = ttk.Frame(panels, style="Panel.TFrame", padding=22)
        source.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
        source.columnconfigure(0, weight=1)
        source.rowconfigure(1, weight=1)
        self._build_source_panel(source)

        monitor = ttk.Frame(panels, style="Panel.TFrame", padding=22)
        monitor.grid(row=0, column=1, sticky="nsew")
        monitor.columnconfigure(0, weight=1)
        monitor.rowconfigure(1, weight=1)
        self._build_monitor_panel(monitor)

        safety = tk.Frame(shell, bg=BACKGROUND)
        safety.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        safety.columnconfigure(1, weight=1)
        tk.Label(safety, text="i", bg=BACKGROUND, fg=ORANGE, font=MONO, width=2, highlightthickness=1, highlightbackground=ORANGE).grid(row=0, column=0, padx=(0, 9))
        tk.Label(safety, text="SIMULATION ONLY. This app creates local UI events; it does not create CAN frames, open SocketCAN, or connect to a vehicle.", bg=BACKGROUND, fg="#a4aca3", font=("DejaVu Sans", 8), wraplength=900, justify="left").grid(row=0, column=1, sticky="ew")
        tk.Label(shell, text="CAN SPEED LAB / PROTOTYPE                                      NO HARDWARE CONNECTION", bg=BACKGROUND, fg=QUIET, font=("DejaVu Sans Mono", 8)).grid(row=4, column=0, sticky="ew", pady=(14, 0))

    def _build_source_panel(self, parent):
        heading = tk.Frame(parent, bg=PANEL)
        heading.grid(row=0, column=0, sticky="ew")
        heading.columnconfigure(0, weight=1)
        ttk.Label(heading, text="01 / SIGNAL SOURCE", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(heading, text="ECU-A", style="Muted.TLabel").grid(row=0, column=1, sticky="e")

        self.diagram = tk.Canvas(parent, height=180, bg=PANEL, highlightthickness=0)
        self.diagram.grid(row=1, column=0, sticky="nsew", pady=(10, 12))
        self.diagram.bind("<Configure>", self._draw_topology)

        speed_block = tk.Frame(parent, bg=PANEL, highlightthickness=1, highlightbackground=LINE, padx=14, pady=12)
        speed_block.grid(row=2, column=0, sticky="ew")
        speed_block.columnconfigure(0, weight=1)
        speed_block.columnconfigure(1, weight=0)
        tk.Label(speed_block, text="VEHICLE SPEED", bg=PANEL, fg=MUTED, font=("DejaVu Sans Mono", 8)).grid(row=0, column=0, sticky="w")
        self.speed_label = ttk.Label(speed_block, text="0", style="Speed.TLabel", width=4, anchor="e")
        self.speed_label.grid(row=1, column=0, sticky="w", pady=(3, 0))
        ttk.Label(speed_block, text="km/h", style="Unit.TLabel").grid(row=1, column=1, sticky="e", padx=(10, 0))
        self.slider = tk.Scale(speed_block, from_=0, to=240, resolution=1, orient="horizontal", showvalue=False, variable=self.speed, command=self._on_speed_change, bg=PANEL, fg=MUTED, troughcolor="#414741", activebackground=ACID, highlightthickness=0, bd=0, sliderlength=16, width=4)
        self.slider.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        scale = tk.Frame(speed_block, bg=PANEL)
        scale.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(3, 0))
        for index, value in enumerate(("0", "60", "120", "180", "240 km/h")):
            scale.columnconfigure(index, weight=1)
            tk.Label(scale, text=value, bg=PANEL, fg=QUIET, font=("DejaVu Sans Mono", 7), anchor="w" if index == 0 else "e").grid(row=0, column=index, sticky="ew")

        footer = tk.Frame(parent, bg=PANEL)
        footer.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        for column in range(3):
            footer.columnconfigure(column, weight=1)
        for column, (key, value) in enumerate((("SIGNAL", "VEH_SPEED"), ("INTERVAL", "500 ms"), ("UNIT", "km/h"))):
            cell = tk.Frame(footer, bg=PANEL)
            cell.grid(row=0, column=column, sticky="w", padx=(0, 8))
            tk.Label(cell, text=key, bg=PANEL, fg=QUIET, font=("DejaVu Sans Mono", 7)).pack(anchor="w")
            tk.Label(cell, text=value, bg=PANEL, fg="#c9d0c8", font=("DejaVu Sans Mono", 8)).pack(anchor="w", pady=(3, 0))
        self.stream_button = ttk.Button(footer, text="▶  START STREAM", style="Accent.TButton", command=self._toggle_stream)
        self.stream_button.grid(row=0, column=3, sticky="e", padx=(8, 0))

    def _build_monitor_panel(self, parent):
        heading = tk.Frame(parent, bg=PANEL)
        heading.grid(row=0, column=0, sticky="ew")
        heading.columnconfigure(0, weight=1)
        ttk.Label(heading, text="02 / MESSAGE MONITOR", style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.monitor_status = tk.Label(heading, text="●  PAUSED", bg=PANEL, fg=MUTED, font=("DejaVu Sans Mono", 8))
        self.monitor_status.grid(row=0, column=1, sticky="e")

        table_frame = ttk.Frame(parent, style="Panel.TFrame")
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(18, 8))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.log = ttk.Treeview(table_frame, columns=("time", "signal", "value"), show="headings", height=8, selectmode="browse")
        self.log.heading("time", text="TIME", anchor="w")
        self.log.heading("signal", text="SIGNAL", anchor="w")
        self.log.heading("value", text="VALUE", anchor="e")
        self.log.column("time", width=76, minwidth=64, stretch=False, anchor="w")
        self.log.column("signal", width=150, minwidth=100, stretch=True, anchor="w")
        self.log.column("value", width=86, minwidth=76, stretch=False, anchor="e")
        self.log.grid(row=0, column=0, sticky="nsew")

        self.count_label = tk.Label(parent, text="0 UPDATES", bg=PANEL, fg=QUIET, font=("DejaVu Sans Mono", 8))
        self.count_label.grid(row=2, column=0, sticky="e", pady=(6, 0))
        self.empty_label = tk.Label(table_frame, text="Waiting for stream\nStart ECU to emit updates", bg="#1c201d", fg=QUIET, font=("DejaVu Sans Mono", 9), justify="center")
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

    def _draw_topology(self, _event=None):
        canvas = self.diagram
        canvas.delete("all")
        width = max(canvas.winfo_width(), 420)
        center_y = 88
        ecu_x = 74
        display_x = width - 72
        bus_start = ecu_x + 60
        bus_end = display_x - 54
        self.bus_bounds = (bus_start, bus_end)

        canvas.create_text(12, 10, text="VISUAL ECU TOPOLOGY", fill=QUIET, font=("DejaVu Sans Mono", 7), anchor="nw")
        canvas.create_rectangle(ecu_x - 43, center_y - 32, ecu_x + 43, center_y + 27, fill="#292f2a", outline="#59605a", width=1)
        canvas.create_rectangle(ecu_x - 15, center_y - 15, ecu_x + 15, center_y + 15, fill=PANEL, outline="#677268", width=1)
        canvas.create_text(ecu_x, center_y, text="ECU", fill=ACID, font=("DejaVu Sans Mono", 8))
        canvas.create_text(ecu_x, center_y + 48, text="SPEED ECU", fill=TEXT, font=("DejaVu Sans", 8, "bold"))
        canvas.create_text(ecu_x, center_y + 63, text="STANDBY" if not self.streaming else "STREAMING", fill=ACID if self.streaming else MUTED, font=("DejaVu Sans Mono", 7))

        wire_color = ACID if self.streaming else LINE
        canvas.create_line(bus_start, center_y - 5, bus_end, center_y - 5, fill=wire_color, width=2)
        canvas.create_line(bus_start, center_y + 5, bus_end, center_y + 5, fill=wire_color, width=2)
        canvas.create_text((bus_start + bus_end) / 2, center_y - 20, text="SIMULATED BUS", fill=QUIET, font=("DejaVu Sans Mono", 7))
        canvas.create_arc(display_x - 40, center_y - 35, display_x + 40, center_y + 42, start=0, extent=180, style="arc", outline="#59605a", width=2)
        canvas.create_line(display_x - 36, center_y + 4, display_x + 36, center_y + 4, fill="#59605a")
        canvas.create_text(display_x, center_y - 1, text=str(self.speed.get()), fill=ACID, font=("DejaVu Sans Mono", 12))
        canvas.create_text(display_x, center_y + 16, text="km/h", fill=MUTED, font=("DejaVu Sans Mono", 7))
        canvas.create_text(display_x, center_y + 57, text="DISPLAY NODE", fill=TEXT, font=("DejaVu Sans", 8, "bold"))
        if self.streaming:
            self.packet_id = canvas.create_oval(bus_start, center_y - 8, bus_start + 7, center_y - 1, fill=ACID, outline="")
        else:
            self.packet_id = None

    def _on_speed_change(self, _value):
        self._update_speed()

    def _update_speed(self):
        speed = self.speed.get()
        self.speed_label.configure(text=str(speed))
        if hasattr(self, "diagram"):
            self._draw_topology()

    def _toggle_stream(self):
        if self.streaming:
            self._stop_stream()
        else:
            self._start_stream()

    def _start_stream(self):
        self.streaming = True
        self.stream_button.configure(text="■  STOP STREAM", style="Stop.TButton")
        self.monitor_status.configure(text="●  LIVE", fg=ACID)
        self.empty_label.place_forget()
        self._draw_topology()
        self._emit_message()
        self._animate_packet()

    def _stop_stream(self):
        self.streaming = False
        if self.stream_job is not None:
            self.after_cancel(self.stream_job)
            self.stream_job = None
        if self.animation_job is not None:
            self.after_cancel(self.animation_job)
            self.animation_job = None
        self.stream_button.configure(text="▶  START STREAM", style="Accent.TButton")
        self.monitor_status.configure(text="●  PAUSED", fg=MUTED)
        self._draw_topology()

    def _emit_message(self):
        if not self.streaming:
            return
        self.sequence += 1
        timestamp = time.strftime("%H:%M:%S")
        self.log.insert("", 0, values=(timestamp, f"VEH_SPEED  #{self.sequence:03d}", f"{self.speed.get()} km/h"))
        rows = self.log.get_children()
        for row in rows[6:]:
            self.log.delete(row)
        self.count_label.configure(text=f"{self.sequence} UPDATES")
        self.stream_job = self.after(500, self._emit_message)

    def _animate_packet(self):
        if not self.streaming or self.packet_id is None:
            return
        bus_start, bus_end = self.bus_bounds
        coordinates = self.diagram.coords(self.packet_id)
        if not coordinates:
            return
        x_position = coordinates[0] + self.packet_direction * 5
        if x_position >= bus_end - 7:
            self.packet_direction = -1
        elif x_position <= bus_start:
            self.packet_direction = 1
        self.diagram.coords(self.packet_id, x_position, 80, x_position + 7, 87)
        self.animation_job = self.after(35, self._animate_packet)


def main():
    app = SpeedLab()
    app.mainloop()


if __name__ == "__main__":
    main()