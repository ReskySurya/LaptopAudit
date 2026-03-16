╔══════════════════════════════════════════════════════════════╗
║              LAPTOP ASSET AUDIT — PANDUAN PAKAI              ║
╚══════════════════════════════════════════════════════════════╝

Sebelum mulai, pastikan semua file berikut ada dalam
SATU FOLDER yang sama di komputer Anda:

  ┌─────────────────────────────────────────────────────────────┐
  │  JALANKAN_AUDIT.bat   ← Yang Anda klik (Windows)            │
  │  audit_windows.ps1    ← Jangan dihapus                      │
  │  audit_unix.sh        ← Untuk macOS / Linux                 │
  │  laptop_audit.html    ← Untuk review hasil                  │
  │  README.txt           ← Panduan ini                         │
  └─────────────────────────────────────────────────────────────┘


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  WINDOWS — Cara Pakai
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Langkah 1
  Dobel klik file  JALANKAN_AUDIT.bat
  (bukan file .ps1)

Langkah 2
  Jika muncul kotak peringatan berjudul
  "Windows protected your PC" — klik "More info",
  lalu klik tombol "Run anyway".
  Ini normal dan aman.

Langkah 3
  Jendela hitam (Command Prompt) akan terbuka.
  Ketik Kode Asset laptop, lalu tekan Enter.
  Contoh:  LP-130

Langkah 4
  Ketik nama pengguna / PIC laptop, lalu tekan Enter.
  Contoh:  Budi Santoso

Langkah 5
  Tunggu beberapa detik — program otomatis mengumpulkan
  data laptop. Tidak perlu melakukan apa-apa.

Langkah 6
  Setelah selesai, dua hal akan terjadi otomatis:
  • File laporan (asset_LP-130.txt) tersimpan di folder
    yang sama dengan file JALANKAN_AUDIT.bat
  • Browser (Chrome/Edge) terbuka untuk review hasil

  Tekan Enter untuk menutup jendela hitam.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  macOS — Cara Pakai
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Langkah 1
  Buka aplikasi Terminal.
  (Tekan Command + Spasi, ketik "Terminal", Enter)

Langkah 2
  Seret folder tempat file audit berada ke jendela
  Terminal, lalu ketik "cd " (dengan spasi) sebelumnya.
  Contoh:  cd /Users/nama/Downloads/audit
  Tekan Enter.

Langkah 3
  Ketik perintah berikut lalu tekan Enter:
    bash audit_unix.sh

Langkah 4
  Ikuti langkah yang sama seperti Windows di atas
  (isi Kode Asset dan nama PIC).


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  LINUX — Cara Pakai
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Langkah 1
  Buka Terminal, masuk ke folder file audit:
    cd ~/Downloads/audit

Langkah 2
  Jalankan script:
    bash audit_unix.sh

  Jika data baterai tidak muncul, coba:
    sudo bash audit_unix.sh


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MELIHAT HASIL & EXPORT KE EXCEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Browser akan terbuka otomatis setelah audit selesai.
Jika tidak terbuka, ikuti langkah berikut:

Langkah 1
  Dobel klik file  laptop_audit.html
  (akan terbuka di browser Chrome atau Edge)

Langkah 2
  Seret file  asset_XX.txt  ke halaman browser tersebut.
  (file XX adalah kode asset yang tadi Anda isi)

Langkah 3
  Data laporan akan tampil otomatis di layar.
  Anda bisa melihat info sistem, baterai, dan
  daftar software yang terinstall.

Langkah 4 (opsional)
  Klik tombol "Export ke XLSX" untuk menyimpan laporan
  dalam format Excel (.xlsx).


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CATATAN PENTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✔  Semua data diproses di komputer Anda sendiri.
   Tidak ada data yang dikirim ke internet.

✔  File hasil (.txt) bisa dibuka dengan Notepad biasa.

✔  Jika ada laptop tanpa baterai (PC desktop),
   bagian baterai akan otomatis tertulis "Tidak ada baterai".

✔  Proses audit biasanya selesai dalam 10–30 detik.