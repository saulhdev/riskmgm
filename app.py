import tkinter as tk
from tkinter import Menu, ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import io
from PIL import Image as PILImage, ImageTk
import os
import base64
import webbrowser

import ttkbootstrap
from core.menu_manager import MenuManager

class RiskAnalysisISO13849:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Riesgo ISO 13849-1")
        self.root.geometry("1200x800")
        
        # Crear menú
        MenuManager(root, self)
        
        self.machine_data = {}
        self.risks = []
        self.machine_photos = []
        self.hrn_calculations = []
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_machine_tab()
        self.create_risk_tab()        
        self.create_hrn_tab()
        self.create_analysis_tab()
        self.create_report_tab()
        self.create_about_tab()

    def close_app(self):
        """Cerrar la aplicación"""
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            self.root.destroy()            

    def create_machine_tab(self):
        """Pestaña de datos de la máquina"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Datos de la Máquina")
        
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create left frame for data fields
        left_frame = ttk.Frame(scrollable_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        fields = [
            ("Tipo de Máquina:", "machine_type"),
            ("Modelo:", "model"),
            ("Fabricante:", "manufacturer"),
            ("Número de Serie:", "serial_number"),
            ("Año de Fabricación:", "year"),
            ("Ubicación:", "location"),
            ("Responsable del Análisis:", "analyst"),
        ]
        
        self.machine_entries = {}
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(left_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky='w', padx=20, pady=10
            )
            entry = ttk.Entry(left_frame, width=50)
            entry.grid(row=i, column=1, padx=20, pady=10)
            self.machine_entries[key] = entry
        
        ttk.Label(left_frame, text="Descripción:", font=('Arial', 10, 'bold')).grid(
            row=len(fields), column=0, sticky='nw', padx=20, pady=10
        )
        self.description_text = tk.Text(left_frame, width=50, height=5)
        self.description_text.grid(row=len(fields), column=1, padx=20, pady=10)
        
        ttk.Button(left_frame, text="Guardar Datos", command=self.save_machine_data).grid(
            row=len(fields)+1, column=1, pady=20
        )
        
        # Create right frame for photos
        right_frame = ttk.Frame(scrollable_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        photo_frame = ttk.Frame(right_frame)
        photo_frame.pack(pady=10)
        
        ttk.Button(photo_frame, text="📷 Añadir Foto", command=self.add_photo).pack(side='left', padx=5)
        ttk.Button(photo_frame, text="🗑️ Eliminar Foto", style='danger', command=self.remove_photo).pack(side='left', padx=5)
                
        self.photos_display_frame = ttk.LabelFrame(right_frame, text="Fotos de la Máquina", padding=10)
        self.photos_display_frame.pack(fill='both', expand=True, pady=10)
        
        self.photos_canvas = tk.Canvas(self.photos_display_frame, height=150, bg='white')
        self.photos_scrollbar = ttk.Scrollbar(self.photos_display_frame, orient="horizontal", command=self.photos_canvas.xview)
        self.photos_inner_frame = ttk.Frame(self.photos_canvas)
        
        self.photos_canvas.create_window((0, 0), window=self.photos_inner_frame, anchor="nw")
        self.photos_canvas.configure(xscrollcommand=self.photos_scrollbar.set)
        
        self.photos_canvas.pack(fill='x', expand=True)
        self.photos_scrollbar.pack(fill='x')
        
        self.photo_labels = []
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_risk_tab(self):
        """Pestaña de gestión de riesgos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Evaluación de Riesgos")
        
        # Frame izquierdo - Formulario
        left_frame = ttk.LabelFrame(frame, text="Añadir Nuevo Riesgo", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Campos del riesgo
        ttk.Label(left_frame, text="Descripción del Peligro:").grid(row=0, column=0, sticky='w', pady=5)
        self.risk_desc = ttk.Entry(left_frame, width=40)
        self.risk_desc.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(left_frame, text="Descripción del Riesgo:").grid(row=1, column=0, sticky='w', pady=5)
        self.risk_zone = ttk.Entry(left_frame, width=40)
        self.risk_zone.grid(row=1, column=1, pady=5, padx=5)
        
        # Severidad (S)
        ttk.Label(left_frame, text="Severidad (S):").grid(row=2, column=0, sticky='w', pady=5)
        self.severity = ttk.Combobox(left_frame, width=37, state='readonly')
        self.severity['values'] = ('S1 - Lesión leve', 'S2 - Lesión grave/permanente o muerte')
        self.severity.grid(row=2, column=1, pady=5, padx=5)
        
        # Frecuencia de exposición (F)
        ttk.Label(left_frame, text="Frecuencia (F):").grid(row=3, column=0, sticky='w', pady=5)
        self.frequency = ttk.Combobox(left_frame, width=37, state='readonly')
        self.frequency['values'] = (
            'F1 - Rara vez a frecuente',
            'F2 - Frecuente a continua'
        )
        self.frequency.grid(row=3, column=1, pady=5, padx=5)
        
        # Posibilidad de evitar (P)
        ttk.Label(left_frame, text="Posibilidad de Evitar (P):").grid(row=4, column=0, sticky='w', pady=5)
        self.avoidance = ttk.Combobox(left_frame, width=37, state='readonly')
        self.avoidance['values'] = (
            'P1 - Posible bajo condiciones específicas',
            'P2 - Apenas posible'
        )
        self.avoidance.grid(row=4, column=1, pady=5, padx=5)
        
        # Performance Level requerido (PLr)
        ttk.Label(left_frame, text="Performance Level (PLr):").grid(row=5, column=0, sticky='w', pady=5)
        self.plr_label = ttk.Label(left_frame, text="Seleccione S, F y P", foreground='blue')
        self.plr_label.grid(row=5, column=1, sticky='w', pady=5, padx=5)
        
        self.severity.bind('<<ComboboxSelected>>', self.calculate_plr)
        self.frequency.bind('<<ComboboxSelected>>', self.calculate_plr)
        self.avoidance.bind('<<ComboboxSelected>>', self.calculate_plr)
        
        ttk.Label(left_frame, text="Medidas de Control:").grid(row=6, column=0, sticky='nw', pady=5)
        self.control_measures = tk.Text(left_frame, width=40, height=4)
        self.control_measures.grid(row=6, column=1, pady=5, padx=5)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Añadir Riesgo", command=self.add_risk).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.clear_risk_form).pack(side='left', padx=5)
        
        right_frame = ttk.LabelFrame(frame, text="Riesgos Identificados", padding=10)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        columns = ('Descripción', 'Zona', 'S', 'F', 'P', 'PLr')
        self.risk_tree = ttk.Treeview(right_frame, columns=columns, show='tree headings', height=20)
        
        self.risk_tree.heading('#0', text='#')
        self.risk_tree.column('#0', width=30)
        
        for col in columns:
            self.risk_tree.heading(col, text=col)
            if col == 'Descripción':
                self.risk_tree.column(col, width=200)
            elif col == 'Zona':
                self.risk_tree.column(col, width=120)
            else:
                self.risk_tree.column(col, width=50)
        
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.risk_tree.yview)
        self.risk_tree.configure(yscrollcommand=scrollbar.set)
        
        self.risk_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        ttk.Button(right_frame, text="Eliminar Seleccionado", 
                   command=self.delete_risk).pack(pady=5)
    
    def create_hrn_tab(self):
        """Pestaña de calculadora HRN"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Calculadora HRN")
        
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        left_frame = ttk.LabelFrame(main_frame, text="Calcular HRN (Hazard Rating Number)", padding=15)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        ttk.Label(left_frame, text="HRN = LO × FE × DPH × NP", 
                 font=('Arial', 14, 'bold'), foreground='#003366').grid(
                     row=0, column=0, columnspan=2, pady=15)
        
        ttk.Label(left_frame, text="Descripción del Peligro:").grid(
            row=1, column=0, sticky='w', pady=10, padx=5)
        self.hrn_description = ttk.Entry(left_frame, width=50)
        self.hrn_description.grid(row=1, column=1, pady=10, padx=5)
        
        ttk.Label(left_frame, text="LO - Probabilidad de Ocurrencia:", 
                 font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=10, padx=5)
        
        self.lo_values = [
            (0.033, "Casi Imposible"),
            (1, "Altamente improbable"),
            (1.5, "Improbable"),
            (2, "Posible"),
            (5, "Hay Posibilidades"),
            (8, "Probable"),
            (10, "Muy Probable"),
            (15, "Cierto")
        ]
        
        self.lo_var = tk.StringVar()
        lo_combo = ttk.Combobox(left_frame, textvariable=self.lo_var, width=47, state='readonly')
        lo_combo['values'] = [f"{val} - {desc}" for val, desc in self.lo_values]
        lo_combo.grid(row=2, column=1, pady=10, padx=5)
        lo_combo.bind('<<ComboboxSelected>>', self.calculate_hrn)
        
        ttk.Label(left_frame, text="FE - Frecuencia de Exposición:", 
                 font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=10, padx=5)
        
        self.fe_values = [
            (0.5, "Anualmente"),
            (1, "Mensualmente"),
            (1.5, "Semanalmente"),
            (2.5, "Diariamente"),
            (4, "Cada Hora"),
            (5, "Constantemente")
        ]
        
        self.fe_var = tk.StringVar()
        fe_combo = ttk.Combobox(left_frame, textvariable=self.fe_var, width=47, state='readonly')
        fe_combo['values'] = [f"{val} - {desc}" for val, desc in self.fe_values]
        fe_combo.grid(row=3, column=1, pady=10, padx=5)
        fe_combo.bind('<<ComboboxSelected>>', self.calculate_hrn)
        
        ttk.Label(left_frame, text="DPH - Grado de Posible Daño:", 
                 font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=10, padx=5)
        
        self.dph_values = [
            (0.1, "Rasguño/Moretón"),
            (0.5, "Quemadura/Enfermedad de corto plazo"),
            (1, "Rotura - Hueso menor o Enfermedad menor (temporal)"),
            (2, "Rotura - Hueso mayor o Enfermedad menor (permanente)"),
            (4, "Pérdida de 1 miembro o Enfermedad grave (permanente)"),
            (8, "Pérdida de 2 miembros o Enfermedad grave (permanente)"),
            (15, "Fatalidad")
        ]
        
        self.dph_var = tk.StringVar()
        dph_combo = ttk.Combobox(left_frame, textvariable=self.dph_var, width=47, state='readonly')
        dph_combo['values'] = [f"{val} - {desc}" for val, desc in self.dph_values]
        dph_combo.grid(row=4, column=1, pady=10, padx=5)
        dph_combo.bind('<<ComboboxSelected>>', self.calculate_hrn)
        
        ttk.Label(left_frame, text="NP - Número de Personas en Riesgo:", 
                 font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=10, padx=5)
        
        self.np_values = [
            (1, "1-2 personas"),
            (2, "3-7 personas"),
            (4, "8-15 personas"),
            (8, "16-50 personas"),
            (12, "Más de 50 personas")
        ]
        
        self.np_var = tk.StringVar()
        np_combo = ttk.Combobox(left_frame, textvariable=self.np_var, width=47, state='readonly')
        np_combo['values'] = [f"{val} - {desc}" for val, desc in self.np_values]
        np_combo.grid(row=5, column=1, pady=10, padx=5)
        np_combo.bind('<<ComboboxSelected>>', self.calculate_hrn)
        
        result_frame = ttk.Frame(left_frame, relief='solid', borderwidth=2)
        result_frame.grid(row=6, column=0, columnspan=2, pady=20, padx=5, sticky='ew')
        
        ttk.Label(result_frame, text="Resultado:", font=('Arial', 12, 'bold')).pack(pady=5)
        
        self.hrn_result_label = ttk.Label(result_frame, text="HRN = ?", 
                                         font=('Arial', 18, 'bold'), foreground='blue')
        self.hrn_result_label.pack(pady=5)
        
        self.hrn_level_label = ttk.Label(result_frame, text="Seleccione todos los valores", 
                                        font=('Arial', 11), foreground='gray')
        self.hrn_level_label.pack(pady=5)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="💾 Guardar Cálculo", 
                  command=self.save_hrn_calculation).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Limpiar", 
                  command=self.clear_hrn_form).pack(side='left', padx=5)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        history_frame = ttk.LabelFrame(right_frame, text="Historial de Cálculos", padding=10)
        history_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Descripción', 'HRN', 'Nivel')
        self.hrn_tree = ttk.Treeview(history_frame, columns=columns, show='tree headings', height=10)
        
        self.hrn_tree.heading('#0', text='#')
        self.hrn_tree.column('#0', width=30)
        self.hrn_tree.heading('Descripción', text='Descripción')
        self.hrn_tree.column('Descripción', width=250)
        self.hrn_tree.heading('HRN', text='HRN')
        self.hrn_tree.column('HRN', width=80)
        self.hrn_tree.heading('Nivel', text='Nivel de Riesgo')
        self.hrn_tree.column('Nivel', width=150)
        
        hrn_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.hrn_tree.yview)
        self.hrn_tree.configure(yscrollcommand=hrn_scrollbar.set)
        
        self.hrn_tree.pack(side='left', fill='both', expand=True)
        hrn_scrollbar.pack(side='right', fill='y')
        
        ttk.Button(history_frame, text="🗑️ Eliminar Seleccionado", 
                  command=self.delete_hrn_calculation).pack(pady=5)
        
        reference_frame = ttk.LabelFrame(right_frame, text="Tabla de Niveles de Riesgo", padding=10)
        reference_frame.pack(fill='x')
        
        reference_text = """
