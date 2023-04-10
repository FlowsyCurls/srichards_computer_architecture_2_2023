# Importing the tkinter module
import tkinter as tk
from tkinter import DISABLED, ttk
from src.utils import *
from src.myrandom import myrandom as rand


def update_text_and_bg_color(widget, text):
    widget.config(bg=BACKGROUND)
    if text is not None:
        widget.config(text=text)


def update_bg_color(widget, color):
    widget.config(bg=color)


def update_bg_color_after(widget, color, delay):
    widget.after(delay, update_bg_color, widget, color)


def update_text_and_bg_color_after(widget, text, delay):
    widget.after(delay, update_text_and_bg_color, widget, text)


import tkinter as tk


class Block:
    def __init__(self, id, state, address, set, data):
        self._id = id
        self._state = state
        self._address = address
        self._set = set
        self._data = data

    # def __str__(self):
    #     if "B" in self._id:
    # return f"Block  -  {self.get_id()}:   {self.get_state()}    {self.get_address()}    {self.get_set()}    {self.get_data()}"
    # return f"MemBlock  -  {self.get_address()}    {self.get_data()}"

    # Getter y setter para el atributo id
    def get_id(self):
        return self._id

    # Getter for set
    def get_set(self):
        return self._set.get()

    # Getter y setter para el atributo state
    def get_state(self):
        return self._state.get()

    def set_state(self, value):
        self._state.set(value)

    # Getter y setter para el atributo address
    def get_address(self):
        return self._address.get()

    def set_address(self, value):
        self._address.set(value)

    # Getter y setter para el atributo data
    def get_data(self):
        return self._data.get()

    def set_data(self, value):
        self._data.set(value)


class Board:
    def __init__(self, master, headers, data_blocks, cols_width):
        self.master = master
        self.rows = len(data_blocks)
        self.cols = len(headers)
        self.data_blocks = data_blocks
        self.changed = []

        # Agregar headers
        for col in range(len(headers)):
            frame = tk.Frame(master, width=cols_width[col], height=height, bg=BORDER)
            frame.grid_propagate(False)  # Prevents the Frame from resizing
            frame.grid(row=0, column=col, sticky="nswe")

            label = tk.Label(
                frame,
                text=headers[col],
                bg=BORDER,
                fg=BACKGROUND,
                font=(FONT, 9, "bold"),
            )
            label.place(relx=0.5, rely=0.5, anchor="center")

        # Crear las celdas
        self.blocks = {}
        self.frames = {}
        self.labels = {}
        for row in range(len(self.data_blocks)):
            arr_data = []
            arr_frames = []
            arr_labels = []
            block = None

            for col in range(len(headers)):
                frame = tk.Frame(
                    master, width=cols_width[col], height=height, bg=BACKGROUND
                )
                frame.grid_propagate(False)  # Prevents the Frame from resizing
                frame.grid(row=row + 1, column=col, pady=(0, padding))

                if col == (len(headers) - 1):
                    frame.grid(
                        row=row + 1, column=col, padx=(0, padding), pady=(0, padding)
                    )
                elif col == 0:
                    frame.grid(
                        row=row + 1, column=col, padx=(padding, 0), pady=(0, padding)
                    )

                # Create StringVar and set value.
                stringvar = tk.StringVar()
                stringvar.set(self.data_blocks[row][col])

                label = tk.Label(
                    frame,
                    textvariable=stringvar,
                    bg=BACKGROUND,
                    fg=BORDER,
                    font=(FONT, 10),
                )
                label.place(relx=0.5, rely=0.5, anchor="center")

                arr_frames.append(frame)
                arr_data.append(stringvar)
                arr_labels.append(label)

            # If its a memory board
            key = data_blocks[row][0]

            # If its a core board.
            if len(headers) > 2:
                # key, state, address set, data
                # ["B2", "I", "000", "1", "0000"],
                block = Block(key, arr_data[1], arr_data[2], arr_data[3], arr_data[4])
            else:
                # Set mem block key and address, key is address.
                # key, state, address set, data
                # Comes : ["111", "0000"]
                # ["111", None, "000", None, "0000"],
                block = Block(key, None, arr_data[0], None, arr_data[1])

            self.blocks[key] = block
            self.frames[key] = arr_frames
            self.labels[key] = arr_labels

    def get_block_by_id(self, id):
        return self.blocks[id]

    def get_block_by_address(self, address):
        for block in self.blocks.values():
            if address == block.get_address():
                return block
        return None

    def get_blocks_in_set(self, set):
        blocks = []
        for block in self.blocks.values():
            if set == int(block.get_set()):
                blocks.append(block)
        return blocks

    def set_state(self, address, value):
        self.blocks[address].set_state(value)

    def set_data(self, address, value):
        self.blocks[address].set_data(value)

    def set_address(self, address, value):
        self.blocks[address].set_address(value)

    def set(self, id, state, address, data):
        block = self.get_block_by_id(id)
        block.set_state(state)
        block.set_data(data)
        block.set_address(address)

    def animation(self, id, color):
        if id not in self.labels.keys():
            print("NO key matches  -  ", id)
            return

        row_labels = self.labels[id]
        row_frames = self.frames[id]
        for i in range(len(row_labels)):
            row_labels[i].config(bg=color)
            row_frames[i].config(bg=color)
            self.changed.append(row_labels[i])
            self.changed.append(row_frames[i])

    def clear_animation(self):
        if self.changed:
            for e in self.changed:
                e.config(bg=BACKGROUND)
        self.change = []


