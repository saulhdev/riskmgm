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
                    risk['description'][:40] + '...' if len(risk['description']) > 40 else risk['description'],
                    risk['zone'][:60] if risk['zone'] else '-',
                    risk['severity'].split('-')[0].strip(),
                    risk['frequency'].split('-')[0].strip(),
                    risk['avoidance'].split('-')[0].strip(),
                    risk['plr']
                ])
            
            risk_table = Table(risk_table_data, colWidths=[0.3*inch, 2*inch, 3*inch, 
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
                    story.append(Paragraph(f"Medidas:\n{risk['control_measures']}", styles['Normal']))
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
            # Limpiar machine_data de cualquier clave de fotos para evitar duplicados
            machine_data_clean = dict(self.machine_data)
            for k in ('photos', 'machine_photos', 'images'):
                machine_data_clean.pop(k, None)

            project_data = {
                'machine_data': machine_data_clean,
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
            self.machine_data = project_data.get('machine_data', {}) or {}

            # Migrar fotos anidadas si existieran (compatibilidad con archivos antiguos)
            nested_photos = self.machine_data.pop('photos', None)

            # Elegir fotos preferentemente desde la clave superior
            if 'photos' in project_data:
                self.machine_photos = project_data.get('photos') or []
            elif nested_photos is not None:
                self.machine_photos = nested_photos
            else:
                self.machine_photos = []

            # Cargar datos en la interfaz
            for key, value in self.machine_data.items():
                if key in self.machine_entries:
                    self.machine_entries[key].delete(0, 'end')
                    self.machine_entries[key].insert(0, value)
                elif key == 'description':
                    self.description_text.delete('1.0', 'end')
                    self.description_text.insert('1.0', value)
            
            # Cargar fotos (ya migradas)
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
        
        # Construir textos estadísticos separados
        iso_stats = ""
        hrn_stats = ""
        
        # Análisis ISO 13849
        if has_iso_risks:
            total = len(self.risks)
            plr_count = {}
            for risk in self.risks:
                plr = risk['plr']
                plr_count[plr] = plr_count.get(plr, 0) + 1
            
            iso_stats += f"=== ISO 13849-1 ===\n"
            iso_stats += f"Total de Riesgos: {total}\n"
            iso_stats += "Distribución por PLr:\n"
            for plr in sorted(plr_count.keys()):
                percentage = (plr_count[plr] / total) * 100
                iso_stats += f"  PLr {plr}: {plr_count[plr]} ({percentage:.1f}%)\n"
            
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
            
            hrn_stats += f"=== Método HRN ===\n"
            hrn_stats += f"Total de Cálculos: {total_hrn}\n"
            hrn_stats += "Distribución por Nivel:\n"
            
            for calc in self.hrn_calculations:
                level = calc['level']
                hrn_levels[level] = hrn_levels.get(level, 0) + 1
            
            for level in hrn_levels:
                percentage = (hrn_levels[level] / total_hrn) * 100
                hrn_stats += f"  {level}: {hrn_levels[level]} ({percentage:.1f}%)\n"
            
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
        
        # Combinar estadísticas lado a lado si ambos existen
        if has_iso_risks and has_hrn_calcs:
            # Dividir en líneas
            iso_lines = iso_stats.split('\n')
            hrn_lines = hrn_stats.split('\n')
            
            # Encontrar el ancho máximo de las líneas ISO
            max_iso_width = max(len(line) for line in iso_lines) if iso_lines else 0
            
            # Combinar líneas lado a lado
            max_lines = max(len(iso_lines), len(hrn_lines))
            combined_stats = []
            
            for i in range(max_lines):
                iso_line = iso_lines[i] if i < len(iso_lines) else ""
                hrn_line = hrn_lines[i] if i < len(hrn_lines) else ""
                
                # Añadir padding a la línea ISO para alinear
                iso_padded = iso_line.ljust(max_iso_width + 5)
                combined_stats.append(f"{iso_padded}{hrn_line}")
            
            stats_text = '\n'.join(combined_stats)
        elif has_iso_risks:
            stats_text = iso_stats
        else:
            stats_text = hrn_stats
        
        self.stats_label.config(text=stats_text)
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = ttkbootstrap.Window()

    app = RiskAnalysisISO13849(root)
    root.mainloop()