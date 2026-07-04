from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_pdf(company_data, competitors, output_path="report.pdf"):
    """Generate a professional PDF report for the researched company."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], fontSize=20, spaceAfter=20
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"], spaceBefore=14, spaceAfter=8
    )
    normal_style = styles["Normal"]

    story = []

    # Title
    company_name = company_data.get("name", "Unknown Company")
    story.append(Paragraph(f"Company Research Report", title_style))
    story.append(Paragraph(f"<b>{company_name}</b>", styles["Heading1"]))
    story.append(Spacer(1, 12))

    # Company Info Table
    info_rows = [
        ["Website", company_data.get("website", "N/A")],
        ["Phone Number", company_data.get("phone") or "N/A"],
        ["Address", company_data.get("address") or "N/A"],
    ]
    table = Table(info_rows, colWidths=[4 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    # Summary
    if company_data.get("summary"):
        story.append(Paragraph("Company Summary", heading_style))
        story.append(Paragraph(company_data["summary"], normal_style))

    # Products/Services
    story.append(Paragraph("Products / Services", heading_style))
    products = company_data.get("products_services", [])
    if products:
        for p in products:
            story.append(Paragraph(f"• {p}", normal_style))
    else:
        story.append(Paragraph("No data available.", normal_style))

    # Pain Points
    story.append(Paragraph("AI-Generated Pain Points", heading_style))
    pain_points = company_data.get("pain_points", [])
    if pain_points:
        for p in pain_points:
            story.append(Paragraph(f"• {p}", normal_style))
    else:
        story.append(Paragraph("No data available.", normal_style))

    # Competitors
    story.append(Paragraph("Competitor Analysis", heading_style))
    if competitors:
        comp_rows = [["Competitor Name", "Website"]] + [
            [c["name"], c["website"]] for c in competitors
        ]
        comp_table = Table(comp_rows, colWidths=[6 * cm, 10 * cm])
        comp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(comp_table)
    else:
        story.append(Paragraph("No competitors identified.", normal_style))

    doc.build(story)
    return output_path