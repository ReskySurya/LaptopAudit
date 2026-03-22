"""
GUI: Image Capture — Upload foto fisik perangkat.
"""
import os
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk


class ImageCaptureFrame(ctk.CTkFrame):
    """Frame untuk upload/choose foto fisik sebagai bukti audit."""

    def __init__(self, master, on_continue_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.on_continue = on_continue_callback
        self.image_paths = []
        self.thumbnail_labels = []

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkLabel(
            self, text="📷 Upload Foto Bukti Fisik",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        header.pack(pady=(15, 5))

        hint = ctk.CTkLabel(
            self, text="Pilih foto fisik perangkat (Cover, Keyboard, Layar, dll).\n"
                       "Minimal 1 foto direkomendasikan.\n"
                       "Rename file foto dengan format: [JenisFoto] e.g. Cover.jpg, Keyboard.png",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        hint.pack(pady=(0, 15))

        # Tombol pilih file
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 10))

        choose_btn = ctk.CTkButton(
            btn_frame, text="📁 Pilih Gambar...",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40, width=200,
            command=self._choose_images,
        )
        choose_btn.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(
            btn_frame, text="🗑 Hapus Semua",
            font=ctk.CTkFont(size=14),
            height=40, width=150,
            fg_color="gray",
            command=self._clear_images,
        )
        clear_btn.pack(side="left", padx=5)

        # Info jumlah foto
        self.count_label = ctk.CTkLabel(
            self, text="Belum ada foto dipilih",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.count_label.pack(pady=(0, 10))

        # Tombol lanjut (Pack di bawah terlebih dahulu agar tidak tersembunyi)
        continue_btn = ctk.CTkButton(
            self, text="▶  Generate Laporan",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45, corner_radius=10,
            command=self._continue,
        )
        continue_btn.pack(side="bottom", pady=(5, 15), fill="x", padx=20)

        # Area preview (scrollable)
        self.preview_frame = ctk.CTkScrollableFrame(
            self, height=300, label_text="Preview Foto",
        )
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _choose_images(self):
        """Buka dialog file untuk memilih gambar."""
        filetypes = [
            ("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
            ("All Files", "*.*"),
        ]
        paths = filedialog.askopenfilenames(
            title="Pilih Foto Bukti Fisik",
            filetypes=filetypes,
        )
        if paths:
            self.image_paths.extend(paths)
            self._update_preview()

    def _clear_images(self):
        """Hapus semua foto."""
        self.image_paths.clear()
        self._update_preview()

    def _update_preview(self):
        """Update tampilan preview thumbnail."""
        # Hapus label lama
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        self.thumbnail_labels.clear()

        if not self.image_paths:
            self.count_label.configure(text="Belum ada foto dipilih")
            return

        self.count_label.configure(text=f"{len(self.image_paths)} foto dipilih")

        for i, path in enumerate(self.image_paths):
            row_frame = ctk.CTkFrame(self.preview_frame)
            row_frame.pack(fill="x", pady=3, padx=5)

            try:
                img = Image.open(path)
                img.thumbnail((120, 90))
                photo = ctk.CTkImage(light_image=img, size=img.size)
                img_label = ctk.CTkLabel(row_frame, image=photo, text="")
                img_label.image = photo  # keep reference
                img_label.pack(side="left", padx=(5, 10), pady=5)
            except Exception:
                err_label = ctk.CTkLabel(
                    row_frame, text="[Preview Error]",
                    text_color="red", width=120,
                )
                err_label.pack(side="left", padx=(5, 10), pady=5)

            # Filename label
            filename = os.path.basename(path)
            name_label = ctk.CTkLabel(
                row_frame, text=filename,
                font=ctk.CTkFont(size=12),
                anchor="w",
            )
            name_label.pack(side="left", fill="x", expand=True)

            # Remove button
            rm_btn = ctk.CTkButton(
                row_frame, text="✕", width=30, height=30,
                fg_color="red", hover_color="darkred",
                command=lambda idx=i: self._remove_image(idx),
            )
            rm_btn.pack(side="right", padx=5)

    def _remove_image(self, index: int):
        """Hapus satu foto dari list."""
        if 0 <= index < len(self.image_paths):
            self.image_paths.pop(index)
            self._update_preview()

    def _continue(self):
        """Lanjut ke generate report."""
        self.on_continue(list(self.image_paths))

    def get_image_paths(self) -> list:
        return list(self.image_paths)