class MemoryBoard(tk.Frame):
    def __init__(self, master):
        super().__init__(
            master,
            background=BACKGROUND,
            highlightthickness=1,
            highlightbackground=BORDER,
        )

        # Titulo
        title = tk.Label(
            self, text="Memory", bg=BACKGROUND, fg=BORDER, font=(FONT, 11, "bold")
        )
        title.grid(row=0, column=0, padx=10, pady=(4, 0), sticky="w")

        # Board Frame
        BoardFrame = tk.Frame(self, background=BORDER)
        BoardFrame.grid(row=1, column=0, padx=(10, 10), pady=(5, 10))

        # Do table
        data = [
            ["000", "0000"],
            ["001", "0000"],
            ["010", "0000"],
            ["011", "0000"],
            ["100", "0000"],
            ["101", "0000"],
            ["110", "0000"],
            ["111", "0000"],
        ]

        # Set Board
        self.board = Board(BoardFrame, ["address", "data"], data, [80, 70])

    def clear_animation(self):
        self.board.clear_animation()

    def get_data(self, address):
        return self.board.get_block_by_id(address).get_data()

    def set_data(self, address, value):
        block = self.board.get_block_by_id(address)
        block.set_data(value)

    def animation(self, id, color):
        self.board.animation(id, color)


