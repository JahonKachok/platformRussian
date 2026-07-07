import io
import math
import os

import qrcode
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from django.conf import settings
from django.core.files.base import ContentFile

from .models import Certificate

FONT_DIR = os.path.join(settings.BASE_DIR, 'static', 'fonts')

CREAM = HexColor('#f9f4e6')
CREAM_DARK = HexColor('#f3ebd6')
GOLD = HexColor('#b8912f')
GOLD_LINE = HexColor('#c9a445')
GOLD_DEEP = HexColor('#8a7434')
NAVY = HexColor('#1e2a44')
MUTED = HexColor('#6b6f7e')

RU_MONTHS = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
]


def _register_fonts():
    fonts = {
        'CertSans': 'DejaVuSans.ttf',
        'CertSans-Bold': 'DejaVuSans-Bold.ttf',
        'CertSerif': 'DejaVuSerif.ttf',
        'CertSerif-Bold': 'DejaVuSerif-Bold.ttf',
    }
    registered = pdfmetrics.getRegisteredFontNames()
    for name, filename in fonts.items():
        if name not in registered:
            pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, filename)))


def _spaced(c, text, cx, y, font, size, char_space):
    """Draw letterspaced text centered at cx."""
    total = c.stringWidth(text, font, size) + char_space * (len(text) - 1)
    t = c.beginText(cx - total / 2, y)
    t.setFont(font, size)
    t.setCharSpace(char_space)
    t.textOut(text)
    t.setCharSpace(0)  # Tc persists in the PDF stream; reset so later text is unaffected
    c.drawText(t)


def _wrap_lines(c, text, font, size, max_width):
    """Greedy word-wrap: split text into lines that fit max_width."""
    words = text.split()
    lines, cur = [], ''
    for w in words:
        trial = f'{cur} {w}'.strip()
        if not cur or c.stringWidth(trial, font, size) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _circular_text(c, cx, cy, r, text, font, size, start_deg, end_deg, inward=False):
    """Draw text along a circle arc, one character at a time."""
    if not text:
        return
    c.setFont(font, size)
    step = (end_deg - start_deg) / max(len(text) - 1, 1)
    for i, ch in enumerate(text):
        a = math.radians(start_deg + step * i)
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        c.saveState()
        c.translate(x, y)
        c.rotate(math.degrees(a) + (90 if inward else -90))
        c.drawCentredString(0, 0, ch)
        c.restoreState()


def _laurel_emblem(c, cx, cy):
    """Small LC monogram in a circle flanked by laurel leaves."""
    c.setStrokeColor(GOLD)
    c.setFillColor(GOLD)
    c.setLineWidth(1.2)
    c.circle(cx, cy, 12, fill=False, stroke=True)
    c.setFont('CertSerif-Bold', 10)
    c.drawCentredString(cx, cy - 3.5, 'LC')
    # Stems: two arcs open at top and bottom
    c.setLineWidth(1)
    c.arc(cx - 20, cy - 20, cx + 20, cy + 20, 150, 85)
    c.arc(cx - 20, cy - 20, cx + 20, cy + 20, 305, 85)
    # Leaves angled off the stems
    for side in (-1, 1):
        for i in range(6):
            ang = math.radians(270 + side * (25 + i * 17))
            x = cx + 21 * math.cos(ang)
            y = cy + 21 * math.sin(ang)
            c.saveState()
            c.translate(x, y)
            c.rotate(math.degrees(ang) + 35 * side)
            c.ellipse(-1.8, -5.0, 1.8, 5.0, fill=True, stroke=False)
            c.restoreState()


