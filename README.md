# Laptop Audit

## Deskripsi Proyek

**Laptop Audit** adalah aplikasi otomatis untuk audit aset laptop/PC perusahaan. Aplikasi ini menggantikan proses audit manual yang memakan waktu dan rentan kesalahan dengan solusi otomatis berbasis Python. Mendukung cross-platform (Windows, macOS, Linux) dan menyediakan GUI user-friendly untuk pengumpulan data hardware, software, serta kondisi fisik perangkat.

Aplikasi ini mengumpulkan data spesifikasi teknis secara otomatis menggunakan pustaka `psutil` dan memungkinkan input manual untuk informasi PIC, kode asset, dan penilaian kondisi fisik. Output berupa laporan PDF dan XLSX, dengan integrasi SharePoint untuk upload otomatis.

## Fitur Utama

- **Pengumpulan Data Otomatis**:
  - Spesifikasi hardware (CPU, RAM, Storage, Battery)
  - Informasi sistem (OS, Serial Number, Manufacturer)
  - Daftar software terinstall
  - Status keamanan (Firewall, Antivirus)

- **Input Manual**:
  - Informasi PIC (Person-in-Charge)
  - Kode Asset
  - Lama penggunaan
  - Penilaian kondisi fisik (Cover, Layar, Keyboard, dll.)
  - Upload/Capture foto sebagai bukti

- **GUI Modern**: Menggunakan CustomTkinter untuk antarmuka yang intuitif

- **Laporan Otomatis**:
  - PDF dengan layout profesional
  - XLSX untuk database-ready format

- **Integrasi SharePoint**: Upload laporan ke endpoint perusahaan via Microsoft Graph API

- **Cross-Platform**: Kompatibel dengan Windows, macOS, dan Linux

## Kebutuhan Sistem

- **Python**: 3.10 atau lebih baru
- **OS**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Dependensi**: Lihat `requirements.txt`

## Instalasi

1. **Clone atau Download Repository**:
   ```
   git clone https://github.com/username/laptop-audit.git
   cd laptop-audit
   ```

2. **Install Python Dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Konfigurasi (Opsional)**:
   - Edit `config.py` untuk pengaturan SharePoint atau parameter lainnya

## Penggunaan

1. **Jalankan Aplikasi**:
   ```
   python main.py
   ```

2. **Isi Form Input**:
   - Masukkan PIC, Kode Asset, Lama Dibawa, Jenis Asset
   - Nilai kondisi fisik perangkat
   - Upload foto bukti

3. **Scan Otomatis**: Klik tombol scan untuk mengumpulkan data hardware/software

4. **Generate Laporan**: Pilih format output (PDF/XLSX) dan generate laporan

5. **Upload ke SharePoint**: Jika dikonfigurasi, laporan akan diupload otomatis

## Struktur Proyek

```
laptop-audit/
├── main.py                 # Entry point aplikasi
├── config.py               # Konfigurasi aplikasi
├── requirements.txt        # Dependensi Python
├── laptop_audit.md         # Dokumentasi konsep proyek
├── reference_programs.md   # Script referensi (PowerShell)
├── collectors/             # Modul pengumpul data
│   ├── battery.py          # Info baterai
│   ├── hardware.py         # Spesifikasi hardware
│   ├── network.py          # Info jaringan
│   ├── security.py         # Status keamanan
│   ├── software.py         # Daftar software
│   └── system_info.py      # Info sistem umum
├── gui/                    # Antarmuka pengguna
│   ├── app.py              # Aplikasi utama GUI
│   ├── forms.py            # Form input
│   └── image_capture.py    # Capture/upload gambar
├── integrations/           # Integrasi eksternal
│   └── sharepoint.py       # Upload ke SharePoint
├── reports/                # Generator laporan
│   ├── pdf_report.py       # Laporan PDF
│   └── xlsx_report.py      # Laporan Excel
├── output/                 # Folder output laporan
└── assets/                 # Asset statis (gambar, dll.)
```

## Lisensi

Proyek ini menggunakan lisensi MIT. Lihat file `LICENSE` untuk detail lebih lanjut.

## Kontak

Untuk pertanyaan atau dukungan, silakan buat issue di repository GitHub atau hubungi tim development.

---

**Versi**: 1.0.0  
**Tanggal Rilis**: Maret 2026  
**Pengembang**: IT Support PT. Aino Indonesia