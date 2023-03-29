# Función principal
from GUI import App


if __name__ == "__main__":
    app = App()
    app.title("MOESI SIMULATOR")
    app.geometry("1400x700+1+40")
    # Configurar la opción fill
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)
    app.mainloop()
