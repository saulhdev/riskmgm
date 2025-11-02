import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
import base64

import ttkbootstrap
from ui.menu_manager import MenuManager
from ui.tab_manager import TabManager

class RiskAnalysisISO13849:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Riesgo ISO 13849-1")
        self.root.geometry("1200x800")

        MenuManager(root, self)
        
        TabManager(root, self)
        
        self.machine_data = {}
        self.risks = []
        self.machine_photos = []
        self.hrn_calculations = []

    def close_app(self):
        """Cerrar la aplicación"""
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            self.root.destroy()  
    
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