def _seal(c, cx, cy):
    """Ornate round seal: scalloped edge, circular text, LC monogram."""
    c.setFillColor(GOLD)
    for i in range(26):
        a = math.radians(i * (360 / 26))
        c.circle(cx + 34 * math.cos(a), cy + 34 * math.sin(a), 2.2, fill=True, stroke=False)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.circle(cx, cy, 30, fill=False, stroke=True)
    c.setLineWidth(0.8)
    c.circle(cx, cy, 17, fill=False, stroke=True)
    c.setFillColor(GOLD_DEEP)
    _circular_text(c, cx, cy, 22.5, 'LINGVOCOMPETENCE', 'CertSans-Bold', 5.5, 160, 20)
    _circular_text(c, cx, cy, 22.5, 'АКАДЕМИЧЕСКИЙ СОВЕТ', 'CertSans-Bold', 5.5, 195, 345, inward=True)
    c.setFillColor(GOLD)
    c.setFont('CertSerif-Bold', 13)
    c.drawCentredString(cx, cy - 4.5, 'LC')


def _pen_nib(c, cx, cy):
    """Small fountain-pen nib icon."""
    c.saveState()
    c.translate(cx, cy)
    c.rotate(-38)
    c.setFillColor(GOLD_DEEP)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(4.5, 11)
    p.lineTo(0, 18)
    p.lineTo(-4.5, 11)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.roundRect(-2.4, 18, 4.8, 15, 2, fill=True, stroke=False)
    c.setStrokeColor(CREAM)
    c.setLineWidth(0.7)
    c.line(0, 3, 0, 12)
    c.setFillColor(CREAM)
    c.circle(0, 12, 1.2, fill=True, stroke=False)
    c.restoreState()


