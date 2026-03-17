"""
Integration: SharePoint — Upload file via Microsoft Graph API.
Menggunakan MSAL untuk authentication.
"""
import os
import requests
import msal
from config import (
    SHAREPOINT_TENANT_ID,
    SHAREPOINT_CLIENT_ID,
    SHAREPOINT_CLIENT_SECRET,
    SHAREPOINT_SITE_URL,
    SHAREPOINT_DRIVE_ID,
    SHAREPOINT_UPLOAD_FOLDER,
)


class SharePointUploader:
    """Upload files ke SharePoint document library via Microsoft Graph API."""

    GRAPH_BASE = "https://graph.microsoft.com/v1.0"

    def __init__(self):
        if not all([SHAREPOINT_TENANT_ID, SHAREPOINT_CLIENT_ID, SHAREPOINT_CLIENT_SECRET]):
            raise ValueError(
                "SharePoint credentials belum dikonfigurasi!\n"
                "Silakan isi SHAREPOINT_TENANT_ID, SHAREPOINT_CLIENT_ID, "
                "dan SHAREPOINT_CLIENT_SECRET di config.py"
            )

        self.authority = f"https://login.microsoftonline.com/{SHAREPOINT_TENANT_ID}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.access_token = None

        self._authenticate()

    def _authenticate(self):
        """Autentikasi via MSAL Client Credentials flow."""
        app = msal.ConfidentialClientApplication(
            SHAREPOINT_CLIENT_ID,
            authority=self.authority,
            client_credential=SHAREPOINT_CLIENT_SECRET,
        )

        result = app.acquire_token_for_client(scopes=self.scope)

        if "access_token" in result:
            self.access_token = result["access_token"]
        else:
            error = result.get("error_description", result.get("error", "Unknown error"))
            raise ConnectionError(f"Gagal autentikasi ke Microsoft Graph: {error}")

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
        }

    def _get_site_id(self) -> str:
        """Resolve SharePoint site URL ke site ID."""
        # Parse site URL: https://company.sharepoint.com/sites/SiteName
        # Graph API: /sites/{hostname}:/{server-relative-path}
        from urllib.parse import urlparse
        parsed = urlparse(SHAREPOINT_SITE_URL)
        hostname = parsed.netloc
        site_path = parsed.path.rstrip("/")

        url = f"{self.GRAPH_BASE}/sites/{hostname}:{site_path}"
        resp = requests.get(url, headers=self._get_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()["id"]

    def upload_file(self, file_path: str, folder: str = None):
        """
        Upload satu file ke SharePoint document library.

        Args:
            file_path: Path lokal file yang akan diupload
            folder: Subfolder tujuan (default: dari config)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

        folder = folder or SHAREPOINT_UPLOAD_FOLDER
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # Untuk file < 4MB, gunakan simple upload
        # Untuk file >= 4MB, perlu upload session (jarang untuk report)
        if file_size < 4 * 1024 * 1024:
            self._simple_upload(file_path, filename, folder)
        else:
            self._large_upload(file_path, filename, folder)

    def _simple_upload(self, file_path: str, filename: str, folder: str):
        """Upload file kecil (< 4MB) direct PUT."""
        if SHAREPOINT_DRIVE_ID:
            url = (
                f"{self.GRAPH_BASE}/drives/{SHAREPOINT_DRIVE_ID}"
                f"/root:/{folder}/{filename}:/content"
            )
        else:
            site_id = self._get_site_id()
            url = (
                f"{self.GRAPH_BASE}/sites/{site_id}/drive"
                f"/root:/{folder}/{filename}:/content"
            )

        headers = self._get_headers()
        headers["Content-Type"] = "application/octet-stream"

        with open(file_path, "rb") as f:
            resp = requests.put(url, headers=headers, data=f, timeout=60)

        resp.raise_for_status()
        return resp.json()

    def _large_upload(self, file_path: str, filename: str, folder: str):
        """Upload file besar (>= 4MB) via upload session."""
        if SHAREPOINT_DRIVE_ID:
            url = (
                f"{self.GRAPH_BASE}/drives/{SHAREPOINT_DRIVE_ID}"
                f"/root:/{folder}/{filename}:/createUploadSession"
            )
        else:
            site_id = self._get_site_id()
            url = (
                f"{self.GRAPH_BASE}/sites/{site_id}/drive"
                f"/root:/{folder}/{filename}:/createUploadSession"
            )

        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        resp = requests.post(url, headers=headers, json={}, timeout=30)
        resp.raise_for_status()
        upload_url = resp.json()["uploadUrl"]

        # Upload in chunks
        file_size = os.path.getsize(file_path)
        chunk_size = 10 * 1024 * 1024  # 10MB chunks

        with open(file_path, "rb") as f:
            start = 0
            while start < file_size:
                chunk = f.read(chunk_size)
                end = start + len(chunk) - 1

                chunk_headers = {
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                }

                resp = requests.put(
                    upload_url, headers=chunk_headers, data=chunk, timeout=120
                )
                resp.raise_for_status()
                start = end + 1

        return resp.json()
