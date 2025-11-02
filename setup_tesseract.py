"""
Script untuk setup Tesseract OCR di Windows
"""

import os
import sys
import subprocess
import urllib.request
import tempfile
from pathlib import Path

def check_tesseract():
    """Cek apakah Tesseract sudah terinstall"""
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Tesseract-OCR\tesseract.exe"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"✅ Tesseract ditemukan di: {path}")
            return path
    
    print("❌ Tesseract tidak ditemukan di lokasi umum")
    return None

def download_tesseract():
    """Download dan instruksi install Tesseract"""
    print("📥 Download Tesseract OCR untuk Windows...")
    
    # URL download Tesseract untuk Windows
    tesseract_url = "https://github.com/UB-Mannheim/tesseract/wiki"
    
    print(f"""
🔧 INSTRUKSI INSTALL TESSERACT OCR:

1. Buka browser dan kunjungi: {tesseract_url}
2. Download versi terbaru Tesseract untuk Windows (file .exe)
3. Jalankan installer dan install ke lokasi default: C:\\Program Files\\Tesseract-OCR\\
4. Pastikan mencentang "Add to PATH" saat instalasi
5. Restart terminal setelah instalasi selesai

📋 ALTERNATIF MENGGUNAKAN CHOCOLATEY:
1. Install Chocolatey jika belum ada: https://chocolatey.org/install
2. Jalankan: choco install tesseract

📋 ALTERNATIF MENGGUNAKAN WINGET:
winget install --id UB-Mannheim.TesseractOCR

Setelah install, jalankan ulang test ini.
""")

def create_env_file(tesseract_path):
    """Buat file .env dengan path Tesseract"""
    env_content = f"""# Tesseract OCR Configuration
TESSERACT_PATH={tesseract_path}

# Server Configuration
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
"""
    
    env_file = Path(".env")
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ File .env dibuat dengan TESSERACT_PATH={tesseract_path}")

def test_tesseract(tesseract_path):
    """Test apakah Tesseract berjalan dengan baik"""
    try:
        result = subprocess.run([tesseract_path, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Tesseract berjalan dengan baik!")
            print(f"Version: {result.stdout.split('tesseract')[1].split()[0]}")
            return True
        else:
            print(f"❌ Error menjalankan Tesseract: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing Tesseract: {str(e)}")
        return False

def main():
    print("🔧 SETUP TESSERACT OCR")
    print("=" * 50)
    
    # Cek apakah Tesseract sudah ada
    tesseract_path = check_tesseract()
    
    if tesseract_path:
        # Test Tesseract
        if test_tesseract(tesseract_path):
            # Buat/update file .env
            create_env_file(tesseract_path)
            print("\n✅ Setup selesai! Tesseract siap digunakan.")
            return True
        else:
            print("❌ Tesseract ditemukan tapi tidak bisa dijalankan")
    
    # Jika Tesseract belum ada atau tidak bisa dijalankan
    download_tesseract()
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️ Harap install Tesseract terlebih dahulu sebelum menjalankan test OCR.")
        sys.exit(1)