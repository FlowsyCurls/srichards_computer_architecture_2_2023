# Importing the tkinter module
import queue
import tkinter as tk
from tkinter import DISABLED, ttk
from Utils import *

from System import System


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



class FrameMemory(tk.Frame):
    def __init__(self, master):
        super().__init__(master, background=BACKGROUND, highlightthickness=1, highlightbackground=BORDER)
        self.frames = []
        self.labels = []
        
        # # Base
        # BaseFrame = tk.Frame(self, background=BACKGROUND, highlightthickness=1, highlightbackground=BORDER)
        # BaseFrame.pack()

        # Titulo
        title = tk.Label(self, text="Memory", bg=BACKGROUND, fg=BORDER, font=(FONT, 11, "bold"))
        title.grid(row=0, column=0, padx=10, pady=(4, 0), sticky="w")

        TableFrame = tk.Frame(self, background=BORDER)
        TableFrame.grid(row=1, column=0, padx=(10, 10), pady=(5, 10), columnspan=2)
        
        # Do table
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
    
        # Agregar headers
        for col in range(len(headers)):
          frame = tk.Frame(TableFrame, width=cols_width[col], height=height, bg=BORDER)
          frame.grid_propagate(False)  # Evita que el Frame cambie de tamaño
          frame.grid(row=0, column=col, sticky='nswe')
    
          label = tk.Label(frame, text=headers[col], bg=BORDER, fg=BACKGROUND, font=(FONT, 9, "bold"))
          label.place(relx=0.5, rely=0.5, anchor="center")
    
        # Crear las celdas
        for row in range(len(self.data)):
          for col in range(len(headers)):
            frame = tk.Frame(TableFrame, width=cols_width[col], height=height, bg=BACKGROUND)
            frame.grid_propagate(False)  # Evita que el Frame cambie de tamaño
            frame.grid(row=row + 1, column=col, pady=(0, padding))

            if col == (len(headers) - 1):
              frame.grid(row=row + 1, column=col, padx=(0, padding), pady=(0, padding))
            elif col == 0:
              frame.grid(row=row + 1, column=col, padx=(padding, 0), pady=(0, padding))

            label = tk.Label(frame, text=self.data[row][col], bg=BACKGROUND, fg=BORDER, font=(FONT, 10))
            label.place(relx=0.5, rely=0.5, anchor="center")

            self.frames.append(frame)
            self.labels.append(label)
           
           
    def get(self, address):
        # Get index de la fila
        # k ->  fila X, columna 0
        # i * num de cols = fila 0, 1, 2...
        k = 0
        for i in range(len(self.data)):
            if address == self.data[i][0]:
                k = i * len(self.data[i])
        return k
    
    # Se asigna el color de una vez
    def read(self, address, delay):
        k = self.get(address=address)
        h = 1
        while h!=-1:
          update_bg_color(self.frames[k+h], HIGHLIGHT_READ)
          update_bg_color(self.labels[k+h], HIGHLIGHT_READ)
          # Tiempo en el que vuelve a la normalidad
          update_bg_color_after(self.frames[k+h], BACKGROUND, delay)
          update_bg_color_after(self.labels[k+h], BACKGROUND, delay)
          h-=1


    def write(self, address, arr_data, delay, color=HIGHLIGHT_WRITE):
        k = self.get(address=address)
        h = len(self.data[0])-1
        while h!=-1:
          update_bg_color(widget=self.frames[k+h], color=color)
          update_bg_color(widget=self.labels[k+h], color=color)
          # Tiempo en el que vuelve a la normalidad
          update_bg_color_after(widget=self.frames[k+h], color=BACKGROUND, delay=delay)
          update_text_and_bg_color_after(widget=self.labels[k+h], text=arr_data[h], delay=delay)
          h-=1


class FrameCache(tk.Frame):
    def __init__(self, master, id):
        super().__init__(master, background=BACKGROUND, highlightthickness=1, highlightbackground=BORDER)
        self.frames = []
        self.labels = []

        # Titulo
        title = tk.Label(self, text=f"N{id}", bg=BACKGROUND, fg=BORDER, font=(FONT, 11, "bold"))
        title.grid(row=0, column=0, padx=10, pady=(4, 0), sticky="w")
        # Miss
        self.miss = tk.Label(self,text="miss", bg=BACKGROUND, fg="red", font=(FONT, 10, "bold"))
        self.miss.grid(row=0, column=1, padx=10, pady=(4, 0), sticky="e")
