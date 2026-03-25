"""
Konfigurasi global untuk Laptop Audit Application.
"""
import os
import sys

# ── App Info ──────────────────────────────────────────────
APP_TITLE = "Laptop Asset Audit"
APP_VERSION = "1.0.0"
REPORT_YEAR = "2026"

# ── Paths ─────────────────────────────────────────────────
# Deteksi PyInstaller: saat di-bundle, __file__ mengarah ke _internal/
# Output harus di sebelah executable, tapi assets bundled ada di _MEIPASS
if getattr(sys, 'frozen', False):
    # Dijalankan dari PyInstaller bundle (one-dir / one-file)
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
    # Assets yang di-bundle via --add-data ada di _MEIPASS (_internal/)
    _BUNDLE_DIR = getattr(sys, '_MEIPASS', BASE_DIR)
else:
    # Dijalankan langsung dari source (python main.py)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    _BUNDLE_DIR = BASE_DIR

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ASSETS_DIR = os.path.join(_BUNDLE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")

# Pastikan folder output ada (assets di-bundle oleh PyInstaller, tidak perlu dibuat)
os.makedirs(OUTPUT_DIR, exist_ok=True)
if not getattr(sys, 'frozen', False):
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
