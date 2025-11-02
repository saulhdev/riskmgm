from tkinter import Menu
import webbrowser
from tkinter import messagebox

class MenuManager:
    """Gestor centralizado del menú de la aplicación"""
    
    def __init__(self, root, app_instance):
        self.root = root
        self.app = app_instance
        self.create_menu()
    
    def create_menu(self):
        """Crear la barra de menú completa"""
        menubar = Menu(self.root)
        
        # Menú Archivo
        archivo_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Abrir", command=self.app.load_project)
        archivo_menu.add_command(label="Guardar", command=self.app.save_project)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Cerrar", command=self.app.close_app)
        
        # Menú Procesar
        procesar_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Procesar", menu=procesar_menu)
        procesar_menu.add_command(label="Generar PDF", command=self.app.generate_pdf)
        
        # Menú Ayuda
        ayuda_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
        ayuda_menu.add_command(label="Código Fuente", command=self.codigo_fuente)
        ayuda_menu.add_command(label="Acerca de...", command=self.acerca_de)
        
        self.root.config(menu=menubar)
    
    def codigo_fuente(self):
        """Abrir repositorio de código fuente"""
        webbrowser.open("https://github.com/saulhdev/riskmgm")
    
    def acerca_de(self):
        """Mostrar información acerca de la aplicación"""
        messagebox.showinfo("Acerca de", "Risk Management\nVersión 1.0")

