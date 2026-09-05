import io
import os
import tempfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import plotly.io as pio


def generate_pdf_report(concept, scores, ec, materials, boq, schedule, solar, water, green, wind, seismic):
    """Generate a self-contained Arc AEC PDF report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]
    story = []
    temp_paths = []

    try:
        story.append(Paragraph(f"Arc AEC Report - {concept.get('type', 'Design Concept')}", title_style))
        story.append(Spacer(1, 0.5 * cm))

        story.append(Paragraph("Project Summary", heading_style))
        story.append(Paragraph(f"Type: {concept.get('type', '-')}", normal_style))
        story.append(Paragraph(f"Floors: {concept.get('floors', '-')}", normal_style))
        story.append(Paragraph(f"Total GFA: {concept.get('total_gfa', 0):.0f} m²", normal_style))
        story.append(Paragraph(f"Country: {concept.get('country', '-')}", normal_style))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("AI Scores", heading_style))
        from modules.renderers import radar_chart
        fig = radar_chart(scores)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img_path = tmp.name
        pio.write_image(fig, img_path, width=800, height=600)
        temp_paths.append(img_path)
        story.append(Image(img_path, width=10 * cm, height=7.5 * cm))
        story.append(Spacer(1, 0.3 * cm))

        structural = concept.get("structural", {})
        story.append(Paragraph("Structural Design", heading_style))
        story.append(Paragraph(f"Foundation: {structural.get('foundation', '-')}", normal_style))
        story.append(Paragraph(f"Slab System: {structural.get('slab_system', '-')}", normal_style))
        story.append(Paragraph(f"Columns: {structural.get('columns', '-')}", normal_style))
        story.append(Paragraph(f"Beams: {structural.get('beams', '-')}", normal_style))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("Eurocode Status", heading_style))
        story.append(Paragraph(str(ec.get("uls_status", "Not assessed")), normal_style))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("Material Quantities", heading_style))
        data = [["Material", "Quantity"]]
        data.extend([
            ["Concrete", f"{materials.get('concrete_volume', 0)} m³"],
            ["Steel", f"{materials.get('steel_weight', 0)} kg"],
            ["Brick", f"{materials.get('brick_units', 0)} units"],
            ["Finishes", f"{materials.get('finish_area', 0)} m²"],
        ])
        table = Table(data, colWidths=[6 * cm, 6 * cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("BOQ Highlights", heading_style))
        boq_data = [["Item", "Qty", "Total USD"]]
        for item in (boq or [])[:5]:
            boq_data.append([
                str(item.get("Item", "-")),
                str(item.get("Qty", "-")),
                f"${item.get('Total USD', 0):,}",
            ])
        boq_table = Table(boq_data, colWidths=[8 * cm, 3 * cm, 3 * cm])
        boq_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(boq_table)
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("Sustainability", heading_style))
        story.append(Paragraph(f"Green Rating: {green.get('rating', '-')} ({green.get('score', 0)}/100)", normal_style))
        story.append(Paragraph(f"Embodied Carbon: {materials.get('embodied_carbon_t', 0)} t CO₂e", normal_style))
        story.append(Paragraph(f"Solar PV: {solar.get('installed_capacity', 0)} kWp", normal_style))
        story.append(Paragraph(f"Rainwater Harvest: {water.get('harvestable_volume', 0)} m³/year", normal_style))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("Wind & Seismic", heading_style))
        story.append(Paragraph(f"Wind Pressure: {wind.get('wind_pressure', 0)} kN/m²", normal_style))
        story.append(Paragraph(f"Seismic Zone: {seismic.get('seismic_zone', 0):.2f}", normal_style))
        story.append(Paragraph(f"Seismic Status: {seismic.get('status', '-')}", normal_style))

        doc.build(story)
        buffer.seek(0)
        return buffer
    finally:
        for path in temp_paths:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except OSError:
                pass
