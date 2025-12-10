from fpdf import FPDF
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
import tempfile
import os
from datetime import date
from flask import current_app
def generate_label_pdf(set_name, stone_count, uuid_code):
    pdf = FPDF(format="A4", unit="mm")
    pdf.add_page()
    pdf.set_auto_page_break(False)

    label_width = 60
    label_height = 25
    page_width = 210
    page_height = 297
    x = (page_width - label_width) / 2
    y = (page_height - label_height) / 2

    pdf.set_fill_color(240, 240, 240)
    pdf.rect(x, y, label_width, label_height, style='F')
    pdf.set_draw_color(0, 0, 0)
    pdf.rect(x, y, label_width, label_height)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(x, y + 6)
    pdf.cell(label_width, 6, f"{set_name} / {stone_count}", align="C")

    pdf.set_xy(x, y + 13)
    pdf.cell(label_width, 6, uuid_code, align="C")

    output = pdf.output(dest="S")
    if isinstance(output, str):
        output = output.encode("latin1")
    return BytesIO(output)

