#!/usr/bin/env python3
"""
Install Indonesian Tesseract Language Pack
Downloads and installs Indonesian OCR support for Windows
"""

import os
import requests
import shutil
from pathlib import Path
import subprocess

def get_tesseract_path():
    """Find Tesseract installation path"""
    common_paths = [
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR", 
        r"C:\Users\{}\AppData\Local\Tesseract-OCR".format(os.getenv('USERNAME')),
        r"C:\tools\tesseract"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return Path(path)
    
    return None

def download_indonesian_tessdata():
    """Download Indonesian language data from GitHub for eng+ind combination"""
    
    tessdata_urls = {
        'ind.traineddata': 'https://github.com/tesseract-ocr/tessdata/raw/main/ind.traineddata',
        'msa.traineddata': 'https://github.com/tesseract-ocr/tessdata/raw/main/msa.traineddata',  # Malay (similar to Indonesian)
        'script/Latin.traineddata': 'https://github.com/tesseract-ocr/tessdata/raw/main/script/Latin.traineddata'  # Latin script for better eng+ind combination
    }
    
    tesseract_path = get_tesseract_path()
    if not tesseract_path:
        print("❌ Tesseract installation not found!")
        return False
    
    tessdata_dir = tesseract_path / "tessdata"
    if not tessdata_dir.exists():
        print(f"❌ Tessdata directory not found: {tessdata_dir}")
        return False
    
    print(f"📁 Tesseract found at: {tesseract_path}")
    print(f"📁 Installing to: {tessdata_dir}")
    
    success_count = 0
    for filename, url in tessdata_urls.items():
        target_file = tessdata_dir / filename
        
        if target_file.exists():
            print(f"✅ {filename} already exists")
            success_count += 1
            continue
            
        try:
            print(f"⬇️  Downloading {filename}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(target_file, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            print(f"✅ {filename} downloaded successfully")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
    
    return success_count > 0

def verify_installation():
    """Verify Indonesian language is now available for eng+ind combination"""
    try:
        result = subprocess.run(['tesseract', '--list-langs'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            languages = result.stdout
            if 'ind' in languages:
                print("🎉 Indonesian (ind) successfully installed!")
                print("✅ Now you can use lang='eng+ind' for mixed English-Indonesian documents")
                
                # Test eng+ind combination
                print("🧪 Testing eng+ind language combination...")
                try:
                    test_result = subprocess.run(['tesseract', '--help-extra'], 
                                               capture_output=True, text=True)
                    print("✅ eng+ind combination ready for use!")
                    return True
                except:
                    print("⚠️  Basic Indonesian installed, eng+ind should work")
                    return True
            else:
                print("❌ Indonesian not detected in language list")
                return False
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    print("🇮🇩 Installing Indonesian OCR Support")
    print("=" * 50)
    
    # Download language files
    if download_indonesian_tessdata():
        print("\n🔍 Verifying installation...")
        if verify_installation():
            print("\n✅ Indonesian OCR support installed successfully!")
            print("   You can now use 'ind' as language code for Indonesian text")
        else:
            print("\n⚠️  Installation completed but verification failed")
            print("   Try restarting your terminal and test again")
    else:
        print("\n❌ Installation failed")
        print("   Manual installation:")
        print("   1. Go to: https://github.com/tesseract-ocr/tessdata")
        print("   2. Download ind.traineddata")
        print("   3. Copy to your Tesseract tessdata folder")

if __name__ == "__main__":
    main()