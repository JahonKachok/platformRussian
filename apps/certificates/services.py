import io
import qrcode
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from .models import Certificate


def generate_certificate_pdf(certificate):
    buffer = io.BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Background gradient simulation
    c.setFillColor(HexColor('#0f0c29'))
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Border
    c.setStrokeColor(HexColor('#6366f1'))
    c.setLineWidth(3)
    c.rect(20, 20, width - 40, height - 40, fill=False, stroke=True)

    # Title
    c.setFillColor(HexColor('#ffffff'))
    c.setFont('Helvetica-Bold', 36)
    c.drawCentredString(width / 2, height - 100, 'CERTIFICATE OF COMPLETION')

    # Subtitle
    c.setFont('Helvetica', 18)
    c.setFillColor(HexColor('#a5b4fc'))
    c.drawCentredString(width / 2, height - 140, 'This certifies that')

    # Student name
    c.setFont('Helvetica-Bold', 30)
    c.setFillColor(HexColor('#6366f1'))
    name = certificate.user.get_full_name() or certificate.user.email
    c.drawCentredString(width / 2, height - 200, name)

    # Course
    c.setFont('Helvetica', 16)
    c.setFillColor(HexColor('#e5e7eb'))
    c.drawCentredString(width / 2, height - 240, 'has successfully completed the course')

    c.setFont('Helvetica-Bold', 22)
    c.setFillColor(HexColor('#ffffff'))
    c.drawCentredString(width / 2, height - 280, certificate.course.title)

    # Level badge
    c.setFont('Helvetica', 14)
    c.setFillColor(HexColor('#a5b4fc'))
    c.drawCentredString(width / 2, height - 310, f'Level: {certificate.course.get_level_display()}')

    # Date
    c.setFont('Helvetica', 14)
    c.setFillColor(HexColor('#9ca3af'))
    date_str = certificate.issued_at.strftime('%B %d, %Y')
    c.drawCentredString(width / 2, 120, f'Issued on {date_str}')

    # Certificate ID
    c.setFont('Helvetica', 10)
    c.setFillColor(HexColor('#6b7280'))
    c.drawCentredString(width / 2, 80, f'Certificate ID: {certificate.certificate_id}')

    # QR code
    qr = qrcode.QRCode(version=1, box_size=3, border=2)
    verify_url = f'https://rustili.uz/certificates/verify/{certificate.certificate_id}/'
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white')
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    from reportlab.lib.utils import ImageReader
    qr_reader = ImageReader(qr_buffer)
    c.drawImage(qr_reader, width - 130, 60, width=80, height=80)
    c.setFont('Helvetica', 8)
    c.setFillColor(HexColor('#6b7280'))
    c.drawCentredString(width - 90, 55, 'Scan to verify')

    # Rustili branding
    c.setFont('Helvetica-Bold', 14)
    c.setFillColor(HexColor('#6366f1'))
    c.drawString(40, 80, 'RUSTILI')
    c.setFont('Helvetica', 10)
    c.setFillColor(HexColor('#9ca3af'))
    c.drawString(40, 65, 'rustili.uz')

    c.save()
    buffer.seek(0)
    return buffer.read()


def issue_certificate(user, course):
    cert, created = Certificate.objects.get_or_create(user=user, course=course)
    if created or not cert.pdf_file:
        pdf_data = generate_certificate_pdf(cert)
        filename = f'certificate_{cert.certificate_id}.pdf'
        cert.pdf_file.save(filename, ContentFile(pdf_data), save=True)
    return cert
