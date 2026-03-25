"""
GUI: Main Application — Orchestrates the full audit flow (5 steps).
"""
import customtkinter as ctk
import threading
import datetime
import os

from config import APP_TITLE, APP_VERSION, OUTPUT_DIR
from gui.forms import InputForm
from gui.image_capture import ImageCaptureFrame
from collectors.system_info import get_system_info
from collectors.hardware import get_cpu_info, get_ram_info, get_storage_info
from collectors.battery import get_battery_info
from collectors.network import get_network_info
from collectors.software import get_installed_software
from collectors.security import get_security_status


class AuditApp(ctk.CTk):
    """Main application window — mengkoordinasikan seluruh flow audit."""

    def __init__(self):
        super().__init__()

        # ── Window Setup ──────────────────────────────
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.geometry("950x720")
        self.minsize(800, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── State ─────────────────────────────────────
        self.user_data = {}
        self.scan_data = {}
        self.image_paths = []
        self.saran_keluhan = ""
        self.current_step = 0

        # ── Layout ────────────────────────────────────
        self._build_header()
        self._build_step_indicator()

        # Container untuk konten yang berganti-ganti
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Mulai dari Step 1: Input Form
        self._show_step_1()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        title = ctk.CTkLabel(
            header_frame,
            text=f"  {APP_TITLE}",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.pack(side="left", padx=20, pady=10)

        ver = ctk.CTkLabel(
            header_frame,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        ver.pack(side="right", padx=20)

    def _build_step_indicator(self):
        self.step_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.step_frame.pack(fill="x", padx=15, pady=(10, 5))

        self.step_labels = []
        steps = [
            "1. Input",
            "2. Scan",
            "3. Foto",
            "4. Saran",
            "5. Report",
        ]

        for i, step_text in enumerate(steps):
            lbl = ctk.CTkLabel(
                self.step_frame,
                text=step_text,
                font=ctk.CTkFont(size=12, weight="bold" if i == 0 else "normal"),
                text_color="white" if i == 0 else "gray",
            )
            lbl.pack(side="left", padx=(0, 8))
            self.step_labels.append(lbl)

            if i < len(steps) - 1:
                arrow = ctk.CTkLabel(
                    self.step_frame, text=">>",
                    font=ctk.CTkFont(size=11), text_color="gray",
                )
                arrow.pack(side="left", padx=(0, 8))

    def _update_step(self, step: int):
        """Update visual step indicator."""
        self.current_step = step
        for i, lbl in enumerate(self.step_labels):
            if i < step:
                lbl.configure(text_color="#4CAF50", font=ctk.CTkFont(size=12, weight="bold"))
            elif i == step:
                lbl.configure(text_color="white", font=ctk.CTkFont(size=12, weight="bold"))
            else:
                lbl.configure(text_color="gray", font=ctk.CTkFont(size=12, weight="normal"))

    def _clear_content(self):
        """Hapus semua widget di content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ══════════════════════════════════════════════════
    # STEP 1: Input Form
    # ══════════════════════════════════════════════════
    def _show_step_1(self):
        self._clear_content()
        self._update_step(0)

        form = InputForm(
            self.content_frame,
            on_submit_callback=self._on_form_submitted,
        )
        form.pack(fill="both", expand=True, padx=10, pady=10)

    def _on_form_submitted(self, data: dict):
        self.user_data = data
        self._show_step_2()

    # ══════════════════════════════════════════════════
    # STEP 2: Hardware Scan
    # ══════════════════════════════════════════════════
    def _show_step_2(self):
        self._clear_content()
        self._update_step(1)

        self.scan_status_label = ctk.CTkLabel(
            self.content_frame,
            text="Sedang melakukan scan hardware & software...",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.scan_status_label.pack(pady=(50, 10))

        self.scan_progress = ctk.CTkProgressBar(self.content_frame, width=400)
        self.scan_progress.pack(pady=10)
        self.scan_progress.set(0)

        self.scan_detail_label = ctk.CTkLabel(
            self.content_frame,
            text="Menginisialisasi...",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.scan_detail_label.pack(pady=(0, 20))

        self.scan_log = ctk.CTkTextbox(
            self.content_frame, height=300,
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.scan_log.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        thread = threading.Thread(target=self._run_scan, daemon=True)
        thread.start()

    def _log(self, message: str):
        self.after(0, lambda: self._append_log(message))

    def _append_log(self, message: str):
        self.scan_log.insert("end", message + "\n")
        self.scan_log.see("end")

    def _run_scan(self):
        steps = [
            ("Mengambil informasi sistem...", self._collect_system),
            ("Mengambil data CPU...", self._collect_cpu),
            ("Mengambil data RAM...", self._collect_ram),
            ("Mengambil data storage...", self._collect_storage),
            ("Mengambil data baterai...", self._collect_battery),
            ("Mengambil data jaringan...", self._collect_network),
            ("Mengambil daftar software...", self._collect_software),
            ("Memeriksa status keamanan...", self._collect_security),
        ]

        for i, (msg, func) in enumerate(steps):
            progress = (i + 1) / len(steps)
            self.after(0, lambda m=msg: self.scan_detail_label.configure(text=m))
            self.after(0, lambda p=progress: self.scan_progress.set(p))
            self._log(f"[{i+1}/{len(steps)}] {msg}")

            try:
                func()
                self._log("  > Selesai")
            except Exception as e:
                self._log(f"  X Error: {e}")

        self.scan_data["tanggal"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.after(0, self._scan_complete)

    def _collect_system(self):
        self.scan_data.update(get_system_info())

    def _collect_cpu(self):
        self.scan_data.update(get_cpu_info())

    def _collect_ram(self):
        self.scan_data.update(get_ram_info())

    def _collect_storage(self):
        self.scan_data["storage"] = get_storage_info()

    def _collect_battery(self):
        self.scan_data["battery"] = get_battery_info()

    def _collect_network(self):
        self.scan_data["network"] = get_network_info()

    def _collect_software(self):
        self.scan_data["software_list"] = get_installed_software()

    def _collect_security(self):
        self.scan_data["security"] = get_security_status()

    def _scan_complete(self):
        self.scan_status_label.configure(text="Scan selesai!")
        self.scan_detail_label.configure(text="Semua data berhasil dikumpulkan.")
        self._log("\n=== SCAN SELESAI ===")

        next_btn = ctk.CTkButton(
            self.content_frame,
            text=">>  Lanjut ke Upload Foto",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45, corner_radius=10,
            command=self._show_step_3,
        )
        next_btn.pack(pady=(10, 15), padx=20, fill="x")

    # ══════════════════════════════════════════════════
    # STEP 3: Upload Foto
    # ══════════════════════════════════════════════════
    def _show_step_3(self):
        self._clear_content()
        self._update_step(2)

        img_capture = ImageCaptureFrame(
            self.content_frame,
            on_continue_callback=self._on_images_selected,
        )
        img_capture.pack(fill="both", expand=True, padx=10, pady=10)

    def _on_images_selected(self, paths: list):
        self.image_paths = paths
        self._show_step_4()

    # ══════════════════════════════════════════════════
    # STEP 4: Saran & Keluhan
    # ══════════════════════════════════════════════════
    def _show_step_4(self):
        self._clear_content()
        self._update_step(3)

        # Header
        header = ctk.CTkLabel(
            self.content_frame,
            text="Saran & Keluhan",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        header.pack(pady=(20, 5))

        hint = ctk.CTkLabel(
            self.content_frame,
            text="Tuliskan saran, keluhan, atau catatan terkait kondisi laptop/PC.\n"
                 "Bagian ini opsional — bisa dikosongkan jika tidak ada.",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        hint.pack(pady=(0, 15))

        # Text area
        self.saran_textbox = ctk.CTkTextbox(
            self.content_frame,
            height=350,
            font=ctk.CTkFont(family="Consolas", size=13),
            border_width=2,
            corner_radius=10,
        )
        self.saran_textbox.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        self.saran_textbox.insert("1.0", "")

        # Placeholder hint
        placeholder_label = ctk.CTkLabel(
            self.content_frame,
            text="Contoh: Keyboard beberapa tombol sudah tidak responsif, baterai cepat habis, dsb.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        )
        placeholder_label.pack(pady=(0, 10))

        # Tombol lanjut
        next_btn = ctk.CTkButton(
            self.content_frame,
            text=">>  Generate Laporan",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45, corner_radius=10,
            command=self._on_saran_submitted,
        )
        next_btn.pack(pady=(5, 15), fill="x", padx=30)

    def _on_saran_submitted(self):
        self.saran_keluhan = self.saran_textbox.get("1.0", "end-1c").strip()
        self._show_step_5()

    # ══════════════════════════════════════════════════
    # STEP 5: Generate Report
    # ══════════════════════════════════════════════════
    def _show_step_5(self):
        self._clear_content()
        self._update_step(4)

        status = ctk.CTkLabel(
            self.content_frame,
            text="Generating reports...",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        status.pack(pady=(50, 10))

        progress = ctk.CTkProgressBar(self.content_frame, width=400)
        progress.pack(pady=10)
        progress.set(0)

        detail = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        detail.pack(pady=(0, 20))

        thread = threading.Thread(
            target=self._generate_reports,
            args=(status, progress, detail),
            daemon=True,
        )
        thread.start()

    def _generate_reports(self, status_label, progress_bar, detail_label):
        """Generate PDF dan XLSX."""
        combined_data = {
            **self.user_data,
            **self.scan_data,
            "image_paths": self.image_paths,
            "saran_keluhan": self.saran_keluhan,
        }

        kode = self.user_data.get("kode_asset", "UNKNOWN")
        pic = self.user_data.get("pic_asset", "Unknown")
        year = datetime.datetime.now().strftime("%Y")

        # Ambil bagian LP-xxx dari kode asset (misal "HD/2022/08/JOG/LP-130" -> "LP-130")
        kode_short = kode.split("/")[-1].split("\\")[-1] if "/" in kode or "\\" in kode else kode
        # Sanitasi nama PIC untuk filename (spasi -> underscore, hapus karakter ilegal)
        pic_safe = pic.replace(" ", "_").replace("/", "_").replace("\\", "_")

        pdf_filename = f"Report_Audit_{kode_short}_{pic_safe}_{year}.pdf"
        xlsx_filename = f"Audit_{kode_short}_{pic_safe}_{year}.xlsx"

        pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
        xlsx_path = os.path.join(OUTPUT_DIR, xlsx_filename)

        results = {"pdf": None, "xlsx": None, "errors": []}

        # Step 1: PDF
        self.after(0, lambda: detail_label.configure(text="Membuat laporan PDF..."))
        self.after(0, lambda: progress_bar.set(0.3))
        try:
            from reports.pdf_report import generate_pdf
            generate_pdf(combined_data, pdf_path)
            results["pdf"] = pdf_path
        except Exception as e:
            results["errors"].append(f"PDF Error: {e}")

        # Step 2: XLSX
        self.after(0, lambda: detail_label.configure(text="Membuat spreadsheet XLSX..."))
        self.after(0, lambda: progress_bar.set(0.7))
        try:
            from reports.xlsx_report import generate_xlsx
            generate_xlsx(combined_data, xlsx_path)
            results["xlsx"] = xlsx_path
        except Exception as e:
            results["errors"].append(f"XLSX Error: {e}")

        self.after(0, lambda: progress_bar.set(1.0))
        self.after(0, lambda: self._show_results(results))

    def _show_results(self, results: dict):
        """Tampilkan halaman hasil akhir."""
        self._clear_content()

        header = ctk.CTkLabel(
            self.content_frame,
            text="Audit Selesai!",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#4CAF50",
        )
        header.pack(pady=(40, 20))

        if results["pdf"]:
            self._add_result_row("PDF Report", results["pdf"])
        if results["xlsx"]:
            self._add_result_row("Excel Spreadsheet", results["xlsx"])

        if results["errors"]:
            for err in results["errors"]:
                err_label = ctk.CTkLabel(
                    self.content_frame,
                    text=f"WARNING: {err}",
                    text_color="orange",
                    font=ctk.CTkFont(size=13),
                )
                err_label.pack(pady=3)

        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(pady=(30, 10))

        open_folder_btn = ctk.CTkButton(
            btn_frame, text="Buka Folder Output",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40, width=200,
            command=self._open_output_folder,
        )
        open_folder_btn.pack(side="left", padx=10)

        upload_btn = ctk.CTkButton(
            btn_frame, text="Upload ke SharePoint",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40, width=220,
            command=lambda: self._upload_sharepoint(results),
        )
        upload_btn.pack(side="left", padx=10)

        new_btn = ctk.CTkButton(
            btn_frame, text="Audit Baru",
            font=ctk.CTkFont(size=14),
            height=40, width=150,
            fg_color="gray",
            command=self._reset,
        )
        new_btn.pack(side="left", padx=10)

        self.sp_status = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=ctk.CTkFont(size=13),
        )
        self.sp_status.pack(pady=(10, 0))

    def _add_result_row(self, label: str, path: str):
        row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        row.pack(fill="x", padx=40, pady=3)
        ctk.CTkLabel(
            row, text=label,
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            row, text=os.path.basename(path),
            font=ctk.CTkFont(size=13), text_color="gray", anchor="e",
        ).pack(side="right")

    def _upload_sharepoint(self, results: dict):
        self.sp_status.configure(text="Uploading ke SharePoint...", text_color="yellow")

        def _do_upload():
            try:
                from integrations.sharepoint import SharePointUploader
                uploader = SharePointUploader()

                files_to_upload = []
                if results.get("pdf"):
                    files_to_upload.append(results["pdf"])
                if results.get("xlsx"):
                    files_to_upload.append(results["xlsx"])

                for fpath in files_to_upload:
                    uploader.upload_file(fpath)

                self.after(0, lambda: self.sp_status.configure(
                    text="Berhasil upload ke SharePoint!", text_color="#4CAF50"
                ))
            except Exception as e:
                self.after(0, lambda: self.sp_status.configure(
                    text=f"SharePoint Error: {e}", text_color="orange"
                ))

        thread = threading.Thread(target=_do_upload, daemon=True)
        thread.start()

    def _open_output_folder(self):
        """Buka folder output di file manager (cross-platform)."""
        import subprocess as sp
        import sys as _sys

        folder = OUTPUT_DIR
        try:
            if _sys.platform == "win32":
                os.startfile(folder)
            elif _sys.platform == "darwin":
                sp.Popen(["open", folder])
            else:
                # Linux: xdg-open
                sp.Popen(["xdg-open", folder])
        except Exception:
            pass

    def _reset(self):
        self.user_data = {}
        self.scan_data = {}
        self.image_paths = []
        self.saran_keluhan = ""
        self._show_step_1()
