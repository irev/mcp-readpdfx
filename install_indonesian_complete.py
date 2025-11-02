#!/usr/bin/env python3
"""
Enhanced Indonesian OCR Installer
Comprehensive installer for Indonesian + English OCR support with eng+ind combination
"""

import os
import requests
import shutil
import subprocess
from pathlib import Path
import tempfile

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

def download_language_pack(url, filename, tessdata_dir):
    """Download a single language pack with progress"""
    try:
        target_file = tessdata_dir / filename
        
        if target_file.exists():
            print(f"✅ {filename} already exists")
            return True
            
        print(f"⬇️  Downloading {filename}...")
        
        # Create temp file first
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"   Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
            
            print()  # New line after progress
        
        # Move temp file to final location
        shutil.move(temp_file.name, target_file)
        print(f"✅ {filename} downloaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        # Clean up temp file if exists
        try:
            if 'temp_file' in locals():
                os.unlink(temp_file.name)
        except:
            pass
        return False

def install_indonesian_ocr_complete():
    """Complete Indonesian OCR installation for eng+ind usage"""
    
    print("🇮🇩 Enhanced Indonesian OCR Installer")
    print("=" * 50)
    print("Installing support for lang='eng+ind' combination")
    print()
    
    # Find Tesseract
    tesseract_path = get_tesseract_path()
    if not tesseract_path:
        print("❌ Tesseract installation not found!")
        print("Install Tesseract first: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    tessdata_dir = tesseract_path / "tessdata"
    if not tessdata_dir.exists():
        print(f"❌ Tessdata directory not found: {tessdata_dir}")
        return False
    
    print(f"📁 Tesseract found: {tesseract_path}")
    print(f"📁 Installing to: {tessdata_dir}")
    print()
    
    # Essential language packs for Indonesian + English
    language_packs = {
        'ind.traineddata': {
            'url': 'https://github.com/tesseract-ocr/tessdata/raw/main/ind.traineddata',
            'description': 'Indonesian (Bahasa Indonesia) - REQUIRED',
            'priority': 1
        },
        'msa.traineddata': {
            'url': 'https://github.com/tesseract-ocr/tessdata/raw/main/msa.traineddata', 
            'description': 'Malay (similar to Indonesian) - RECOMMENDED',
            'priority': 2
        }
    }
    
    success_count = 0
    total_packs = len(language_packs)
    
    print("📦 Downloading language packs...")
    print()
    
    for filename, pack_info in language_packs.items():
        print(f"[{pack_info['priority']}/{total_packs}] {pack_info['description']}")
        
        if download_language_pack(pack_info['url'], filename, tessdata_dir):
            success_count += 1
        
        print()
    
    print(f"📊 Installation Summary: {success_count}/{total_packs} packs installed")
    
    return success_count > 0

def test_eng_ind_combination():
    """Test eng+ind language combination"""
    print("🧪 Testing eng+ind Language Combination")
    print("-" * 40)
    
    try:
        # Check available languages
        result = subprocess.run(['tesseract', '--list-langs'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            languages = result.stdout
            print("📋 Available languages:")
            for line in languages.split('\n'):
                if line.strip() and not line.startswith('List of'):
                    lang = line.strip()
                    status = "✅" if lang in ['eng', 'ind', 'msa'] else "📝"
                    print(f"   {status} {lang}")
        
        # Check Indonesian specifically
        if 'ind' in languages:
            print(f"\n🎉 Indonesian Language Pack: ✅ INSTALLED")
            print(f"🔧 Ready for lang='eng+ind' usage!")
            
            # Show usage examples
            print(f"\n📖 Usage Examples:")
            print(f"   Python: pytesseract.image_to_string(image, lang='eng+ind')")
            print(f"   CLI: tesseract input.pdf output.txt -l eng+ind")
            print(f"   MCP Tools: process_pdf_smart(pdf_path, language='eng+ind')")
            
            return True
        else:
            print(f"\n❌ Indonesian not found in language list")
            return False
            
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return False

def create_usage_guide():
    """Create usage guide for eng+ind combination"""
    
    guide_content = """# Indonesian OCR Usage Guide

## Language Combination: eng+ind

### Optimal Settings
- **Mixed Documents**: `lang='eng+ind'` (English + Indonesian) - RECOMMENDED
- **Fallback**: `lang='eng'` (English only)

### MCP Tools Usage
```python
# Smart PDF processing with Indonesian support
result = await process_pdf_smart(pdf_path, language='eng+ind')

# OCR with Indonesian language
ocr_result = await perform_ocr(file_path, language='eng+ind')

# Batch processing with Indonesian
batch_result = await batch_process_pdfs(directory, language='eng+ind')
```

### Python Direct Usage
```python
import pytesseract
from PIL import Image

# Load image
image = Image.open('indonesian_document.png')

# OCR with Indonesian + English
text = pytesseract.image_to_string(image, lang='eng+ind')
```

### Command Line Usage
```bash
# OCR PDF with Indonesian support
tesseract input.pdf output.txt -l eng+ind

# OCR image with Indonesian
tesseract document.png result.txt -l eng+ind
```

## Language Codes
- `ind`: Indonesian (Bahasa Indonesia)
- `eng`: English
- `msa`: Malay (Bahasa Malaysia)
- `eng+ind`: English + Indonesian (RECOMMENDED)

## Installation Verification
```bash
tesseract --list-langs
# Should show: eng, ind, msa, osd
```
"""
    
    guide_path = Path(__file__).parent / "INDONESIAN_OCR_GUIDE.md"
    
    try:
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        print(f"📖 Usage guide created: {guide_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create guide: {e}")
        return False

def main():
    """Main installation process"""
    
    print("Starting Indonesian OCR installation...")
    print()
    
    # Install language packs
    if install_indonesian_ocr_complete():
        print("✅ Language packs installation completed")
        print()
        
        # Test installation
        if test_eng_ind_combination():
            print("✅ eng+ind combination working!")
            print()
            
            # Create usage guide
            create_usage_guide()
            
            print("\n🎉 Installation Complete!")
            print("Indonesian OCR support ready for lang='eng+ind' usage")
            
        else:
            print("⚠️  Installation completed but testing failed")
            print("Check language packs manually")
    else:
        print("❌ Installation failed")
        print("\nManual installation steps:")
        print("1. Download: https://github.com/tesseract-ocr/tessdata/raw/main/ind.traineddata")
        print("2. Copy to: C:\\Program Files\\Tesseract-OCR\\tessdata\\")
        print("3. Verify: tesseract --list-langs")

if __name__ == "__main__":
    main()