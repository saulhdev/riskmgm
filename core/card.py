from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph

def crear_card(risk):
    data = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CardTitle', fontSize=12, leading=14, spaceAfter=6, bold=True))
    styles.add(ParagraphStyle(name='CardText', fontSize=10, leading=12, textColor=colors.black))
    titulo = Paragraph(f"<b>{risk['description']}</b>", styles['CardTitle'])
    descripcion = Paragraph(risk['zone'], styles['CardText'])

    data.append([titulo])
    data.append([descripcion])

    tabla_sfp = Table(
        [
            ["Severidad", "Frecuencia", "Posibilidad"],
            [
                risk['severity'].split('-')[0].strip(), 
                risk['frequency'].split('-')[0].strip(), 
                risk['avoidance'].split('-')[0].strip()
            ]
        ],
        colWidths=[100, 100, 100]
    )
    tabla_sfp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.gray),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.grey),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ]))

    data.append([tabla_sfp])

    plr = Paragraph(f"<b>PLr:</b> {risk['plr'].upper()}", styles['CardText'])
    data.append([plr])
    control = Paragraph(f"<b>Medidas de Control:</b>", styles['CardText'])
    data.append([control])
    if risk['control_measures']:
        items = risk['control_measures'].split('\n')

        for measure in items:            
            measure_paragraph = Paragraph(f"&#10003; {measure}", styles['CardText'])
            data.append([measure_paragraph])

    card = Table(data, colWidths=[400])
    card.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f7f9fc")),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROUNDEDCORNERS', (0, 0), (-1, -1), 8, colors.white),
    ]))

    return card