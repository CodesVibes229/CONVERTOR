import ttkbootstrap as ttk
from ttkbootstrap.constants import SUCCESS, INFO, BOTTOM
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import time
import os
import csv
from datetime import datetime

from converters import (
    excel_to_csv,
    csv_to_excel,
    word_to_pdf,
    image_to_pdf,
    csv_to_pdf
)

HISTORY_FILE = "history.csv"


class ConverterApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.style = ttk.Style("flatly")
        self.title("Convertisseur de documents")
        self.geometry("700x600")
        self.resizable(False, False)

        self.input_file = None

        self.create_history_file()

        # ===== TITRE =====
        ttk.Label(
            self,
            text="Convertisseur de documents",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        # ===== MENU =====
        ttk.Label(self, text="Type de conversion").pack()

        self.conversion_var = ttk.StringVar()
        self.conversion_menu = ttk.Combobox(
            self,
            textvariable=self.conversion_var,
            state="readonly",
            width=42
        )
        self.conversion_menu["values"] = (
            "Excel → CSV",
            "CSV → Excel",
            "Word → PDF",
            "Image → PDF",
            "CSV → PDF"
        )
        self.conversion_menu.current(0)
        self.conversion_menu.pack(pady=10)

        # ===== DRAG & DROP =====
        self.drop_zone = ttk.Label(
            self,
            text="Glissez-déposez un fichier ici\nou cliquez pour sélectionner",
            relief="ridge",
            padding=30
        )
        self.drop_zone.pack(pady=15, padx=20, fill="x")

        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind("<<Drop>>", self.on_drop)
        self.drop_zone.bind("<Button-1>", self.select_file)

        # ===== BOUTON =====
        ttk.Button(
            self,
            text="Lancer la conversion",
            bootstyle=SUCCESS,
            command=self.start_conversion
        ).pack(pady=10)

        # ===== PROGRESS =====
        self.progress = ttk.Progressbar(
            self,
            mode="indeterminate",
            bootstyle=INFO,
            length=350
        )
        self.progress.pack(pady=10)

        # ===== HISTORIQUE =====
        ttk.Label(
            self,
            text="Historique des conversions",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=10)

        self.history_table = ttk.Treeview(
            self,
            columns=("date", "type", "file"),
            show="headings",
            height=8
        )

        self.history_table.heading("date", text="Date")
        self.history_table.heading("type", text="Conversion")
        self.history_table.heading("file", text="Fichier")

        self.history_table.column("date", width=150)
        self.history_table.column("type", width=120)
        self.history_table.column("file", width=300)

        self.history_table.pack(padx=20, fill="x")

        self.load_history()

        # ===== FOOTER =====
        ttk.Label(
            self,
            text="© Convertisseur Tkinter",
            font=("Segoe UI", 9)
        ).pack(side=BOTTOM, pady=10)

    # ================= HISTORIQUE =================
    def create_history_file(self):
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "conversion", "file"])

    def add_to_history(self, conversion, filename):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([date, conversion, filename])

        self.history_table.insert("", "end", values=(date, conversion, filename))

    def load_history(self):
        self.history_table.delete(*self.history_table.get_children())

        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.history_table.insert(
                    "",
                    "end",
                    values=(row["date"], row["conversion"], row["file"])
                )

    # ================= DRAG & DROP =================
    def on_drop(self, event):
        self.input_file = event.data.strip("{}")
        self.drop_zone.config(text=os.path.basename(self.input_file))

    def select_file(self, event=None):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.input_file = file_path
            self.drop_zone.config(text=os.path.basename(file_path))

    # ================= THREAD =================
    def start_conversion(self):
        if not self.input_file:
            messagebox.showerror("Erreur", "Aucun fichier sélectionné")
            return

        self.progress.start(10)
        threading.Thread(target=self.run_conversion, daemon=True).start()

    # ================= LOGIQUE =================
    def run_conversion(self):
        try:
            conversion = self.conversion_var.get()
            filename = os.path.basename(self.input_file)

            if "PDF" in conversion:
                output_file = filedialog.asksaveasfilename(defaultextension=".pdf")
            elif "CSV" in conversion:
                output_file = filedialog.asksaveasfilename(defaultextension=".csv")
            else:
                output_file = filedialog.asksaveasfilename(defaultextension=".xlsx")

            if not output_file:
                return

            time.sleep(0.4)

            if conversion == "Excel → CSV":
                excel_to_csv(self.input_file, output_file)
            elif conversion == "CSV → Excel":
                csv_to_excel(self.input_file, output_file)
            elif conversion == "Word → PDF":
                word_to_pdf(self.input_file, output_file)
            elif conversion == "Image → PDF":
                image_to_pdf(self.input_file, output_file)
            elif conversion == "CSV → PDF":
                csv_to_pdf(self.input_file, output_file)

            self.after(0, lambda: self.add_to_history(conversion, filename))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erreur", str(e)))
        finally:
            self.after(0, self.progress.stop)


if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()
