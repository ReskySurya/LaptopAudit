# Project Concept Requirement (PCR)
## Audit Asset System: Cross-Platform Hardware & Software Auditor

| Informasi Proyek 
| Detail |
| **Nama Proyek** | Automated Laptop/PC Audit Script 2026 |
| **Versi** | 1.0.0 |
| **Bahasa Pemrograman** | Python 3.10+ |
| **Target OS** | Windows, macOS, Linux (Cross-Platform) |
| **Output** | PDF Report, XLSX Spreadsheet, SharePoint Upload |

---

## 1. Latar Belakang
Proyek ini bertujuan untuk menggantikan proses audit laptop/PC manual yang memakan waktu dan rentan terhadap kesalahan input. Program ini akan mengotomatisasi pengambilan spesifikasi teknis (hardware & software) dan mewajibkan bukti foto fisik untuk memvalidasi kondisi aset perusahaan.

## 2. Kriteria Data yang Dikumpulkan

### A. Data Input User (Manual)
1.  **PIC Asset**: Nama person-in-charge pengguna perangkat.
2.  **Kode Asset**: ID Inventaris perusahaan (contoh: LP-130).
3.  **Lama Dibawa**: Durasi penggunaan (Format: `X Tahun X Bulan`).
4.  **Jenis Asset**: Pilihan Radio/Dropdown (`Laptop` atau `PC`).
5.  **Matriks Fisik**: Penilaian kondisi (Baik/Rusak/Lecet) pada:
    * Cover
    * Back Cover
    * Engsel
    * Layar
    * Keyboard
6.  **Input Gambar**: Upload/Capture foto fisik sebagai bukti audit.

### B. Data Deteksi Otomatis (Script)
1.  **Waktu**: Hari/Tanggal pengecekan secara real-time.
2.  **Manufactur**: Merk/Vendor (contoh: Dell, Apple, Lenovo).
3.  **Serial Number**: S/N unik perangkat dari BIOS/Logic Board.
4.  **Matriks Spesifikasi**: 
    * **CPU**: Nama model, Core, dan Thread.
    * **RAM**: Total kapasitas dalam GB.
    * **OS**: Versi Sistem Operasi dan Build Number.
5.  **Matriks Battery**:
    * Design Capacity (Wh).
    * Max/Full Charge Capacity (Wh).
    * Battery Health (%).
6.  **Matriks Storage**:
    * Kapasitas total dan Free space.
    * Daftar aplikasi yang terinstall (Software List).
7.  **Matriks Security**: Status Firewall dan Antivirus yang aktif.

---

## 3. Alur Kerja Program (Workflow)

1.  **Initialization**: Program mendeteksi tipe OS (Windows/Darwin/Linux).
2.  **User Input Form**: User mengisi data manual (PIC, Kode Asset, dll).
3.  **Hardware/Software Scan**: 
    * Mengonversi logika Bash/PowerShell ke modul Python (`psutil`, `platform`, `subprocess`).
    * Pengambilan data baterai menggunakan `powercfg` (Win) atau `ioreg` (Mac).
4.  **Image Attachment**: User mengunggah foto fisik perangkat.
5.  **Report Generation**:
    * Menyusun data ke tabel **XLSX**.
    * Membuat layout **PDF** dengan judul: `Report Pemeriksaan Audit Laptop_{pic_name_user} 2026`.
6.  **SharePoint Integration**: Mengunggah file ke endpoint SharePoint perusahaan menggunakan API (Microsoft Graph).

---

## 4. Spesifikasi Output

### 4.1. Dokumen PDF
* **Header**: Judul Laporan & Logo Perusahaan.
* **Section 1**: Informasi Umum (PIC, Kode Asset, Tanggal).
* **Section 2**: Hasil Scan Hardware & Software.
* **Section 3**: Tabel Penilaian Fisik.
* **Section 4**: Lampiran Foto Bukti Fisik.

### 4.2. Dokumen Excel (XLSX)
* Satu baris data lengkap untuk keperluan database (Database-ready format).

---

## 5. Kebutuhan Library Python (Dependencies)
```python
# System Info
import psutil
import platform

# Data Handling & Export
import pandas as pd
from fpdf import FPDF
from openpyxl import Workbook

# Integration
import requests
from office365.sharepoint.client_context import ClientContext