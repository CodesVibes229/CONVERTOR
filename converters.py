import pandas as pd
from docx2pdf import convert
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

# Excel -> CSV
def excel_to_csv(input_file, output_file):
    df = pd.read_excel(input_file)
    df.to_csv(output_file, index=False)

# CSV -> Excel
def csv_to_excel(input_file, output_file):
    df = pd.read_csv(input_file)
    df.to_excel(output_file, index=False)

# Word -> PDF
def word_to_pdf(input_file, output_file):
    convert(input_file, output_file)

# Image -> PDF
def image_to_pdf(input_file, output_file):
    # Forcer l'extension PDF
    if not output_file.lower().endswith(".pdf"):
        output_file += ".pdf"

    image = Image.open(input_file)

    # Convertir en RGB si nécessaire (PNG, RGBA, etc.)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    image.save(output_file, "PDF")

# CSV -> PDF
def csv_to_pdf(input_file, output_file):
    df = pd.read_csv(input_file)
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    y = height - 40

    for col in df.columns:
        c.drawString(40, y, col)
        y -= 20

    for _, row in df.iterrows():
        for item in row:
            c.drawString(40, y, str(item))
            y -= 20
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
