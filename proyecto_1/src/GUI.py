# Importing the tkinter module
import tkinter as tk
from tkinter import ttk
from Utils import *

from System import System


class Table:
    def __init__(self, master, headers, data, cols_width):
        self.master = master
        self.rows = len(data)
        self.cols = len(headers)
        self.data = data
        self.frames = []
        self.labels = []
        self.StringVars = []

        Canvas = tk.Canvas(
            master,
            background=BORDER,
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
                bg=BORDER,
            )
            frame.grid_propagate(False)  # Evita que el Frame cambie de tamaño
            frame.grid(row=0, column=col)

            label = tk.Label(
                frame,
                text=headers[col],
                bg=BORDER,
                fg=BACKGROUND,
                font=(FONT, 9, "bold"),
            ).place(relx=0.5, rely=0.5, anchor="center")

        # Crear las celdas
        for row in range(self.rows):
            for col in range(self.cols):
                frame = tk.Frame(
                    Canvas,
                    width=cols_width[col],
                    height=height,
                    bg=BACKGROUND,
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
                    bg=BACKGROUND,
                    fg=BORDER,
                    font=(FONT, 10),
                )
                label.place(relx=0.5, rely=0.5, anchor="center")

                self.frames.append(frame)
                self.labels.append(label)

    def get(self, address):
        # Get index de la fila
        # k ->  fila X, columna 0
        # i * num de cols = fila 0, 1, 2...
        k = next(
            (
                i * self.cols
                for i, d in enumerate(self.data)
                if print_address_bin(address) == d[0]
            ),
            0,
        )
        return k

    # Se asigna el color de una vez
    def read(self, address, delay):
        k = self.get(address=address)
        h = self.cols - 1
        while h != -1:
            self.update_bg_color(self.frames[k + h], HIGHLIGHT_READ)
            self.update_bg_color(self.labels[k + h], HIGHLIGHT_READ)
            # Tiempo en el que vuelve a la normalidad
            self.update_bg_color_after(self.frames[k + h], BACKGROUND, delay)
            self.update_bg_color_after(self.labels[k + h], BACKGROUND, delay)

            # Decrementar
            h -= 1

    def write(self, address, load, delay):
        k = self.get(address=address)
        # Set all cols
        # k -> address
        # k + 1 -> dato 1
        # k + 2 -> dato 2
        # k + 3 -> dato 3
        # h = self.cols - 1
        # while h != -1:
        #     self.frames[k + h].config(bg=HIGHLIGHT_WRITE)
        #     self.labels[k + h].config(bg=HIGHLIGHT_WRITE)

        #     # Tiempo en el que vuelve a la normalidad
        #     self.frames[k + h].after(5000, self._set_data, self.frames[k + h], load[h])
        #     self.labels[k + h].after(5000, self._set_data, self.frames[k + h], load[h])

        #     # Decrementar
        #     h -= 1

    def _set_data(self, widget, data):
        widget.config(text=data, bg=BACKGROUND)

    def update_bg_color(self, widget, color):
        widget.config(bg=color)

    def update_bg_color_after(self, widget, color, delay):
        widget.after(delay, self.update_bg_color, widget, color)


class FrameMemory(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        Canvas = tk.Canvas(
            self,
            background=BACKGROUND,
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        Canvas.pack()

        # Titulo
        tk.Label(
            Canvas,
            text="Memory",
            bg=BACKGROUND,
            fg=BORDER,
            font=(FONT, 11, "bold"),
        ).grid(row=0, column=0, padx=10, pady=(4, 0), sticky="w")

        # Inicial DATA
        headers = ["address", "data"]
        self.data = [
            ["000", "0000"],
            ["001", "0000"],
            ["010", "0000"],
            ["011", "0000"],
            ["100", "0000"],
            ["101", "0000"],
            ["110", "0000"],
            ["111", "0000"],
        ]
        cols_width = [80, 70]

        self.table = Table(
            master=Canvas, headers=headers, data=self.data, cols_width=cols_width
        )

    def read(self, address, delay):
        self.table.read(address=address, delay=delay)

    # def clear(self, k):
    # self.table.clear(k=k)


class FrameCache(ttk.Frame):
    def __init__(self, master, id):
        super().__init__(master)

        Canvas = tk.Canvas(
            self,
            background=BACKGROUND,
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        Canvas.pack()

        # Titulo
        tk.Label(
            Canvas,
            text=f"N{id}",
            bg=BACKGROUND,
            fg=BORDER,
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

    def read(self, address):
        self.table.read(address=address, delay=5000)

    # def write(self, address, color, time):
    #     self.table.set(address=address, color=color, time=time)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.main_canva = tk.Canvas(self, background="lightgray")
        self.main_canva.grid(row=0, column=0, sticky="nsew")
        self.main_canva.grid_propagate(True)

        # Memory
        self.memory_frame = FrameMemory(self.main_canva)
        self.memory_frame.place(x=500, y=300)

        # Cache
        self.cache_frames = []
        for i in range(NUM_CPU):
            frame = FrameCache(self.main_canva, i)
            frame.place(x=30 + (i * 320), y=30)
            self.cache_frames.append(frame)

        # Bus
        x1, y1, x2, y2 = 55, 250, 1250, 265
        self.main_canva.create_rectangle(x1, y1, x2, y2, fill=BORDER)
        self.main_canva.create_polygon(
            x1, y1 - 8, x1, y2 + 7, x1 - 15, y1 + 8, fill=BORDER
        )
        self.main_canva.create_polygon(
            x2, y1 - 8, x2, y2 + 7, x2 + 15, y1 + 8, fill=BORDER
        )

        # Set system
        self.sys = System(
            cache_frames=self.cache_frames, memory_frame=self.memory_frame
        )

    # Define a function to execute the code in a thread
    def start_system(self):
        # Execute in manual mode
        self.sys.execute_manual()
        # self.sys.execute_auto(2)