from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parents[2]
CERTIFICATE_DIR = BASE_DIR / "certificates"
CERTIFICATE_DIR.mkdir(exist_ok=True)


def generate_certificate(
    certificate_id: str,
    recipient_name: str,
    event_name: str,
    event_date: str,
) -> Path:
    # This is the single predefined certificate design required by the assignment.
    output_path = CERTIFICATE_DIR / f"{certificate_id}.pdf"

    width, height = landscape(A4)
    pdf = canvas.Canvas(str(output_path), pagesize=(width, height))

    # Outer border
    pdf.setStrokeColor(colors.HexColor("#1F3A5F"))
    pdf.setLineWidth(5)
    pdf.rect(30, 30, width - 60, height - 60)

    pdf.setStrokeColor(colors.HexColor("#C9A227"))
    pdf.setLineWidth(2)
    pdf.rect(45, 45, width - 90, height - 90)

    pdf.setFillColor(colors.HexColor("#1F3A5F"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(width / 2, height - 105, "CERTIFICATE OF PARTICIPATION")

    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, height - 145, "This certificate is proudly presented to")

    pdf.setFillColor(colors.HexColor("#111111"))
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(width / 2, height - 205, recipient_name)

    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width / 2, height - 245, "for successfully participating in")

    pdf.setFillColor(colors.HexColor("#1F3A5F"))
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(width / 2, height - 285, event_name)

    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(width / 2, 115, f"Event date: {event_date}")

    pdf.setStrokeColor(colors.HexColor("#888888"))
    pdf.setLineWidth(1)
    pdf.line(width / 2 - 100, 75, width / 2 + 100, 75)

    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(width / 2, 58, "Authorized Signature")

    pdf.save()
    return output_path
