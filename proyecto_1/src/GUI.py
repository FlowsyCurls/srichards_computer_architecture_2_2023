# Importing the tkinter module
import math
import tkinter as tk
from tkinter import CENTER, ttk

import tkinter.font as font

from PIL import Image, ImageTk
from Sistem import System

MEMORY_SIZE = 8
CACHE_SIZE = 4
NUM_CPU = 4
FONT = "Century Gothic"
BLACK = "black"
WHITE = "white"
YELLOW = "yellow"
padding = 1
height = 28
# print(font.families())


class Table:
    def __init__(self, master, headers, data, cols_width):
        self.master = master
        self.rows = len(data)
        self.cols = len(headers)
        self.labels = []
        self.StringVars = []

        Canvas = tk.Canvas(
            master,
            background=BLACK,
            highlightthickness=1,
            highlightbackground="black",
        )
        Canvas.grid(row=1, column=0, padx=(10, 10), pady=(5, 10))

        # Agregar headers
        for col in range(self.cols):
            frame = tk.Frame(
                Canvas,
                width=cols_width[col],
                height=height,
                bg=BLACK,
            )
            frame.grid_propagate(False)  # Evita que el Frame cambie de tamaño
            frame.grid(row=0, column=col)

            label = tk.Label(
                frame,
                text=headers[col],
                bg=BLACK,
                fg=WHITE,
                font=(FONT, 9, "bold"),
            ).place(relx=0.5, rely=0.5, anchor="center")

        # Crear las celdas
        for row in range(self.rows):
            for col in range(self.cols):
                frame = tk.Frame(
                    Canvas,
                    width=cols_width[col],
                    height=height,
                    bg=WHITE,
                )
                frame.grid_propagate(False)  # Evita que el Frame cambie de tamaño
                frame.grid(row=row + 1, column=col, pady=(0, padding))

                if col == (self.cols - 1):
                    frame.grid(
                        row=row + 1, column=col, padx=(0, padding), pady=(0, padding)
                    )
                elif col == 0:
                    frame.grid(
                        row=row + 1, column=col, padx=(padding, 0), pady=(0, padding)
                    )

                label = tk.Label(
                    frame,
                    text=data[row][col],
                    bg=WHITE,
                    fg=BLACK,
                    font=(FONT, 10),
                ).place(relx=0.5, rely=0.5, anchor="center")

                self.labels.append(label)

    def get(self, row, col):
        index = row * self.cols + col
        return self.entries[index].get()

    def set(self, row, col, value):
        index = row * self.cols + col
        print(index)
        self.entries[index].delete(0, tk.END)
        self.entries[index].insert(0, value)


class FrameMemory(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        Canvas = tk.Canvas(
            self,
            background=WHITE,
            highlightthickness=1,
            highlightbackground=BLACK,
        )
        Canvas.pack()

        # Titulo
        tk.Label(
            Canvas,
            text="Memory",
            bg=WHITE,
            fg=BLACK,
            font=(FONT, 11, "bold"),
        ).grid(row=0, column=0, padx=10, pady=(4, 0), sticky="w")

        # Inicial DATA
        headers = ["address", "data"]
        self.data = [
            ("000", "0000"),
            ("001", "0000"),
            ("002", "0000"),
            ("003", "0000"),
            ("004", "0000"),
            ("005", "0000"),
            ("006", "0000"),
            ("007", "0000"),
            ("008", "0000"),
        ]
        cols_width = [80, 70]

        self.table = Table(
            master=Canvas, headers=headers, data=self.data, cols_width=cols_width
        )


class FrameCache(ttk.Frame):
    def __init__(self, master, id):
        super().__init__(master)

        Canvas = tk.Canvas(
            self,
            background=WHITE,
            highlightthickness=1,
            highlightbackground=BLACK,
        )
        Canvas.pack()

        # Titulo
        tk.Label(
            Canvas,
            text=f"N{id}",
            bg=WHITE,
            fg=BLACK,
            font=(FONT, 10, "bold"),
        ).grid(row=0, column=0, padx=10, pady=(4, 0), sticky="w")

        # Inicial Cache Data
        headers = ["", "state", "address", "set", "data"]
        self.data = [
            ["B0", "I", "000", "0", "0000"],
            ["B1", "I", "000", "0", "0000"],
            ["B2", "I", "000", "1", "0000"],
            ["B3", "I", "000", "1", "0000"],
        ]
        cols_width = [38, 35, 85, 25, 75]

        self.table = Table(
            master=Canvas, headers=headers, data=self.data, cols_width=cols_width
        )


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.main_canva = tk.Canvas(self, background="lightgray")
        self.main_canva.grid(row=0, column=0, sticky="nsew")
        self.main_canva.grid_propagate(True)

        # Memory
        self.frame_memory = FrameMemory(self.main_canva)
        self.frame_memory.place(x=500, y=300)

        # Cache
        self.frames = []
        for i in range(4):
            frame = FrameCache(self.main_canva, i)
            frame.place(x=30 + (i * 320), y=30)
            self.frames.append(frame)

        # Bus
        x1, y1, x2, y2 = 55, 250, 1250, 265
        self.main_canva.create_rectangle(x1, y1, x2, y2, fill=BLACK)
        self.main_canva.create_polygon(
            x1, y1 - 8, x1, y2 + 7, x1 - 15, y1 + 8, fill=BLACK
        )
        self.main_canva.create_polygon(
            x2, y1 - 8, x2, y2 + 7, x2 + 15, y1 + 8, fill=BLACK
        )

        # self.frames[0].update(1, 0x1000, 1, 0x0F, 0xA5)
        # self.frames[1].update(2, 0x2000, 2, 0x55, 0x33)
        # self.frames[2].update(3, 0x3000, 3, 0xAA, 0xCC)
        # self.frames[3].update(4, 0x4000, 4, 0x11, 0x22)

# # CPU
# self.frames = []
# for i in range(4):
#     frame = FrameCache(self)
#     frame.pack(side=tk.LEFT, padx=10, pady=10)
#     self.frames.append(frame)

# self.frames[0].update(1, 0x1000, 1, 0x0F, 0xA5)
# self.frames[1].update(2, 0x2000, 2, 0x55, 0x33)
# self.frames[2].update(3, 0x3000, 3, 0xAA, 0xCC)
# self.frames[3].update(4, 0x4000, 4, 0x11, 0x22)

# Variable del sistema
# self.system = System(self.frames, self.memory_frame)

# Variables graficas
# text =
# {
#   :
# }

# # Execute in manual mode
# self.system.execute_manual()
# Execute in automatic mode with one cycle every 2 seconds
# system.execute_auto(2)