#############
        # Instructions Frame
        InstrFrame = tk.Frame(self, background=BACKGROUND)
        InstrFrame.grid(row=1, column=0, padx=10, pady=(4, 0), sticky="nswe")

        # Instruction Indicators Labels
        tk.Label(InstrFrame, text="next:", bg=BACKGROUND, fg=BORDER, font=(FONT, 8)).grid(row=0, column=0, padx=10, sticky="w")
        tk.Label(InstrFrame, text="curr:", bg=BACKGROUND, fg=BORDER, font=(FONT, 8)).grid(row=1, column=0, padx=10, sticky="w")
        
      # Creamos StringVar de cada instruccion y le asignamos un valor inicial
        self.next_instruction_StringVar = tk.StringVar(value="READ 000")
        self.curr_instruction_StringVar = tk.StringVar(value="WRITE 111; FFFF")

        # Next and Current Instruction
        next_instruction_label = tk.Label(InstrFrame, textvariable=self.next_instruction_StringVar, bg=BACKGROUND, fg=BORDER, font=(FONT, 8, "italic","bold"))
        curr_instruction_label = tk.Label(InstrFrame, textvariable=self.curr_instruction_StringVar, bg=BACKGROUND, fg='blue', font=(FONT, 8,"italic","bold"))
        next_instruction_label.grid(row=0, column=1, padx=2, sticky="w")
        curr_instruction_label.grid(row=1, column=1, padx=2, sticky="w")
#############
        TableFrame = tk.Frame(self, background=BORDER)
        TableFrame.grid(row=2, column=0, padx=(10, 10), pady=(5, 10), columnspan=2)
        
        # # Do table
        # Inicial DATA
        headers = ["", "state", "address", "set", "data"]
        self.data = [
            ["B0", "I", "000", "0", "0000"],
            ["B1", "I", "000", "0", "0000"],
            ["B2", "I", "000", "1", "0000"],
            ["B3", "I", "000", "1", "0000"],
        ]
        cols_width = [38, 35, 85, 25, 75]
    
        # Agregar headers
        for col in range(len(headers)):
          frame = tk.Frame(TableFrame, width=cols_width[col], height=height, bg=BORDER)
          frame.grid_propagate(False)  # Evita que el Frame cambie de tamaño
          frame.grid(row=0, column=col, sticky='nswe')
    
          label = tk.Label(frame, text=headers[col], bg=BORDER, fg=BACKGROUND, font=(FONT, 9, "bold"))
          label.place(relx=0.5, rely=0.5, anchor="center")
    
        # Crear las celdas
        for row in range(len(self.data)):
          for col in range(len(headers)):
            frame = tk.Frame(TableFrame, width=cols_width[col], height=height, bg=BACKGROUND)
            frame.grid_propagate(False)  # Evita que el Frame cambie de tamaño
            frame.grid(row=row + 1, column=col, pady=(0, padding))

            if col == (len(headers) - 1):
              frame.grid(row=row + 1, column=col, padx=(0, padding), pady=(0, padding))
            elif col == 0:
              frame.grid(row=row + 1, column=col, padx=(padding, 0), pady=(0, padding))

            label = tk.Label(frame, text=self.data[row][col], bg=BACKGROUND, fg=BORDER, font=(FONT, 10))
            label.place(relx=0.5, rely=0.5, anchor="center")

            self.frames.append(frame)
            self.labels.append(label)
            
    def set_next_instruction(self, instr):
      self.curr_instruction_StringVar.set(self.next_instruction_StringVar.get())
      self.next_instruction_StringVar.set(instr)
           
    # def get(self, address):
    #     # Get index de la fila
    #     # k ->  fila X, columna 0
    #     # i * num de cols = fila 0, 1, 2...
    #     k = 0
    #     for i in range(len(self.data)):
    #         if address == self.data[i][0]:
    #             k = i * len(self.data[i])
    #     return k
    
    # # Se asigna el color de una vez
    # def read(self, address):
    #     k = self.get(address=address)
    #     h = len(self.data)-1
    #     while h!=-1:
    #       update_bg_color(self.frames[k+h], HIGHLIGHT_READ)
    #       update_bg_color(self.labels[k+h], HIGHLIGHT_READ)
    #       # Tiempo en el que vuelve a la normalidad
    #       update_bg_color_after(self.frames[k+h], BACKGROUND, 1500)
    #       update_bg_color_after(self.labels[k+h], BACKGROUND, 1500)
    #       h-=1


    # def write(self, address, arr_data, color=HIGHLIGHT_WRITE):
    #     k = self.get(address=address)
    #     h = 1
    #     while h!=-1:
    #       update_bg_color(widget=self.frames[k+h], color=color)
    #       update_bg_color(widget=self.labels[k+h], color=color)
    #       # Tiempo en el que vuelve a la normalidad
    #       update_bg_color_after(widget=self.frames[k+h], color=BACKGROUND, delay=1500)
    #       update_text_and_bg_color_after(widget=self.labels[k+h], text=arr_data[h], delay=1500)
    #       h-=1


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # bind the <Escape> key event to the exit_app method
        self.bind("<Escape>", self.exit_app)
        
         # set window background color
        self.configure(bg=MENU)
############################################
# Define Variables
############################################
        self.running = False
        self.cycles = tk.IntVar(value=1)          # default is 1
        self.is_limited_run = tk.BooleanVar()     # default is False
        self.processors_list = []
        self.queue = queue.Queue()

        # Next instrucion string variable per core
        self.next_instruction_list = []
        # Current instrucion string variable per core
        self.curr_instruction_list = []
        # Bus message string variable per core
        self.bus_message_list = []
        
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
        menu_canva = tk.Canvas(self, background=MENU, highlightbackground=BORDER, highlightthickness=1)
        menu_canva.place(x=pos_x+705, y=pos_y+573)
        self.start_button = ttk.Button(menu_canva, text='Start', command=self.start, style="Menu.TButton", takefocus=False)
        self.step_button = ttk.Button(menu_canva, text='Step', state=DISABLED, command=self.step, style="Menu.TButton", takefocus=False)
        self.run_button = ttk.Button(menu_canva, text='Run', state=DISABLED, command=self.run, style="Menu.TButton", takefocus=False)
        self.stop_button = ttk.Button(menu_canva, text='Stop', state=DISABLED, command=self.stop, style="Menu.TButton",takefocus=False)
        self.check_button = ttk.Checkbutton(menu_canva, text=' limited cycles ', style="Menu.TCheckbutton", variable=self.is_limited_run, state=DISABLED, command=self.set_cycles, onvalue=True, offvalue=False, takefocus=False)
        self.spinbox_entry = ttk.Spinbox(menu_canva, from_=1.0, to=10.0, style="Menu.TSpinbox", textvariable=self.cycles, state=DISABLED, takefocus=False)
        self.start_button.grid(column=0, row=0, rowspan=2, padx=(10,0), pady=5)
        self.stop_button.grid(column=1, row=0, rowspan=2,  padx=(0,10), pady=5)
        self.step_button.grid(column=2, row=0, rowspan=2, padx=(10,0), pady=5)
        self.run_button.grid(column=3, row=0, rowspan=2, padx=(0,10), pady=5)
        self.check_button.grid(column=4, row=0, padx=13, pady=(5,0))
        self.spinbox_entry.grid(column=4, row=1, padx=10, pady=(0,5))
 
        """  SYSTEM ELEMENTS  """
        
        # Cache
        self.cache_frames = []
        for i in range(NUM_CPU):
            frame = FrameCache(main_canva, i)
            frame.place(x=pos_x + (i * 310), y=pos_y)
            self.cache_frames.append(frame)

        # Bus
        x1, y1, x2, y2 = pos_x+15, pos_y+263, pos_x+1220, pos_y+278
        main_canva.create_rectangle(x1, y1, x2, y2, fill=BORDER)
        main_canva.create_polygon(x1, y1 - 8, x1, y2 + 7, x1 - 15, y1 + 8, fill=BORDER)
        main_canva.create_polygon(x2, y1 - 8, x2, y2 + 7, x2 + 15, y1 + 8, fill=BORDER)
        
        # Memory
        self.memory_frame = FrameMemory(main_canva)
        self.memory_frame.place(x=pos_x+400, y=pos_y+305)
        self.memory_frame.read(address='000', delay=1400)
        self.memory_frame.write(address='111', arr_data=[None, 'FFFF'], delay=3000)

        pos_x = 750
        pos_y = pos_y + 310
        offset_inst = 280
        offset_addr = 145
        offset_data_x = 280
        offset_data_y = 130

        # Processors, Instructions, Address, Data
        self.selected_node = tk.StringVar(value="0")
        self.selected_inst = tk.StringVar(value="READ")
        self.selected_address = tk.StringVar(value="000")

        ttk.Label(main_canva, style="Note.TLabel", text="Select processor").place(x=pos_x, y=pos_y)
        ttk.Label(main_canva, style="Note.TLabel", text="Select instruction").place(x=pos_x+offset_inst, y=pos_y)
        ttk.Label(main_canva, style="Note.TLabel", text="Select address",).place(x=pos_x + offset_addr, y=pos_y)
        ttk.Label(main_canva, style="Note.TLabel", text="Enter data").place(x=pos_x + offset_data_x, y=pos_y + offset_data_y)

        # Options for the radio buttons
        options1 = ["N0", "N1", "N2", "N3"]
        options2 = ["READ", "WRITE", "CALC"]
        options3 = ["000", "001", "010", "011", "100", "101", "110", "111"]

        for i, option in enumerate(options1): # Processors
            radio = ttk.Radiobutton(main_canva, style="Custom.TRadiobutton",  takefocus=False, text=option, variable=self.selected_node, value=i)
            radio.place(x=pos_x, y=pos_y + 25 + (i * 26))
        for i, option in enumerate(options2): # Instructions
            radio = ttk.Radiobutton(main_canva, style="Custom.TRadiobutton",  takefocus=False, text=option, variable=self.selected_inst, value=option, command=self.write_label_disable)
            radio.place(x=pos_x+offset_inst, y=pos_y + 25 + (i * 26))
        for i, option in enumerate(options3): # Address
            radio = ttk.Radiobutton(main_canva, style="Custom.TRadiobutton",  takefocus=False, text=option, variable=self.selected_address, value=option)
            radio.place(x=pos_x + offset_addr, y= pos_y + 25 + (i * 26))

        # Entry para insertar el dato a escribir
        self.data_entry = tk.Entry(main_canva, font=(FONT, 10), state="disabled")
        self.data_entry.place(x=pos_x + offset_data_x, y=pos_y + offset_data_y + 30)

        # Button to add instruction.
        self.button = ttk.Button(main_canva, text="ADD", command=self.add_inst, style="RoundedButton.TButton", takefocus=False)
        self.button.place(x=pos_x + offset_data_x + 30, y=pos_y + offset_data_y + 60)
        



    def start(self):
      pass
    def step(self):
      pass
    def stop(self):
      pass
    def set_cycles(self):
      pass
    
    def run(self):
      pass 
        
        
    def styles(self):
        # Creamos el estilo para el botón redondo
        style = ttk.Style()
        style.configure("RoundedButton.TButton", padding=6, relief="flat", background=WINDOW, borderwidth=0)
        style.map("RoundedButton.TButton", background=[('active', '#aaa')])
        
        # Creamos el estilo para el botón redondo
        style = ttk.Style()
        style.configure("Menu.TButton", background=MENU)
        style.map("Menu.TButton", background=[('active', '#aaa')])
        style.configure('Menu.TCheckbutton', background=MENU, foreground="red",  font=(FONT, 10))
        style.configure('Menu.TSpinbox', background=MENU)
        # Creamos el estilo para el boton redondo pero no clickeable
        style.configure('Note.TLabel', background=WINDOW, foreground="black", font=(FONT, 10, "italic","bold"), padding=4)
        
        # Creamos un estilo para los botones de radio        
        style.configure("Custom.TRadiobutton", padding=10, background=WINDOW, font=(FONT, 10), foreground=NOTE)
      

    def write_label_disable(self):
      if self.selected_inst.get() == "WRITE":
          self.data_entry.config(state="normal")
      else:
          self.data_entry.config(state="disabled")
          # Clear entry
          self.data_entry.delete(0, tk.END)

    def add_inst(self):
        node = f'P{self.selected_node.get()}'
        inst = self.selected_inst.get()
        addr = self.selected_address.get()
        data = self.data_entry.get()
        
        # Clear entry
        self.data_entry.delete(0, tk.END)
        
        if inst == 'WRITE' and data == '':
          return

        conc = ''
        if inst == 'READ':
          conc = f'{node}: {inst} {addr}'
        elif inst == 'WRITE':
          conc = f'{node}: {inst} {addr};{data}'
        elif inst == 'CALC':
          conc = f'{node}: {inst}'
        
        print(conc)
        
    # function to exit the application
    def exit_app(self, event):
        self.destroy()

    # Define a function to execute the code in a thread
    def start_system(self):
        # Execute in manual mode
        self.sys.execute_manual()
        # self.sys.execute_auto(2)