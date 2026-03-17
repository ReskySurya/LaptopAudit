"""
GUI: Form Input — PIC, Kode Asset, Matriks Fisik, dll.
"""
import customtkinter as ctk
from config import KONDISI_OPTIONS, KOMPONEN_FISIK, JENIS_ASSET_OPTIONS


class InputForm(ctk.CTkScrollableFrame):
    """Frame berisi semua field input manual untuk audit."""

    def __init__(self, master, on_submit_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.on_submit = on_submit_callback
        self.entries = {}
        self.kondisi_vars = {}

        self._build_form()

    def _build_form(self):
        # ── Header ────────────────────────────────────
        header = ctk.CTkLabel(
            self, text="📋 Data Input Audit",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        header.pack(pady=(10, 20), anchor="w")

        # ── PIC Asset ────────────────────────────────
        self._add_label("Nama PIC Asset *")
        self.entries["pic_asset"] = self._add_entry("Masukkan nama PIC...")

        # ── Kode Asset ───────────────────────────────
        self._add_label("Kode Asset *")
        self.entries["kode_asset"] = self._add_entry("Contoh: LP-130")

        # ── Jenis Asset ──────────────────────────────
        self._add_label("Jenis Asset *")
        self.jenis_var = ctk.StringVar(value=JENIS_ASSET_OPTIONS[0])
        jenis_frame = ctk.CTkFrame(self, fg_color="transparent")
        jenis_frame.pack(fill="x", pady=(0, 15))
        for option in JENIS_ASSET_OPTIONS:
            rb = ctk.CTkRadioButton(
                jenis_frame, text=option,
                variable=self.jenis_var, value=option,
                font=ctk.CTkFont(size=14),
            )
            rb.pack(side="left", padx=(0, 30))

        # ── Lama Dibawa ──────────────────────────────
        self._add_label("Lama Dibawa *")
        lama_frame = ctk.CTkFrame(self, fg_color="transparent")
        lama_frame.pack(fill="x", pady=(0, 15))

        self.tahun_var = ctk.StringVar(value="0")
        ctk.CTkLabel(lama_frame, text="Tahun:", font=ctk.CTkFont(size=14)).pack(side="left")
        tahun_spin = ctk.CTkOptionMenu(
            lama_frame, variable=self.tahun_var,
            values=[str(i) for i in range(0, 16)],
            width=80,
        )
        tahun_spin.pack(side="left", padx=(5, 20))

        self.bulan_var = ctk.StringVar(value="0")
        ctk.CTkLabel(lama_frame, text="Bulan:", font=ctk.CTkFont(size=14)).pack(side="left")
        bulan_spin = ctk.CTkOptionMenu(
            lama_frame, variable=self.bulan_var,
            values=[str(i) for i in range(0, 12)],
            width=80,
        )
        bulan_spin.pack(side="left", padx=(5, 0))

        # ── Matriks Fisik ────────────────────────────
        self._add_label("Penilaian Kondisi Fisik *")

        fisik_frame = ctk.CTkFrame(self)
        fisik_frame.pack(fill="x", pady=(0, 15), padx=5)

        # Header row
        ctk.CTkLabel(
            fisik_frame, text="Komponen",
            font=ctk.CTkFont(size=13, weight="bold"), width=150, anchor="w"
        ).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(
            fisik_frame, text="Kondisi",
            font=ctk.CTkFont(size=13, weight="bold"), width=150, anchor="w"
        ).grid(row=0, column=1, padx=10, pady=8, sticky="w")

        for i, komponen in enumerate(KOMPONEN_FISIK, start=1):
            ctk.CTkLabel(
                fisik_frame, text=komponen,
                font=ctk.CTkFont(size=14), width=150, anchor="w"
            ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

            var = ctk.StringVar(value=KONDISI_OPTIONS[0])
            self.kondisi_vars[komponen] = var
            dropdown = ctk.CTkOptionMenu(
                fisik_frame, variable=var,
                values=KONDISI_OPTIONS, width=150,
            )
            dropdown.grid(row=i, column=1, padx=10, pady=5, sticky="w")

        # ── Error label ──────────────────────────────
        self.error_label = ctk.CTkLabel(
            self, text="", text_color="red",
            font=ctk.CTkFont(size=13),
        )
        self.error_label.pack(pady=(5, 0))

        # ── Submit Button ────────────────────────────
        submit_btn = ctk.CTkButton(
            self, text="▶  Lanjutkan ke Scan Hardware",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45, corner_radius=10,
            command=self._validate_and_submit,
        )
        submit_btn.pack(pady=(15, 10), fill="x", padx=20)

    def _add_label(self, text: str):
        label = ctk.CTkLabel(
            self, text=text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        label.pack(fill="x", pady=(10, 3))

    def _add_entry(self, placeholder: str) -> ctk.CTkEntry:
        entry = ctk.CTkEntry(
            self, placeholder_text=placeholder,
            font=ctk.CTkFont(size=14), height=38,
        )
        entry.pack(fill="x", pady=(0, 5))
        return entry

    def _validate_and_submit(self):
        """Validasi semua field wajib dan panggil callback."""
        pic = self.entries["pic_asset"].get().strip()
        kode = self.entries["kode_asset"].get().strip()

        if not pic:
            self.error_label.configure(text="⚠ Nama PIC Asset wajib diisi!")
            return
        if not kode:
            self.error_label.configure(text="⚠ Kode Asset wajib diisi!")
            return

        self.error_label.configure(text="")

        # Kumpulkan data
        lama = f"{self.tahun_var.get()} Tahun {self.bulan_var.get()} Bulan"

        matriks_fisik = {}
        for komponen, var in self.kondisi_vars.items():
            matriks_fisik[komponen] = var.get()

        data = {
            "pic_asset": pic,
            "kode_asset": kode,
            "jenis_asset": self.jenis_var.get(),
            "lama_dibawa": lama,
            "matriks_fisik": matriks_fisik,
        }

        self.on_submit(data)
