"""
Konfigurasi global untuk Laptop Audit Application.
"""
import os

# ── App Info ──────────────────────────────────────────────
APP_TITLE = "Laptop Asset Audit"
APP_VERSION = "1.0.0"
REPORT_YEAR = "2026"

# ── Paths ─────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")

# Pastikan folder output ada
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# ── Matriks Fisik ─────────────────────────────────────────
KONDISI_OPTIONS = ["Baik", "Rusak", "Lecet"]
KOMPONEN_FISIK = ["Cover", "Back Cover", "Engsel", "Layar", "Keyboard"]
JENIS_ASSET_OPTIONS = ["Laptop", "PC"]

# ── SharePoint Configuration ─────────────────────────────
# Isi dengan credentials Azure AD Anda
SHAREPOINT_TENANT_ID = ""
SHAREPOINT_CLIENT_ID = ""
SHAREPOINT_CLIENT_SECRET = ""
SHAREPOINT_SITE_URL = ""  # contoh: "https://yourcompany.sharepoint.com/sites/IT-Assets"
SHAREPOINT_DRIVE_ID = ""  # ID drive/document library
SHAREPOINT_UPLOAD_FOLDER = "Audit Reports"  # Folder tujuan upload