def generate_certificate_pdf(certificate):
    _register_fonts()
    buffer = io.BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # ---- Background ----
    c.setFillColor(CREAM)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # ---- Frames ----
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.rect(30, 30, width - 60, height - 60, fill=False, stroke=True)
    c.setStrokeColor(GOLD_LINE)
    c.setLineWidth(1.6)
    c.rect(40, 40, width - 80, height - 80, fill=False, stroke=True)

    # Thick gold corner brackets at page corners
    c.setStrokeColor(GOLD)
    c.setLineWidth(5)
    blen = 34
    for x, dx in ((12, 1), (width - 12, -1)):
        for y, dy in ((12, 1), (height - 12, -1)):
            c.line(x, y, x + blen * dx, y)
            c.line(x, y, x, y + blen * dy)

    # ---- Header ----
    c.setFillColor(NAVY)
    _spaced(c, 'LINGVOCOMPETENCE', width / 2, height - 88, 'CertSans-Bold', 11, 4)

    c.setFillColor(GOLD)
    _spaced(c, 'СЕРТИФИКАТ', width / 2, height - 146, 'CertSans-Bold', 44, 6)

    c.setFillColor(NAVY)
    _spaced(c, 'О ЗАВЕРШЕНИИ КУРСА', width / 2, height - 174, 'CertSans', 13, 4)

    _laurel_emblem(c, width / 2, height - 216)

    # ---- Recipient ----
    c.setFillColor(NAVY)
    c.setFont('CertSans', 12)
    c.drawCentredString(width / 2, height - 256, 'Настоящий сертификат вручается')

    name = certificate.user.get_full_name() or certificate.user.email
    name_size = 32
    while c.stringWidth(name, 'CertSans-Bold', name_size) > width - 260 and name_size > 16:
        name_size -= 2
    c.setFillColor(GOLD)
    c.setFont('CertSans-Bold', name_size)
    c.drawCentredString(width / 2, height - 296, name)

    # ---- Course panel ----
    px, pw = 120, width - 240
    title = certificate.course.title.upper()
    max_tw = pw - 44
    # Largest size that fits: one line preferred, two lines at 15pt and below
    for title_size in range(20, 9, -1):
        title_lines = _wrap_lines(c, title, 'CertSerif-Bold', title_size, max_tw)
        if len(title_lines) <= (1 if title_size > 15 else 2):
            break
    else:
        title_size = 10
        title_lines = _wrap_lines(c, title, 'CertSerif-Bold', title_size, max_tw)[:3]

    leading = title_size * 1.35
    ph = 66 + leading * len(title_lines)
    py = (height - 316) - ph
    c.setFillColor(CREAM_DARK)
    c.setStrokeColor(GOLD_DEEP)
    c.setLineWidth(1)
    c.rect(px, py, pw, ph, fill=True, stroke=True)

    c.setFillColor(NAVY)
    c.setFont('CertSerif', 12)
    c.drawCentredString(width / 2, py + ph - 24, 'Присуждается решением Академического совета')

    c.setFont('CertSerif-Bold', title_size)
    ty = py + ph - 46
    for line in title_lines:
        c.drawCentredString(width / 2, ty, line)
        ty -= leading

    c.setFillColor(MUTED)
    c.setFont('CertSans', 11)
    c.drawCentredString(width / 2, py + 13, 'за успешное прохождение учебного курса')

    # ---- Bottom row: date / seal / platform ----
    base_y = 108
    line_w = 150

    lx = width * 0.24
    d = certificate.issued_at
    date_str = f'{d.day} {RU_MONTHS[d.month - 1]} {d.year} г.'
    c.setFillColor(NAVY)
    c.setFont('CertSans', 12)
    c.drawCentredString(lx, base_y + 22, date_str)
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.75)
    c.line(lx - line_w / 2, base_y + 14, lx + line_w / 2, base_y + 14)
    c.setFillColor(MUTED)
    _spaced(c, 'ДАТА ВЫДАЧИ', lx, base_y, 'CertSans', 8.5, 1.5)
    _pen_nib(c, lx - line_w / 2 - 28, base_y + 12)

    _seal(c, width / 2, base_y + 26)

    rx = width * 0.73
    c.setFillColor(NAVY)
    c.setFont('CertSans-Bold', 12)
    c.drawCentredString(rx, base_y + 22, 'LingvoCompetence')
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.75)
    c.line(rx - line_w / 2, base_y + 14, rx + line_w / 2, base_y + 14)
    c.setFillColor(MUTED)
    c.setFont('CertSans', 9)
    c.drawCentredString(rx, base_y, 'lingvocompetence.uz')

    # Certificate ID
    c.setFillColor(MUTED)
    c.setFont('CertSans', 8.5)
    c.drawCentredString(width / 2, 50, f'ID сертификата: {certificate.certificate_id}')

    # ---- QR code (bottom-right) ----
    qr = qrcode.QRCode(version=1, box_size=3, border=2)
    verify_url = f'https://lingvocompetence.uz/certificates/verify/{certificate.certificate_id}/'
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white')
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    from reportlab.lib.utils import ImageReader
    qr_reader = ImageReader(qr_buffer)
    c.setFillColor(HexColor('#ffffff'))
    c.setStrokeColor(GOLD_LINE)
    c.setLineWidth(1)
    c.roundRect(width - 128, base_y + 2, 66, 66, 6, fill=True, stroke=True)
    c.drawImage(qr_reader, width - 124, base_y + 6, width=58, height=58)
    c.setFillColor(MUTED)
    c.setFont('CertSans', 5.5)
    c.drawCentredString(width - 95, base_y - 8, 'СКАНИРУЙТЕ ДЛЯ ПРОВЕРКИ')

    c.save()
    buffer.seek(0)
    return buffer.read()


def issue_certificate(user, course):
    cert, created = Certificate.objects.get_or_create(user=user, course=course)
    if created or not cert.pdf_file:
        pdf_data = generate_certificate_pdf(cert)
        filename = f'certificate_{cert.certificate_id}.pdf'
        cert.pdf_file.save(filename, ContentFile(pdf_data), save=True)

    if created:
        try:
            from apps.notifications.utils import notify
            from apps.notifications.models import Notification
            notify(
                user=user,
                title=f'Sertifikat olindi: {course.title}',
                message=f'Tabriklaymiz! "{course.title}" kursi uchun sertifikatingiz tayyor. Sertifikatlar bo\'limidan yuklab olishingiz mumkin.',
                notification_type=Notification.TYPE_CERTIFICATE,
                icon='📜',
            )
        except Exception:
            pass

    return cert
