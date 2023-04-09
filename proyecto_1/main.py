# Función principal
from src.app import App

if __name__ == "__main__":
    app = App()
    app.title("MOESI SIMULATOR")
    app.geometry("1300x680+40+40")
    # maximize the window
    # app.state('zoomed')
    app.mainloop()
