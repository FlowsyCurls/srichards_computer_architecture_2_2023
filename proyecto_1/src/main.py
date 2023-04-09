# Función principal
from app import App

if __name__ == "__main__":
    app = App()
    app.title("MOESI SIMULATOR")
    app.geometry("1300x680+40+40")
    # Configurar la opción fill
    # app.grid_rowconfigure(0, weight=1)
    # app.grid_columnconfigure(0, weight=1)

    # Create a new thread and start it
    # thread = threading.Thread(target=lambda: app.start_system())
    # thread.start()
    # maximize the window
    # app.state('zoomed')
    app.mainloop()
