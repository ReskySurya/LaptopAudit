"""
Report: Google Sheets — Append data audit ke spreadsheet terpusat.
Menggunakan gspread + Google Service Account.
"""
import gspread
from google.oauth2.service_account import Credentials

from config import GOOGLE_SHEET_ID, GOOGLE_CREDENTIALS_FILE, KOMPONEN_FISIK

# Scopes yang dibutuhkan untuk read/write Google Sheets
_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# Header kolom — harus konsisten tiap append
HEADERS = [
    "Tanggal Audit",
    "PIC Asset",
    "Kode Asset",
    "Jenis Asset",
    "Lama Dibawa",
    "Hostname",
    "Username",
    "OS",
    "OS Build",
    "Vendor",
    "Model",
    "Serial Number",
    "CPU",
    "CPU Cores",
    "CPU Threads",
    "RAM (GB)",
    "IP Address",
    "MAC Address",
    "Battery (%)",
    "Charging Status",
    "Design Capacity",
    "Full Charge Capacity",
    "Battery Health",
    "Firewall Status",
    "Antivirus",
    "Antivirus Status",
]

# Tambah kolom kondisi fisik
for _komponen in KOMPONEN_FISIK:
    HEADERS.append(f"Kondisi {_komponen}")

HEADERS.append("Storage Info")
HEADERS.append("Jumlah Software Terinstall")
HEADERS.append("Saran / Keluhan")


def _build_row(data: dict) -> list:
    """Bangun satu baris data dari dict audit."""
    bat = data.get("battery", {})
    net = data.get("network", {})
    sec = data.get("security", {})
    matriks = data.get("matriks_fisik", {})

    # Storage sebagai string
    storage = data.get("storage", [])
    storage_str = "; ".join(
        f"{s.get('drive', '?')}: {s.get('total_gb', '?')}GB total, "
        f"{s.get('free_gb', '?')}GB free"
        for s in storage
    ) if storage else "N/A"

    row = [
        str(data.get("tanggal", "")),
        str(data.get("pic_asset", "")),
        str(data.get("kode_asset", "")),
        str(data.get("jenis_asset", "")),
        str(data.get("lama_dibawa", "")),
        str(data.get("hostname", "")),
        str(data.get("username", "")),
        str(data.get("os_name", "")),
        str(data.get("os_build", "")),
        str(data.get("vendor", "")),
        str(data.get("model", "")),
        str(data.get("serial_number", "")),
        str(data.get("cpu_name", "")),
        str(data.get("cpu_cores", "")),
        str(data.get("cpu_threads", "")),
        str(data.get("ram_total_gb", "")),
        ", ".join(net.get("ip_addresses", ["-"])),
        ", ".join(net.get("mac_addresses", ["-"])),
        str(bat.get("percent", "N/A")),
        str(bat.get("charging_status", "N/A")),
        str(bat.get("design_capacity_wh", "N/A")),
        str(bat.get("full_charge_capacity_wh", "N/A")),
        str(bat.get("health_percent", "N/A")),
        str(sec.get("firewall_status", "N/A")),
        str(sec.get("antivirus_name", "N/A")),
        str(sec.get("antivirus_status", "N/A")),
    ]

    # Kondisi fisik
    for komponen in KOMPONEN_FISIK:
        row.append(str(matriks.get(komponen, "-")))

    row.append(storage_str)
    row.append(str(len(data.get("software_list", []))))
    row.append(str(data.get("saran_keluhan", "")))

    return row


def _get_client() -> gspread.Client:
    """Buat gspread client dengan service account credentials."""
    creds = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE, scopes=_SCOPES
    )
    return gspread.authorize(creds)


def append_to_google_sheet(data: dict) -> tuple[bool, str]:
    """
    Append satu baris data audit ke Google Sheets master.

    Args:
        data: dict gabungan data manual + scan

    Returns:
        (success, message) — tuple untuk feedback ke GUI
    """
    try:
        client = _get_client()
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        worksheet = spreadsheet.sheet1

        # Cek apakah sheet kosong (belum ada header)
        existing = worksheet.get_all_values()

        if not existing:
            # Sheet kosong → tulis header dulu
            worksheet.append_row(HEADERS, value_input_option="RAW")

        # Append data row
        row = _build_row(data)
        worksheet.append_row(row, value_input_option="RAW")

        row_number = len(existing) + 2 if existing else 2
        return True, f"Data berhasil di-append ke Google Sheets (baris {row_number})"

    except FileNotFoundError:
        return False, (
            "File credentials.json tidak ditemukan!\n"
            "Pastikan file ada di folder root aplikasi."
        )
    except gspread.exceptions.SpreadsheetNotFound:
        return False, (
            "Spreadsheet tidak ditemukan!\n"
            "Pastikan spreadsheet sudah di-share ke email service account."
        )
    except gspread.exceptions.APIError as e:
        return False, f"Google Sheets API Error: {e}"
    except Exception as e:
        return False, f"Error append ke Google Sheets: {e}"