0-1     → Riesgo Despreciable
2-5     → Riesgo Muy Bajo
6-10    → Riesgo Bajo
11-50   → Riesgo Significante
51-100  → Riesgo Alto
101-500 → Riesgo Muy Alto
501-1000 → Riesgo Extremo
>1000   → Riesgo Inaceptable
        """
        
        ref_label = ttk.Label(reference_frame, text=reference_text, 
                             font=('Courier', 9), justify='left')
        ref_label.pack()
    
    def calculate_hrn(self, event=None):
        """Calcular HRN"""
        try:
            lo_text = self.lo_var.get()
            fe_text = self.fe_var.get()
            dph_text = self.dph_var.get()
            np_text = self.np_var.get()
            
            if not all([lo_text, fe_text, dph_text, np_text]):
                return
            
            lo = float(lo_text.split(' - ')[0])
            fe = float(fe_text.split(' - ')[0])
            dph = float(dph_text.split(' - ')[0])
            np = float(np_text.split(' - ')[0])
            
            hrn = lo * fe * dph * np
            
            if hrn <= 1:
                level = "Riesgo Despreciable"
                color = '#90EE90'
            elif hrn <= 5:
                level = "Riesgo Muy Bajo"
                color = '#98FB98'
            elif hrn <= 10:
                level = "Riesgo Bajo"
                color = '#FFFF99'
            elif hrn <= 50:
                level = "Riesgo Significante"
                color = '#FFD700'
            elif hrn <= 100:
                level = "Riesgo Alto"
                color = '#FFA500'
            elif hrn <= 500:
                level = "Riesgo Muy Alto"
                color = '#FF6347'
            elif hrn <= 1000:
                level = "Riesgo Extremo"
                color = '#DC143C'
            else:
                level = "Riesgo Inaceptable"
                color = '#8B0000'

            self.hrn_result_label.config(text=f"HRN = {hrn:.2f}", foreground=color)
            self.hrn_level_label.config(text=level, foreground=color, font=('Arial', 12, 'bold'))
            
            self.current_hrn = {
                'hrn': hrn,
                'level': level,
                'lo': lo,
                'lo_desc': lo_text.split(' - ')[1],
                'fe': fe,
                'fe_desc': fe_text.split(' - ')[1],
                'dph': dph,
                'dph_desc': dph_text.split(' - ')[1],
                'np': np,
                'np_desc': np_text.split(' - ')[1]
            }
            
        except Exception as e:
            self.hrn_result_label.config(text="Error en cálculo", foreground='red')
    
    def save_hrn_calculation(self):
        """Guardar cálculo HRN en el historial"""
        if not hasattr(self, 'current_hrn'):
            messagebox.showwarning("Advertencia", "Primero calcule el HRN")
            return
        
        description = self.hrn_description.get()
        if not description:
            messagebox.showwarning("Advertencia", "Ingrese una descripción del peligro")
            return
        
        calc = {
            'description': description,
            'hrn': self.current_hrn['hrn'],
            'level': self.current_hrn['level'],
            'lo': self.current_hrn['lo'],
            'lo_desc': self.current_hrn['lo_desc'],
            'fe': self.current_hrn['fe'],
            'fe_desc': self.current_hrn['fe_desc'],
            'dph': self.current_hrn['dph'],
            'dph_desc': self.current_hrn['dph_desc'],
            'np': self.current_hrn['np'],
            'np_desc': self.current_hrn['np_desc'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.hrn_calculations.append(calc)
        
        idx = len(self.hrn_calculations)
        self.hrn_tree.insert('', 'end', text=str(idx), values=(
            description[:40] + '...' if len(description) > 40 else description,
            f"{calc['hrn']:.2f}",
            calc['level']
        ))
        
        messagebox.showinfo("Éxito", "Cálculo HRN guardado en el historial")
        self.clear_hrn_form()
    
    def clear_hrn_form(self):
        """Limpiar formulario HRN"""
        self.hrn_description.delete(0, 'end')
        self.lo_var.set('')
        self.fe_var.set('')
        self.dph_var.set('')
        self.np_var.set('')
        self.hrn_result_label.config(text="HRN = ?", foreground='blue')
        self.hrn_level_label.config(text="Seleccione todos los valores", 
                                   foreground='gray', font=('Arial', 11))
        if hasattr(self, 'current_hrn'):
            delattr(self, 'current_hrn')
    
    def delete_hrn_calculation(self):
        """Eliminar cálculo HRN seleccionado"""
        selected = self.hrn_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un cálculo para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Desea eliminar el cálculo seleccionado?"):
            idx = int(self.hrn_tree.item(selected[0])['text']) - 1
            self.hrn_calculations.pop(idx)
            self.hrn_tree.delete(selected[0])
            
            for i, item in enumerate(self.hrn_tree.get_children()):
                self.hrn_tree.item(item, text=str(i+1))

    def create_analysis_tab(self):
        """Pestaña de análisis y gráficos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Análisis y Gráficos")
        
        stats_frame = ttk.LabelFrame(frame, text="Estadísticas", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="No hay riesgos añadidos", 
                                     font=('Arial', 10))
        self.stats_label.pack()
        
        graph_frame = ttk.Frame(frame)
        graph_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.fig = Figure(figsize=(12, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Botón actualizar gráficos
        ttk.Button(frame, text="Actualizar Análisis", 
                   command=self.update_analysis).pack(pady=10)
        
    def create_report_tab(self):
        """Pestaña de generación de reportes"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Generar Reporte")
        
        info_frame = ttk.LabelFrame(frame, text="Información del Reporte", padding=20)
        info_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(info_frame, text="Generar reporte completo en PDF", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        ttk.Label(info_frame, text="El reporte incluirá:", 
                 font=('Arial', 10)).pack(pady=5)
        
        items = [
            "✓ Datos de la máquina",
            "✓ Lista completa de riesgos evaluados",
            "✓ Cálculos de Performance Level (PLr)",
            "✓ Gráficos de análisis",
            "✓ Medidas de control propuestas"
        ]
        
        for item in items:
            ttk.Label(info_frame, text=item, font=('Arial', 10)).pack(anchor='w', padx=50)
        
        # Botones
        btn_frame = ttk.Frame(info_frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="Generar PDF", command=self.generate_pdf,
                  style='Accent.TButton').pack(side='left', padx=10)
        
        ttk.Button(btn_frame, text="Guardar Proyecto (JSON)", 
                  command=self.save_project).pack(side='left', padx=10)
        
        ttk.Button(btn_frame, text="Cargar Proyecto", 
                  command=self.load_project).pack(side='left', padx=10)
    
    def create_about_tab(self):
        """Pestaña de información del sistema"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Acerca de")
        
        content_frame = ttk.Frame(frame)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Título
        title_label = ttk.Label(
            content_frame, 
            text="Sistema de Análisis de Riesgo",
            font=('Arial', 20, 'bold'),
            foreground='#003366'
        )
        title_label.pack(pady=20)
        
        subtitle_label = ttk.Label(
            content_frame,
            text="ISO 13849-1",
            font=('Arial', 16),
            foreground='#666666'
        )
        subtitle_label.pack(pady=5)
        
        # Separador
        separator1 = ttk.Separator(content_frame, orient='horizontal')
        separator1.pack(fill='x', pady=20, padx=50)
        
        # Frame de información
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(pady=20)
        
        # Versión
        version_frame = ttk.Frame(info_frame)
        version_frame.pack(pady=10)
        ttk.Label(
            version_frame,
            text="Versión:",
            font=('Arial', 12, 'bold')
        ).pack(side='left', padx=5)
        ttk.Label(
            version_frame,
            text="1.0",
            font=('Arial', 12)
        ).pack(side='left')
        
        # Fecha de creación
        date_frame = ttk.Frame(info_frame)
        date_frame.pack(pady=10)
        ttk.Label(
            date_frame,
            text="Build Date:",
            font=('Arial', 12, 'bold')
        ).pack(side='left', padx=5)
        ttk.Label(
            date_frame,
            text="2025/11/01",
            font=('Arial', 12)
        ).pack(side='left')
        
        # Autor
        author_frame = ttk.Frame(info_frame)
        author_frame.pack(pady=10)
        ttk.Label(
            author_frame,
            text="Autor:",
            font=('Arial', 12, 'bold')
        ).pack(side='left', padx=5)
        ttk.Label(
            author_frame,
            text="Saul Henriquez",
            font=('Arial', 12)
        ).pack(side='left')
        
        # Separador
        separator2 = ttk.Separator(content_frame, orient='horizontal')
        separator2.pack(fill='x', pady=20, padx=50)
        
        # Universidad
        university_label = ttk.Label(
            content_frame,
            text="Universidad Tecnológica de El Salvador",
            font=('Arial', 14, 'bold'),
            foreground='#003366'
        )
        university_label.pack(pady=15)
        
        # Descripción
        description_text = (
            "Sistema para la evaluación y análisis de riesgos\n"
            "de maquinaria industrial según norma ISO 13849-1"
        )
        description_label = ttk.Label(
            content_frame,
            text=description_text,
            font=('Arial', 10),
            foreground='#666666',
            justify='center'
        )
        description_label.pack(pady=10)
        
        # Copyright
        copyright_label = ttk.Label(
            content_frame,
            text="© 2025 - Todos los derechos reservados",
            font=('Arial', 9, 'italic'),
            foreground='#999999'
        )
        copyright_label.pack(pady=20)
    
    def save_machine_data(self):
        """Guardar datos de la máquina"""
        self.machine_data = {
            key: entry.get() for key, entry in self.machine_entries.items()
        }
        self.machine_data['description'] = self.description_text.get('1.0', 'end-1c')
        self.machine_data['date'] = datetime.now().strftime("%Y-%m-%d")
        self.machine_data['photos'] = self.machine_photos
        
        messagebox.showinfo("Éxito", "Datos de la máquina guardados correctamente")
    
    def add_photo(self):
        """Añadir foto de la máquina"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar fotografía",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Convertir imagen a base64 para almacenamiento
                with open(file_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                
                # Obtener nombre del archivo
                filename = os.path.basename(file_path)
                
                # Añadir a la lista
                photo_info = {
                    'filename': filename,
                    'data': img_data,
                    'path': file_path
                }
                self.machine_photos.append(photo_info)
                
                # Actualizar visualización
                self.update_photos_display()
                
                messagebox.showinfo("Éxito", f"Foto '{filename}' añadida correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{str(e)}")
    
    def remove_photo(self):
        """Eliminar foto seleccionada"""
        if not self.machine_photos:
            messagebox.showwarning("Advertencia", "No hay fotos para eliminar")
            return
        
        # Crear ventana de selección
        remove_window = tk.Toplevel(self.root)
        remove_window.title("Eliminar Foto")
        remove_window.geometry("400x300")
        
        ttk.Label(remove_window, text="Seleccione la foto a eliminar:", 
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        listbox = tk.Listbox(remove_window, height=10)
        listbox.pack(fill='both', expand=True, padx=20, pady=10)
        
        for i, photo in enumerate(self.machine_photos):
            listbox.insert(tk.END, f"{i+1}. {photo['filename']}")
        
        def delete_selected():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                removed = self.machine_photos.pop(idx)
                self.update_photos_display()
                messagebox.showinfo("Éxito", f"Foto '{removed['filename']}' eliminada")
                remove_window.destroy()
            else:
                messagebox.showwarning("Advertencia", "Seleccione una foto")
        
        ttk.Button(remove_window, text="Eliminar", command=delete_selected).pack(pady=10)
    
    def update_photos_display(self):
        """Actualizar visualización de fotos"""
        
        for widget in self.photos_inner_frame.winfo_children():
            widget.destroy()
        
        self.photo_labels.clear()
        
        if not self.machine_photos:
            ttk.Label(self.photos_inner_frame, text="No hay fotos añadidas", 
                     foreground='gray').pack(pady=20)
            return
        
        for i, photo in enumerate(self.machine_photos):
            frame = ttk.Frame(self.photos_inner_frame, relief='solid', borderwidth=1)
            frame.pack(side='left', padx=5, pady=5)
            
            try:
                img_data = base64.b64decode(photo['data'])
                img = PILImage.open(io.BytesIO(img_data))
                
                # Crear miniatura
                img.thumbnail((120, 120), PILImage.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                
                # Mostrar miniatura
                label = ttk.Label(frame, image=photo_img)
                label.image = photo_img  # Mantener referencia
                label.pack()
                
                # Nombre del archivo
                name_label = ttk.Label(frame, text=photo['filename'][:15] + '...' 
                                      if len(photo['filename']) > 15 else photo['filename'],
                                      font=('Arial', 8))
                name_label.pack()
                
                self.photo_labels.append(label)
                
            except Exception as e:
                ttk.Label(frame, text=f"Error\n{photo['filename']}", 
                         foreground='red', font=('Arial', 8)).pack()
        
        # Actualizar región de scroll
        self.photos_inner_frame.update_idletasks()
        self.photos_canvas.configure(scrollregion=self.photos_canvas.bbox("all"))
    
    def calculate_plr(self, event=None):
        """Calcular el Performance Level requerido según ISO 13849-1"""
        s = self.severity.current()
        f = self.frequency.current()
        p = self.avoidance.current()
        
        if s == -1 or f == -1 or p == -1:
            return
        
        # Matriz de decisión ISO 13849-1
        # [S][F][P]
        plr_matrix = {
            (0, 0, 0): 'a',  # S1, F1, P1
            (0, 0, 1): 'b',  # S1, F1, P2
            (0, 1, 0): 'b',  # S1, F2, P1
            (0, 1, 1): 'c',  # S1, F2, P2
            (1, 0, 0): 'c',  # S2, F1, P1
            (1, 0, 1): 'd',  # S2, F1, P2
            (1, 1, 0): 'd',  # S2, F2, P1
            (1, 1, 1): 'e',  # S2, F2, P2
        }
        
        plr = plr_matrix.get((s, f, p), 'a')
        self.plr_label.config(text=f"PLr = {plr.upper()}", foreground='red', 
                             font=('Arial', 12, 'bold'))
        return plr
    
    def add_risk(self):
        """Añadir un nuevo riesgo"""
        if not self.risk_desc.get():
            messagebox.showwarning("Advertencia", "Debe ingresar una descripción del peligro")
            return
        
        plr = self.calculate_plr()
        if not plr:
            messagebox.showwarning("Advertencia", "Debe seleccionar S, F y P")
            return
        
        risk = {
            'description': self.risk_desc.get(),
            'zone': self.risk_zone.get(),
            'severity': self.severity.get(),
            'frequency': self.frequency.get(),
            'avoidance': self.avoidance.get(),
            'plr': plr.upper(),
            'control_measures': self.control_measures.get('1.0', 'end-1c')
        }
        
        self.risks.append(risk)
        
        idx = len(self.risks)
        self.risk_tree.insert('', 'end', text=str(idx), values=(
            risk['description'][:30] + '...' if len(risk['description']) > 30 else risk['description'],
            risk['zone'],
            risk['severity'].split('-')[0].strip(),
            risk['frequency'].split('-')[0].strip(),
            risk['avoidance'].split('-')[0].strip(),
            risk['plr']
        ))
        
        self.clear_risk_form()
        messagebox.showinfo("Éxito", "Riesgo añadido correctamente")
    
    def clear_risk_form(self):
        """Limpiar formulario de riesgo"""
        self.risk_desc.delete(0, 'end')
        self.risk_zone.delete(0, 'end')
        self.severity.set('')
        self.frequency.set('')
        self.avoidance.set('')
        self.control_measures.delete('1.0', 'end')
        self.plr_label.config(text="Seleccione S, F y P", foreground='blue', 
                             font=('Arial', 10))
    
    def delete_risk(self):
        """Eliminar riesgo seleccionado"""
        selected = self.risk_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un riesgo para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Desea eliminar el riesgo seleccionado?"):
            idx = int(self.risk_tree.item(selected[0])['text']) - 1
            self.risks.pop(idx)
            self.risk_tree.delete(selected[0])
            
            for i, item in enumerate(self.risk_tree.get_children()):
                self.risk_tree.item(item, text=str(i+1))
    
    def update_analysis(self):
        """Actualizar análisis y gráficos"""
        if not self.risks and not self.hrn_calculations:
            messagebox.showinfo("Información", "No hay datos para analizar")
            return
        
        self.fig.clear()
        
        has_iso_risks = len(self.risks) > 0
        has_hrn_calcs = len(self.hrn_calculations) > 0
        
        # Determinar número de subplots
        if has_iso_risks and has_hrn_calcs:
            # Mostrar ambos análisis
            ax1 = self.fig.add_subplot(221)
            ax2 = self.fig.add_subplot(222)
            ax3 = self.fig.add_subplot(223)
            ax4 = self.fig.add_subplot(224)
        elif has_iso_risks:
            ax1 = self.fig.add_subplot(121)
            ax2 = self.fig.add_subplot(122)
        elif has_hrn_calcs:
            ax3 = self.fig.add_subplot(121)
            ax4 = self.fig.add_subplot(122)
        
        stats_text = ""
        
        # Análisis ISO 13849
        if has_iso_risks:
            total = len(self.risks)
            plr_count = {}
            for risk in self.risks:
                plr = risk['plr']
                plr_count[plr] = plr_count.get(plr, 0) + 1
            
            stats_text += f"=== ISO 13849-1 ===\n"
            stats_text += f"Total de Riesgos: {total}\n"
            stats_text += "Distribución por PLr:\n"
            for plr in sorted(plr_count.keys()):
                percentage = (plr_count[plr] / total) * 100
                stats_text += f"  PLr {plr}: {plr_count[plr]} ({percentage:.1f}%)\n"
            
            # Gráfico de barras - Distribución PLr
            plr_labels = sorted(plr_count.keys())
            plr_values = [plr_count[plr] for plr in plr_labels]
            colors_map = {'A': '#90EE90', 'B': '#FFFF99', 'C': '#FFD700', 
                         'D': '#FFA500', 'E': '#FF6347'}
            bar_colors = [colors_map.get(plr, 'gray') for plr in plr_labels]
            
            ax1.bar(plr_labels, plr_values, color=bar_colors, edgecolor='black')
            ax1.set_xlabel('Performance Level Requerido')
            ax1.set_ylabel('Cantidad de Riesgos')
            ax1.set_title('Distribución de Riesgos por PLr (ISO 13849)')
            ax1.grid(axis='y', alpha=0.3)
            
            # Gráfico circular - Severidad
            s_count = {}
            for risk in self.risks:
                s = 'S1' if 'S1' in risk['severity'] else 'S2'
                s_count[s] = s_count.get(s, 0) + 1
            
            ax2.pie(s_count.values(), labels=s_count.keys(), autopct='%1.1f%%',
                   colors=['#90EE90', '#FF6347'], startangle=90)
            ax2.set_title('Distribución por Severidad')
        
        # Análisis HRN
        if has_hrn_calcs:
            total_hrn = len(self.hrn_calculations)
            hrn_levels = {}
            
            stats_text += f"\n=== Método HRN ===\n"
            stats_text += f"Total de Cálculos: {total_hrn}\n"
            stats_text += "Distribución por Nivel:\n"
            
            for calc in self.hrn_calculations:
                level = calc['level']
                hrn_levels[level] = hrn_levels.get(level, 0) + 1
            
            for level in hrn_levels:
                percentage = (hrn_levels[level] / total_hrn) * 100
                stats_text += f"  {level}: {hrn_levels[level]} ({percentage:.1f}%)\n"
            
            # Gráfico de barras - Distribución HRN
            level_order = [
                "Riesgo Despreciable",
                "Riesgo Muy Bajo",
                "Riesgo Bajo",
                "Riesgo Significante",
                "Riesgo Alto",
                "Riesgo Muy Alto",
                "Riesgo Extremo",
                "Riesgo Inaceptable"
            ]
            
            level_colors = {
                "Riesgo Despreciable": '#90EE90',
                "Riesgo Muy Bajo": '#98FB98',
                "Riesgo Bajo": '#FFFF99',
                "Riesgo Significante": '#FFD700',
                "Riesgo Alto": '#FFA500',
                "Riesgo Muy Alto": '#FF6347',
                "Riesgo Extremo": '#DC143C',
                "Riesgo Inaceptable": '#8B0000'
            }
            
            present_levels = [level for level in level_order if level in hrn_levels]
            level_values = [hrn_levels[level] for level in present_levels]
            bar_colors_hrn = [level_colors[level] for level in present_levels]
            
            ax3.bar(range(len(present_levels)), level_values, color=bar_colors_hrn, edgecolor='black')
            ax3.set_xticks(range(len(present_levels)))
            ax3.set_xticklabels([l.replace('Riesgo ', '') for l in present_levels], rotation=45, ha='right')
            ax3.set_xlabel('Nivel de Riesgo')
            ax3.set_ylabel('Cantidad')
            ax3.set_title('Distribución de Riesgos HRN')
            ax3.grid(axis='y', alpha=0.3)
            
            # Gráfico de valores HRN individuales
            hrn_values = [calc['hrn'] for calc in self.hrn_calculations]
            descriptions = [calc['description'][:15] + '...' if len(calc['description']) > 15 
                          else calc['description'] for calc in self.hrn_calculations]
            
            colors_hrn_bars = []
            for hrn in hrn_values:
                if hrn <= 1:
                    colors_hrn_bars.append('#90EE90')
                elif hrn <= 5:
                    colors_hrn_bars.append('#98FB98')
                elif hrn <= 10:
                    colors_hrn_bars.append('#FFFF99')
                elif hrn <= 50:
                    colors_hrn_bars.append('#FFD700')
                elif hrn <= 100:
                    colors_hrn_bars.append('#FFA500')
                elif hrn <= 500:
                    colors_hrn_bars.append('#FF6347')
                elif hrn <= 1000:
                    colors_hrn_bars.append('#DC143C')
                else:
                    colors_hrn_bars.append('#8B0000')
            
            ax4.barh(range(len(hrn_values)), hrn_values, color=colors_hrn_bars, edgecolor='black')
            ax4.set_yticks(range(len(hrn_values)))
            ax4.set_yticklabels(descriptions)
            ax4.set_xlabel('Valor HRN')
            ax4.set_title('Valores HRN Calculados')
            ax4.grid(axis='x', alpha=0.3)
        
        self.stats_label.config(text=stats_text)
        self.fig.tight_layout()
        self.canvas.draw()
    
    def generate_pdf(self):
        """Generar reporte en PDF"""
        if not self.machine_data:
            messagebox.showwarning("Advertencia", "Debe guardar los datos de la máquina primero")
            return
        
        if not self.risks:
            messagebox.showwarning("Advertencia", "Debe añadir al menos un riesgo")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Analisis_Riesgo_{self.machine_data.get('model', 'Maquina')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        
        if not filename:
            return
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            doc.topMargin = 0.75 * inch
            doc.bottomMargin = 0.75 * inch
            doc.leftMargin = 1 * inch
            doc.rightMargin = 1 * inch
            story = []
            styles = getSampleStyleSheet()
            
            # Estilo personalizado
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#003366'),
                spaceAfter=20,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#003366'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Título
            story.append(Paragraph("Análisis de Riesgo según ISO 13849-1", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Datos de la máquina
            story.append(Paragraph("DATOS DE LA MÁQUINA", heading_style))
            
            machine_table_data = [
                ['Campo', 'Valor'],
                ['Tipo de Máquina', self.machine_data.get('machine_type', '')],
                ['Modelo', self.machine_data.get('model', '')],
                ['Fabricante', self.machine_data.get('manufacturer', '')],
                ['Número de Serie', self.machine_data.get('serial_number', '')],
                ['Año', self.machine_data.get('year', '')],
                ['Ubicación', self.machine_data.get('location', '')],
                ['Analista', self.machine_data.get('analyst', '')],
                ['Fecha de Análisis', self.machine_data.get('date', '')],
            ]        
            machine_table = Table(machine_table_data, colWidths=[2*inch, 4*inch])
            machine_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(machine_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Descripción
            if self.machine_data.get('description'):
                story.append(Paragraph("Descripción:", styles['Heading3']))
                story.append(Paragraph(self.machine_data['description'], styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            story.append(PageBreak())
            
            # Tabla de riesgos
            story.append(Paragraph("EVALUACIÓN DE RIESGOS", heading_style))
            
            risk_table_data = [['#', 'Descripción', 'Zona', 'S', 'F', 'P', 'PLr']]
            
            for i, risk in enumerate(self.risks, 1):
                risk_table_data.append([
                    str(i),
                    risk['description'][:50] + '...' if len(risk['description']) > 50 else risk['description'],
                    risk['zone'][:20] if risk['zone'] else '-',
                    risk['severity'].split('-')[0].strip(),
                    risk['frequency'].split('-')[0].strip(),
                    risk['avoidance'].split('-')[0].strip(),
                    risk['plr']
                ])
            
            risk_table = Table(risk_table_data, colWidths=[0.3*inch, 2.5*inch, 1.2*inch, 
                                                           0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(risk_table)
            story.append(PageBreak())
            
            # Medidas de control
            story.append(Paragraph("MEDIDAS DE CONTROL", heading_style))
            
            for i, risk in enumerate(self.risks, 1):
                story.append(Paragraph(f"<b>{i}. {risk['description']}</b>", styles['Normal']))
                story.append(Paragraph(f"<i>PLr requerido: {risk['plr']}</i>", styles['Normal']))
                if risk['control_measures']:
                    story.append(Paragraph(f"Medidas: {risk['control_measures']}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Cálculos HRN si existen
            if self.hrn_calculations:
                story.append(PageBreak())
                story.append(Paragraph("CÁLCULOS HRN (HAZARD RATING NUMBER)", heading_style))
                
                hrn_table_data = [['#', 'Descripción', 'LO', 'FE', 'DPH', 'NP', 'HRN', 'Nivel']]
                
                for i, calc in enumerate(self.hrn_calculations, 1):
                    hrn_table_data.append([
                        str(i),
                        calc['description'][:30] + '...' if len(calc['description']) > 30 else calc['description'],
                        str(calc['lo']),
                        str(calc['fe']),
                        str(calc['dph']),
                        str(calc['np']),
                        f"{calc['hrn']:.2f}",
                        calc['level']
                    ])
                
                hrn_table = Table(hrn_table_data, colWidths=[0.3*inch, 2*inch, 0.5*inch, 
                                                             0.5*inch, 0.5*inch, 0.5*inch, 
                                                             0.7*inch, 1.5*inch])
                hrn_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                
                story.append(hrn_table)
                story.append(Spacer(1, 0.3*inch))
                
                # Detalle de cálculos HRN
                story.append(Paragraph("Detalle de Cálculos HRN:", styles['Heading3']))
                
                for i, calc in enumerate(self.hrn_calculations, 1):
                    story.append(Paragraph(f"<b>{i}. {calc['description']}</b>", styles['Normal']))
                    story.append(Paragraph(f"LO ({calc['lo']}): {calc['lo_desc']}", styles['Normal']))
                    story.append(Paragraph(f"FE ({calc['fe']}): {calc['fe_desc']}", styles['Normal']))
                    story.append(Paragraph(f"DPH ({calc['dph']}): {calc['dph_desc']}", styles['Normal']))
                    story.append(Paragraph(f"NP ({calc['np']}): {calc['np_desc']}", styles['Normal']))
                    story.append(Paragraph(f"<b>HRN = {calc['hrn']:.2f} → {calc['level']}</b>", styles['Normal']))
                    story.append(Spacer(1, 0.15*inch))

            # Gráficos
            if self.risks:
                self.update_analysis()
                
                # Guardar gráfico como imagen
                buf = io.BytesIO()
                self.fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                
                story.append(PageBreak())
                story.append(Paragraph("ANÁLISIS GRÁFICO", heading_style))
                
                
                for i, calc in enumerate(self.hrn_calculations, 1):
                    story.append(Paragraph(f"<b>{i}. {calc['description']}</b>", styles['Normal']))
                    story.append(Paragraph(f"LO ({calc['lo']}): {calc['lo_desc']}", styles['Normal']))
                    story.append(Paragraph(f"FE ({calc['fe']}): {calc['fe_desc']}", styles['Normal']))
                    story.append(Paragraph(f"DPH ({calc['dph']}): {calc['dph_desc']}", styles['Normal']))
                    story.append(Paragraph(f"NP ({calc['np']}): {calc['np_desc']}", styles['Normal']))
                    story.append(Paragraph(f"<b>HRN = {calc['hrn']:.2f} → {calc['level']}</b>", styles['Normal']))
                    story.append(Spacer(1, 0.15*inch))

            # Gráficos
            if self.risks:
                self.update_analysis()
                
                # Guardar gráfico como imagen
                buf = io.BytesIO()
                self.fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                
                story.append(PageBreak())
                story.append(Paragraph("ANÁLISIS GRÁFICO", heading_style))
                
                img = Image(buf, width=7*inch, height=3.5*inch)
                story.append(img)
            
            # Añadir fotos de la máquina
            self.add_photos_to_pdf(story, styles)
            
            # Generar PDF
            doc.build(story)
            messagebox.showinfo("Éxito", f"Reporte PDF generado correctamente:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF:\n{str(e)}")
    
    def add_photos_to_pdf(self, story, styles):
        """Añadir fotos al PDF"""
        if not self.machine_photos:
            return
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        story.append(PageBreak())
        story.append(Paragraph("FOTOGRAFÍAS DE LA MÁQUINA", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Añadir fotos (máximo 2 por página)
        for i, photo in enumerate(self.machine_photos):
            try:
                # Decodificar imagen desde base64
                img_data = base64.b64decode(photo['data'])
                img_buffer = io.BytesIO(img_data)
                
                # Crear imagen para PDF
                img = Image(img_buffer, width=5*inch, height=3.5*inch, kind='proportional')
                story.append(img)
                story.append(Paragraph(f"<i>Figura {i+1}: {photo['filename']}</i>", styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
                
                # Nueva página cada 2 fotos
                if (i + 1) % 2 == 0 and i < len(self.machine_photos) - 1:
                    story.append(PageBreak())
                    
            except Exception as e:
                story.append(Paragraph(f"<i>Error al cargar imagen: {photo['filename']}</i>", 
                                      styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
    
    def save_project(self):
        """Guardar proyecto en JSON"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            project_data = {
                'machine_data': self.machine_data,
                'risks': self.risks,
                'photos': self.machine_photos,
                'hrn_calculations': self.hrn_calculations
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", "Proyecto guardado correctamente")
    
    def load_project(self):
        """Cargar proyecto desde JSON"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Cargar datos de máquina
            self.machine_data = project_data.get('machine_data', {})
            for key, value in self.machine_data.items():
                if key in self.machine_entries:
                    self.machine_entries[key].delete(0, 'end')
                    self.machine_entries[key].insert(0, value)
                elif key == 'description':
                    self.description_text.delete('1.0', 'end')
                    self.description_text.insert('1.0', value)
            
            # Cargar fotos
            self.machine_photos = project_data.get('photos', [])
            self.update_photos_display()
            
            # Cargar riesgos ISO 13849
            self.risks = project_data.get('risks', [])
            
            # Actualizar treeview de riesgos
            for item in self.risk_tree.get_children():
                self.risk_tree.delete(item)
            
            for idx, risk in enumerate(self.risks, 1):
                self.risk_tree.insert('', 'end', text=str(idx), values=(
                    risk['description'][:30] + '...' if len(risk['description']) > 30 else risk['description'],
                    risk['zone'],
                    risk['severity'].split('-')[0].strip(),
                    risk['frequency'].split('-')[0].strip(),
                    risk['avoidance'].split('-')[0].strip(),
                    risk['plr']
                ))
            
            # Cargar cálculos HRN
            self.hrn_calculations = project_data.get('hrn_calculations', [])
            
            # Actualizar treeview de HRN
            for item in self.hrn_tree.get_children():
                self.hrn_tree.delete(item)
            
            for idx, calc in enumerate(self.hrn_calculations, 1):
                self.hrn_tree.insert('', 'end', text=str(idx), values=(
                    calc['description'][:40] + '...' if len(calc['description']) > 40 else calc['description'],
                    f"{calc['hrn']:.2f}",
                    calc['level']
                ))
            
            messagebox.showinfo("Éxito", "Proyecto cargado correctamente")

if __name__ == "__main__":
    root = ttkbootstrap.Window()

    app = RiskAnalysisISO13849(root)
    root.mainloop()