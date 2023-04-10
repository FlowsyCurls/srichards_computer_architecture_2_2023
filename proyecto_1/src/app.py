# Importing the tkinter module
import queue
import threading
import time
import tkinter as tk
from tkinter import DISABLED, ttk
from src.bus import Bus
from src.utils import *
from src.cpu import CPU
from src.boards import Add_Inst_Section, CoreBoard, MemoryBoard


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # bind the <Escape> key event to the exit_app method
        self.bind("<Escape>", self._exit_app)

        # set window background color
        self.configure(bg=MENU)
        ############################################
        # Define Variables
        ############################################
        self.running = False
        self.cycles = tk.IntVar(value=1)
        self.is_limited_run = tk.BooleanVar(value=False)
        self.cores = []
        self.channel = queue.Queue()
        self.next_inst_stringvars = []  # Next instrucion text variable para cada nodo
        self.curr_inst_stringvars = []  # Curr instrucion text variable para cada nodo

        ############################################
        # Interface
        ############################################

        # Llamamos a los estilos
        self.styles()

        pos_x = 30
        pos_y = 30

        """  CONTEXT CANVA """
        # configure grid rows and columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create canvas widgets
        main_canva = tk.Canvas(self, background=WINDOW, highlightthickness=0)
        main_canva.grid(row=0, column=0, sticky="nsew")

        """  MENU ELEMENTS  """
        menu_canva = tk.Canvas(
            self, background=MENU, highlightbackground=EDGES, highlightthickness=1
        )
        menu_canva.place(x=pos_x + 705, y=pos_y + 573)
        self.start_button = ttk.Button(
            menu_canva,
            text="Start",
            command=self.start,
            style="Menu.TButton",
            takefocus=False,
        )
        self.step_button = ttk.Button(
            menu_canva,
            text="Step",
            state=DISABLED,
            command=self.step,
            style="Menu.TButton",
            takefocus=False,
        )
        self.run_button = ttk.Button(
            menu_canva,
            text="Run",
            state=DISABLED,
            command=self.run,
            style="Menu.TButton",
            takefocus=False,
        )
        self.stop_button = ttk.Button(
            menu_canva,
            text="Stop",
            state=DISABLED,
            command=self.stop,
            style="Menu.TButton",
            takefocus=False,
        )
        self.check_button = ttk.Checkbutton(
            menu_canva,
            text="limit cycles",
            style="Menu.TCheckbutton",
            variable=self.is_limited_run,
            state=DISABLED,
            command=self.set_cycles,
            onvalue=True,
            offvalue=False,
            takefocus=False,
        )
        self.spinbox_entry = ttk.Spinbox(
            menu_canva,
            from_=1.0,
            to=10.0,
            style="Menu.TSpinbox",
            textvariable=self.cycles,
            state=DISABLED,
            takefocus=False,
        )
        self.start_button.grid(column=0, row=0, rowspan=2, padx=(10, 0), pady=5)
        self.stop_button.grid(column=1, row=0, rowspan=2, padx=(0, 10), pady=5)
        self.step_button.grid(column=2, row=0, rowspan=2, padx=(10, 0), pady=5)
        self.run_button.grid(column=3, row=0, rowspan=2, padx=(0, 10), pady=5)
        self.check_button.grid(column=4, row=0, padx=13, pady=(5, 0))
        self.spinbox_entry.grid(column=4, row=1, padx=10, pady=(0, 5))

        """  SYSTEM ELEMENTS  """

        # CPU and Cache
        for i in range(NUM_CPU):
            core_board = CoreBoard(main_canva, i)
            core_board.place(x=pos_x + (i * 310), y=pos_y)
            self.next_inst_stringvars.append(core_board.next_instr_stringvar)
            self.curr_inst_stringvars.append(core_board.curr_instr_stringvar)
            self.cores.append(CPU(id=i, core_board=core_board, channel=self.channel))

        # Memory
        self.memory_board = MemoryBoard(main_canva)
        self.memory_board.place(x=pos_x + 400, y=pos_y + 305)

        # Bus
        self.bus = Bus(self.memory_board, self.channel, self.cores)
        x1, y1, x2, y2 = pos_x + 15, pos_y + 263, pos_x + 1220, pos_y + 278
        main_canva.create_rectangle(x1, y1, x2, y2, fill=BORDER)
        main_canva.create_polygon(x1, y1 - 8, x1, y2 + 7, x1 - 15, y1 + 8, fill=BORDER)
        main_canva.create_polygon(x2, y1 - 8, x2, y2 + 7, x2 + 15, y1 + 8, fill=BORDER)

        # Add instruction section
        self.add_inst_section = Add_Inst_Section(main_canva, self.cores)
        self.add_inst_section.place(x=pos_x + 705, y=340)

        # Colors menu
        guide = tk.Canvas(
            main_canva,
            background=GUIDE,
            highlightthickness=1,
            highlightbackground=EDGES,
        )
        guide.place(x=30, y=460)
        # Define a list of colors and their names
        colors = [
            (HIGHLIGHT_HIT, "hit"),
            (HIGHLIGHT_READ, "read"),
            (HIGHLIGHT_WRITE, "write"),
            (HIGHLIGHT_RQ, "sponsored"),
            (HIGHLIGHT_INV, "invalidated"),
            (HIGHLIGHT_WB, "write-back"),
        ]

        # Loop to create each row with a circle and a label
        for i, (color, name) in enumerate(colors):
            color_canvas = tk.Canvas(
                guide,
                width=20,
                height=20,
                background=color,
                highlightthickness=1,
                highlightbackground=EDGES,
            )

            color_canvas.grid(row=i, column=0, padx=5, pady=5)

            # Create a label with the color name in column 1
            label = tk.Label(guide, text=name, bg=GUIDE, font=(FONT, 10),)
            label.grid(row=i, column=1, padx=5, pady=5, sticky="w")

    # function to exit the application
    def _exit_app(self, event):
        self.destroy()

    #####################################################################
    #         PROCESS METHODS
    #####################################################################

    # Method that loads the next instruction for each core.
    def start(self):
        # Create and start threads for creating instructions on each CPU core
        cpu_threads = [
            threading.Thread(target=core.set_instruction, daemon=True)
            for core in (self.cores)
        ]
        for thread in cpu_threads:
            thread.start()
        # Enable the step, run, and check buttons
        self.add_inst_section.add["state"] = "normal"
        self.step_button["state"] = "normal"
        self.run_button["state"] = "normal"
        self.check_button["state"] = "normal"

    # Method to stop processing.
    def stop(self):
        self.running = False
        self.stop_button["state"] = "disabled"
        self.step_button["state"] = "normal"
        self.run_button["state"] = "normal"
        self.check_button["state"] = "normal"
        self.spinbox_entry["state"] = "normal"

    def step(self):
        # Create and start threads for processing instructions on each CPU core
        cpu_threads = [
            threading.Thread(target=core.execute, daemon=True) for core in (self.cores)
        ]
        for thread in cpu_threads:
            thread.start()

        # Create and start threads for generating new instructions on each CPU core
        instr_threads = [
            threading.Thread(target=core.set_instruction, daemon=True)
            for core in (self.cores)
        ]

        for thread in instr_threads:
            thread.start()

        # Start a new thread to check the system bus
        simulation_thread = threading.Thread(target=self.bus.process_tasks, daemon=True)
        simulation_thread.start()

        # Wait 500 ms before continuing
        self.after(500)

    # Method to start the simulation
    def run(self):
        # Disable run, step, and check buttons; enable stop button; disable spinbox entry
        self.run_button["state"] = "disabled"
        self.step_button["state"] = "disabled"
        self.stop_button["state"] = "normal"
        self.check_button["state"] = "disabled"
        self.spinbox_entry["state"] = "disabled"

        # Set running flag to True and start a new thread for the simulation
        self.running = True
        simulation_thread = threading.Thread(target=self._run_simulation, daemon=True)
        simulation_thread.start()

    def _run_simulation(self):
        # Keep running until stopped by user
        while self.running:
            # If it is a limited run and there are no more cycles, stop execution
            if self.is_limited_run.get():
                n = self.cycles.get() - 1
                self.cycles.set(n)

                if n == 0:
                    self.stop()
                    self.is_limited_run.set(False)
                    # Reset cycles to one.
                    self.cycles.set(1)

                    break

            # Execute one step and wait for X seconds
            self.step()

            time.sleep(CYCLES_DELAY)

    # Method to set the cycles based on the user's input
    def set_cycles(self):
        # If it is a limited run, enable the spinbox entry, otherwise disable it
        self.spinbox_entry["state"] = (
            "normal" if self.is_limited_run.get() else "disabled"
        )

    #####################################################################
    #         GUI METHODS
    #####################################################################

    def styles(self):
        # Creamos el estilo para el botón redondo
        style = ttk.Style()
        style.configure(
            "RoundedButton.TButton",
            padding=6,
            relief="flat",
            background=WINDOW,
            borderwidth=0,
        )
        style.map("RoundedButton.TButton", background=[("active", "#aaa")])

        # Creamos el estilo para el botón redondo
        style = ttk.Style()
        style.configure("Menu.TButton", background=MENU)
        style.map("Menu.TButton", background=[("active", "#aaa")])
        style.configure(
            "Menu.TCheckbutton", background=MENU, foreground=BORDER, font=(FONT, 10)
        )
        style.configure("Menu.TSpinbox", background=MENU)
        # Creamos el estilo para el boton redondo pero no clickeable
        style.configure(
            "Note.TLabel",
            background=ADDSECTION,
            foreground="black",
            font=(FONT, 10, "bold"),
            padding=4,
        )

        # Creamos un estilo para los botones de radio
        style.configure(
            "Custom.TRadiobutton",
            padding=10,
            background=ADDSECTION,
            font=(FONT, 10),
            foreground=NOTE,
        )
