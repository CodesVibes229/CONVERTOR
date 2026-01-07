import os
from PIL import Image
from fpdf import FPDF
import pandas as pd
from docx import Document
from history import add_history

# ---------- IMAGES ----------

def images_to_single_pdf(image_paths, output_path, progress_cb=None):
    images = []
    total = len(image_paths)

    for i, path in enumerate(image_paths, start=1):
        img = Image.open(path).convert("RGB")
        images.append(img)
        if progress_cb:
            progress_cb(i, total)

    images[0].save(output_path, save_all=True, append_images=images[1:])

    add_history({
        "type": "Images → PDF (fusion)",
        "files": len(image_paths),
        "output": output_path
    })

def images_to_multiple_pdfs(image_paths, output_dir, progress_cb=None):
    total = len(image_paths)

    for i, path in enumerate(image_paths, start=1):
        img = Image.open(path).convert("RGB")
        name = os.path.splitext(os.path.basename(path))[0]
        img.save(os.path.join(output_dir, f"{name}.pdf"))

        if progress_cb:
            progress_cb(i, total)

    add_history({
        "type": "Images → PDF (multiple)",
        "files": len(image_paths),
        "output": output_dir
    })

# ---------- CSV / EXCEL ----------

def csv_to_excel(csv_path, output_path):
    df = pd.read_csv(csv_path)
    df.to_excel(output_path, index=False)

    add_history({
        "type": "CSV → Excel",
        "files": 1,
        "output": output_path
    })

def excel_to_csv(excel_path, output_path):
    df = pd.read_excel(excel_path)
    df.to_csv(output_path, index=False)

    add_history({
        "type": "Excel → CSV",
        "files": 1,
        "output": output_path
    })

# ---------- WORD ----------

def word_to_pdf(word_path, output_path):
    doc = Document(word_path)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for para in doc.paragraphs:
        text = para.text.encode("latin-1", "ignore").decode("latin-1")
        pdf.multi_cell(0, 8, text)

    pdf.output(output_path)

    add_history({
        "type": "Word → PDF",
        "files": 1,
        "output": output_path
    })