class CoreBoard(tk.Frame):
    def __init__(self, master, id):
        super().__init__(
            master,
            background=BACKGROUND,
            highlightthickness=1,
            highlightbackground=BORDER,
            # width=283,
            # height=240,
        )

        # self.grid_propagate(False)

        # Titulo
        title = tk.Label(
            self, text=f"N{id}", bg=BACKGROUND, fg=BORDER, font=(FONT, 11, "bold")
        )
        title.grid(row=0, column=0, padx=10, pady=(4, 0), sticky="w")
        # Miss
        self.miss = tk.Label(
            self, text="", bg=BACKGROUND, fg="red", font=(FONT, 10, "bold")
        )
        self.miss.grid(row=0, column=1, columnspan=3, padx=10, pady=(4, 0), sticky="ne")

        #############

        # Instructions Frame
        InstrFrame = tk.Frame(self, background=BACKGROUND)
        InstrFrame.grid(
            row=1, column=0, padx=10, pady=(4, 0), sticky="nswe", columnspan=4
        )
        # Board Frame
        BoardFrame = tk.Frame(self, background=BORDER)
        BoardFrame.grid(row=2, column=0, padx=(10, 10), pady=(5, 10), columnspan=4)

        #############

        # Instruction Indicators Labels
        tk.Label(
            InstrFrame, text="next:", bg=BACKGROUND, fg="darkgray", font=(FONT, 8)
        ).grid(row=0, column=0, padx=10, sticky="w")
        tk.Label(
            InstrFrame, text="curr:", bg=BACKGROUND, fg="black", font=(FONT, 8)
        ).grid(row=1, column=0, padx=10, sticky="w")

        # Creamos StringVar de cada instruccion y le asignamos un valor inicial
        self.next_instr_stringvar = tk.StringVar(value="")
        self.curr_instr_stringvar = tk.StringVar(value="")

        # Next and Current Instruction
        next_instruction_label = tk.Label(
            InstrFrame,
            textvariable=self.next_instr_stringvar,
            bg=BACKGROUND,
            fg="darkgray",
            font=(FONT, 10),
        )
        curr_instruction_label = tk.Label(
            InstrFrame,
            textvariable=self.curr_instr_stringvar,
            bg=BACKGROUND,
            fg="black",
            font=(FONT, 10, "bold"),
        )
        next_instruction_label.grid(row=0, column=1, columnspan=3, padx=2, sticky="w")
        curr_instruction_label.grid(row=1, column=1, columnspan=3, padx=2, sticky="w")

        #############

        # Do table
        data = [
            ["B0", "I", "000", "0", "0000"],
            ["B1", "I", "000", "0", "0000"],
            ["B2", "I", "000", "1", "0000"],
            ["B3", "I", "000", "1", "0000"],
        ]

        # Set Board
        self.board = Board(
            BoardFrame,
            ["", "state", "address", "set", "data"],
            data,
            [38, 35, 85, 25, 75],
        )

    def animation_access(self, access):
        color = "red" if "miss" in access else ("green" if "hit" in access else "blue")
        self.miss.config(text=access, fg=color)

    def get_cache(self):
        return self.board

    def clear_animation(self):
        self.board.clear_animation()


