"""
Laptop Asset Audit — Main Entry Point.
Jalankan: python main.py
"""
import sys
import os

# Pastikan project root ada di path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import AuditApp


def main():
    app = AuditApp()
    app.mainloop()


if __name__ == "__main__":
    main()
