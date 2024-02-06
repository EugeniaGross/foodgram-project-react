import io

from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def get_pdf(ingredients):
    buf = io.BytesIO()
    p = canvas.Canvas(buf)
    pdfmetrics.registerFont(TTFont('Arial', 'arialmt.ttf'))
    p.setFillColorRGB(0, 0, 1)
    p.rect(150, 780, 300, 30, fill=True)
    p.setFillColorRGB(255, 255, 255)
    p.setFont('Arial', 20)
    p.drawString(253, 787, 'FoodGram')
    p.setFillColorRGB(0, 0, 0)
    y = 0
    count = 1
    for ingredient in ingredients:
        string = (
            ingredient['ingredient__name']
            + ' - ' + str(ingredient['amount__sum'])
            + ' ' + ingredient['ingredient__measurement_unit']
        )
        p.drawString(inch * 2 + 6, inch * 10 + 15 - y, string)
        if count % 36 == 0:
            p.showPage()
            p.setFont('Arial', 20)
            y = -50
        count += 1
        y += 20
    p.save()
    buf.seek(0)
    return buf
