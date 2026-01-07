import os
import threading
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

from config import load_config, save_config
from converters import (
    images_to_single_pdf,
    images_to_multiple_pdfs,
    csv_to_excel,
    excel_to_csv,
    word_to_pdf
)
from history import load_history


class ConvertorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Universal Convertor")
        self.root.geometry("950x620")

        self.config = load_config()
        self.files = []

        self.build_menu()
        self.build_ui()

    # ---------- MENU ----------
    def build_menu(self):
        menubar = tb.Menu(self.root)

        settings = tb.Menu(menubar, tearoff=0)
        settings.add_command(label="Dossier de sortie", command=self.choose_output_dir)

        history_menu = tb.Menu(menubar, tearoff=0)
        history_menu.add_command(label="Voir l’historique", command=self.show_history)

        menubar.add_cascade(label="Paramètres", menu=settings)
        menubar.add_cascade(label="Historique", menu=history_menu)

        self.root.config(menu=menubar)

    def choose_output_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.config["output_dir"] = folder
            save_config(self.config)
            messagebox.showinfo("Succès", "Dossier de sortie mis à jour")

    # ---------- UI ----------
    def build_ui(self):
        main = tb.Frame(self.root, padding=20)
        main.pack(fill=BOTH, expand=True)

        # --- Drag & Drop Zone ---
        self.drop_zone = tb.Label(
            main,
            text="📂 Glissez-déposez vos fichiers ici\nou cliquez sur “Ajouter des fichiers”",
            bootstyle="info",
            anchor=CENTER,
            padding=40
        )
        self.drop_zone.pack(fill=X, pady=15)

        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind("<<Drop>>", self.on_drop)

        # --- Fichiers sélectionnés ---
        self.files_label = tb.Label(
            main,
            text="Aucun fichier sélectionné",
            bootstyle="secondary",
            wraplength=800
        )
        self.files_label.pack(pady=10)

        tb.Button(
            main,
            text="Ajouter des fichiers",
            bootstyle="primary",
            command=self.select_files
        ).pack(pady=5)

        # --- Mode ---
        self.mode = tb.StringVar(value="multiple")

        mode_frame = tb.Labelframe(main, text="Mode de conversion")
        mode_frame.pack(fill=X, pady=10)

        tb.Radiobutton(
            mode_frame,
            text="Un PDF par fichier",
            variable=self.mode,
            value="multiple"
        ).pack(anchor=W, padx=10)

        tb.Radiobutton(
            mode_frame,
            text="Fusionner en un seul PDF",
            variable=self.mode,
            value="single"
        ).pack(anchor=W, padx=10)

        # --- Progression ---
        self.progress = tb.Progressbar(main, length=700)
        self.progress.pack(pady=20)

        tb.Button(
            main,
            text="Convertir",
            bootstyle="success",
            command=self.start_conversion
        ).pack(pady=10)

    # ---------- DRAG & DROP ----------
    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        self.files = list(files)
        self.files_label.config(text="\n".join(self.files))

    # ---------- LOGIC ----------
    def select_files(self):
        self.files = filedialog.askopenfilenames()
        if self.files:
            self.files_label.config(text="\n".join(self.files))

    def update_progress(self, current, total):
        percent = int((current / total) * 100)
        self.progress["value"] = percent
        self.root.update_idletasks()

    def start_conversion(self):
        if not self.files:
            messagebox.showerror("Erreur", "Aucun fichier sélectionné")
            return

        self.progress["value"] = 0
        threading.Thread(target=self.convert, daemon=True).start()

    def convert(self):
        output_dir = self.config["output_dir"]
        ext = os.path.splitext(self.files[0])[1].lower()

        try:
            if ext in [".jpg", ".jpeg", ".png"]:
                if self.mode.get() == "single":
                    images_to_single_pdf(
                        self.files,
                        os.path.join(output_dir, "fusion.pdf"),
                        self.update_progress
                    )
                else:
                    images_to_multiple_pdfs(
                        self.files,
                        output_dir,
                        self.update_progress
                    )

            elif ext == ".csv":
                csv_to_excel(self.files[0], os.path.join(output_dir, "output.xlsx"))

            elif ext in [".xls", ".xlsx"]:
                excel_to_csv(self.files[0], os.path.join(output_dir, "output.csv"))

            elif ext == ".docx":
                word_to_pdf(self.files[0], os.path.join(output_dir, "output.pdf"))

            else:
                messagebox.showerror("Erreur", "Format non supporté")
                return

            messagebox.showinfo("Succès", "Conversion terminée")

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ---------- HISTORIQUE ----------
    def show_history(self):
        history = load_history()

        window = tb.Toplevel(self.root)
        window.title("Historique des conversions")
        window.geometry("900x400")

        frame = tb.Frame(window, padding=10)
        frame.pack(fill=BOTH, expand=True)

        columns = ("date", "type", "files", "output")
        tree = tb.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col.capitalize())

        tree.pack(fill=BOTH, expand=True)

        for entry in history:
            tree.insert("", END, values=(
                entry.get("date"),
                entry.get("type"),
                entry.get("files"),
                entry.get("output")
            ))


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    style = tb.Style("flatly")
    app = ConvertorApp(root)
    root.mainloop()
