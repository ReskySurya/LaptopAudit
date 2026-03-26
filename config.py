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

# ── Google Sheets Configuration ──────────────────────────
GOOGLE_SHEET_ID = "14nQTHNxepU-e298LrYLGVegAiG8guyBzkEfdjAXVBNk"
GOOGLE_CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
