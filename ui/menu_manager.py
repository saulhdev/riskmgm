from tkinter import Menu
import webbrowser
from tkinter import messagebox
import tkinter as tk
from .tab_manager import TabManager

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
        """Mostrar información acerca de la aplicación en un diálogo con el contenido del tab 'Acerca de'"""
        about_win = tk.Toplevel(self.root)
        about_win.title("Acerca de")
        about_win.transient(self.root)
        about_win.grab_set()
        about_win.geometry("640x480")

        # Renderizar el mismo contenido del tab "Acerca de" dentro del diálogo
        TabManager.render_about(about_win)

        # Centrar el diálogo respecto a la ventana principal
        about_win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - about_win.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - about_win.winfo_height()) // 2
        about_win.geometry(f"+{x}+{y}")