class Add_Inst_Section(tk.Frame):
    def __init__(self, master, cores):
        super().__init__(
            master,
            background="gainsboro",
            highlightthickness=1,
            highlightbackground=EDGES,
            width=501,
            height=240,
        )
        self.grid_propagate(False)
        self.cores = cores

        # Processors, Instructions, Address, Data
        self.selected_core = tk.StringVar(value="0")
        self.selected_inst = tk.StringVar(value="READ")
        self.selected_address = tk.StringVar(value="000")

        FrameProcessor = tk.Frame(self, background=ADDSECTION)
        FrameAddress = tk.Frame(self, background=ADDSECTION)
        FrameInstruction = tk.Frame(self, background=ADDSECTION)
        FrameData = tk.Frame(self, background=ADDSECTION)
        FrameProcessor.grid(row=0, column=0, sticky="nsew")
        FrameInstruction.grid(row=1, column=0, pady=(1, 0), sticky="nsew")
        FrameAddress.grid(row=2, column=0, pady=(1, 0), sticky="nsew")
        FrameData.grid(row=3, column=0, pady=(1, 0), sticky="nsew")

        label1 = ttk.Label(
            FrameProcessor, style="Note.TLabel", text="Select node         "
        )
        label2 = ttk.Label(
            FrameInstruction, style="Note.TLabel", text="Select operation "
        )

        label3 = ttk.Label(FrameAddress, style="Note.TLabel", text="Select address    ")
        label4 = ttk.Label(FrameData, style="Note.TLabel", text="Enter data        ")
        padx = 20
        label1.grid(row=0, column=0, sticky="w", padx=padx)
        label2.grid(row=0, column=0, sticky="w", padx=padx + 1)
        label3.grid(row=0, column=0, sticky="w", rowspan=2, padx=padx)
        label4.grid(row=0, column=0, sticky="w", padx=padx, pady=5)
        padx = 12

        # Options for the radio buttons
        options1 = ["N0", "N1", "N2", "N3"]
        options2 = ["READ", "WRITE", "CALC"]
        options3 = ["000", "001", "010", "011", "100", "101", "110", "111"]

        for i, option in enumerate(options1):  # Processors
            radio = ttk.Radiobutton(
                FrameProcessor,
                style="Custom.TRadiobutton",
                takefocus=False,
                text=option,
                variable=self.selected_core,
                value=i,
            )
            radio.grid(row=0, column=i + 1, padx=padx)

        for i, option in enumerate(options2):  #  Instructions
            radio = ttk.Radiobutton(
                FrameInstruction,
                style="Custom.TRadiobutton",
                takefocus=False,
                text=option,
                variable=self.selected_inst,
                value=option,
                command=self.enable_disable_data_entry,
            )
            radio.grid(row=0, column=i + 1, padx=padx)

        for i, option in enumerate(options3):  # Addresses
            radio = ttk.Radiobutton(
                FrameAddress,
                style="Custom.TRadiobutton",
                takefocus=False,
                text=option,
                variable=self.selected_address,
                value=option,
            )
            if i <= 3:
                radio.grid(row=0, column=i + 1, padx=padx)
            else:
                radio.grid(row=1, column=(i + 1) - 4, padx=padx)

        # Entry para insertar el dato a escribir
        self.data_entry = tk.Entry(FrameData, font=(FONT, 10), state="disabled")
        self.data_entry.grid(row=1, column=0, padx=padx)
        self.data_entry.config(
            validate="key",
            validatecommand=(self.data_entry.register(self.limit_data_entry), "%P"),
        )

        # Button to add instruction.
        self.add = ttk.Button(
            FrameData,
            text="ADD",
            command=self.add_inst,
            style="RoundedButton.TButton",
            takefocus=False,
            state=DISABLED,
        )
        self.add.grid(row=1, column=1, pady=(0, 6))
        
        # Button to add instruction.
        self.calc = ttk.Button(
            FrameData,
            text="STALL",
            command=self.stall,
            style="RoundedButton.TButton",
            takefocus=False,
            state=DISABLED,
        )
        self.calc.grid(row=1, column=2, padx=(145,0),pady=(0, 6))

    def stall(self):
        for core in self.cores:
            inst_str = f"P{self.selected_core.get()}: CALC"
            core.get_core_board().next_instr_stringvar.set(inst_str)

        
    def add_inst(self):
        core = f"P{self.selected_core.get()}"
        inst = self.selected_inst.get()
        addr = self.selected_address.get()
        data = self.data_entry.get().upper()

        # Clear entry
        self.data_entry.delete(0, tk.END)

        if inst == "WRITE" and data == "":
            return

        # Add zeros in case its necessary
        data = "{:0>4}".format(data)

        conc = ""
        if inst == "READ":
            conc = f"{core}: {inst} {addr}"
        elif inst == "WRITE":
            conc = f"{core}: {inst} {addr};{data}"
        elif inst == "CALC":
            conc = f"{core}: {inst}"

        self.cores[int(core[1])].get_core_board().next_instr_stringvar.set(conc)

    def limit_data_entry(self, new_text):
        valid_chars = "0123456789abcdef"
        if len(new_text) > 4:
            return False
        for char in new_text:
            if char.lower() not in valid_chars:
                return False
        return True

    def enable_disable_data_entry(self):
        if self.selected_inst.get() == "WRITE":
            self.data_entry["state"] = "normal"
        else:
            self.data_entry["state"] = "disabled"
            # Clear entry
            self.data_entry.delete(0, tk.END)
