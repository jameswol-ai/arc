import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import plotly.io as pio
import tempfile
import os

def generate_pdf_report(concept, scores, ec, materials, boq, schedule, solar, water, green, wind, seismic):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']

    story = []

    # Title
    story.append(Paragraph(f"Arc AEC Report – {concept['type']}", title_style))
    story.append(Spacer(1, 0.5*cm))

    # Summary
    story.append(Paragraph("Project Summary", heading_style))
    story.append(Paragraph(f"Type: {concept['type']}", normal_style))
    story.append(Paragraph(f"Floors: {concept['floors']}", normal_style))
    story.append(Paragraph(f"Total GFA: {concept['total_gfa']:.0f} m²", normal_style))
    story.append(Paragraph(f"Country: {concept['country']}", normal_style))
    story.append(Spacer(1, 0.3*cm))

    # AI Scores (radar chart)
    story.append(Paragraph("AI Scores", heading_style))
    from modules.renderers import radar_chart
    fig = radar_chart(scores)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        pio.write_image(fig, tmp.name, width=400, height=300)
        img_path = tmp.name
        story.append(Image(img_path, width=10*cm, height=7.5*cm))
        os.unlink(img_path)

    story.append(Spacer(1, 0.3*cm))

    # Structural Design
    story.append(Paragraph("Structural Design", heading_style))
    story.append(Paragraph(f"Foundation: {concept['structural']['foundation']}", normal_style))
    story.append(Paragraph(f"Slab System: {concept['structural']['slab_system']}", normal_style))
    story.append(Paragraph(f"Columns: {concept['structural']['columns']}", normal_style))
    story.append(Paragraph(f"Beams: {concept['structural']['beams']}", normal_style))
    story.append(Spacer(1, 0.3*cm))

    # Eurocode
    story.append(Paragraph("Eurocode Status", heading_style))
    story.append(Paragraph(ec['uls_status'], normal_style))
    story.append(Spacer(1, 0.3*cm))

    # Material Quantities
    story.append(Paragraph("Material Quantities", heading_style))
    data = [["Material", "Quantity"]]
    data.append(["Concrete", f"{materials['concrete_volume']} m³"])
    data.append(["Steel", f"{materials['steel_weight']} kg"])
    data.append(["Brick", f"{materials['brick_units']} units"])
    data.append(["Finishes", f"{materials['finish_area']} m²"])
    t = Table(data, colWidths=[6*cm, 6*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # BOQ (first 5 items)
    story.append(Paragraph("BOQ Highlights", heading_style))
    boq_data = [["Item", "Qty", "Total USD"]]
    for item in boq[:5]:
        boq_data.append([item['Item'], str(item['Qty']), f"${item['Total USD']}"])
    t_boq = Table(boq_data, colWidths=[4*cm, 3*cm, 3*cm])
    t_boq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(t_boq)
    story.append(Spacer(1, 0.3*cm))

    # Green rating and environmental
    story.append(Paragraph("Sustainability", heading_style))
    story.append(Paragraph(f"Green Rating: {green['rating']} ({green['score']}/100)", normal_style))
    story.append(Paragraph(f"Embodied Carbon: {materials['embodied_carbon_t']} t CO₂e", normal_style))
    story.append(Paragraph(f"Solar PV: {solar['installed_capacity']} kWp", normal_style))
    story.append(Paragraph(f"Rainwater Harvest: {water['harvestable_volume']} m³/year", normal_style))
    story.append(Spacer(1, 0.3*cm))

    # Wind & Seismic
    story.append(Paragraph("Wind & Seismic", heading_style))
    story.append(Paragraph(f"Wind Pressure: {wind['wind_pressure']} kN/m²", normal_style))
    story.append(Paragraph(f"Seismic Zone: {seismic['seismic_zone']:.2f}", normal_style))
    story.append(Paragraph(f"Seismic Status: {seismic['status']}", normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer