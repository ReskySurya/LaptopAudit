@echo off
chcp 65001 >nul
title Laptop Asset Audit

:: Jalankan PowerShell dengan bypass execution policy
:: -ExecutionPolicy Bypass : izinkan script ini jalan tanpa ubah setting global
:: -NoProfile              : lebih cepat, tidak load profil user
:: -File                   : jalankan file ps1 yang ada di folder yang sama

powershell.exe -ExecutionPolicy Bypass -NoProfile -NoExit -File "%~dp0audit_windows.ps1"

:: Jika PowerShell tidak tersedia (sangat jarang), tampilkan pesan
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Gagal menjalankan audit.
    echo  Pastikan Windows PowerShell terinstall di komputer ini.
    echo.
    pause
)
