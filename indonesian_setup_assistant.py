#!/usr/bin/env python3
"""
Indonesian OCR Setup Assistant
Downloads language packs to temp folder and provides manual installation guide
"""

import os
import requests
import shutil
import subprocess
from pathlib import Path
import tempfile

def download_to_temp():
    """Download Indonesian language packs to temporary folder"""
    
    print("🇮🇩 Indonesian OCR Setup Assistant")
    print("=" * 50)
    print("Downloading language packs for lang='eng+ind' support...")
    print()
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="indonesian_ocr_"))
    print(f"📁 Download location: {temp_dir}")
    
    language_packs = {
        'ind.traineddata': 'https://github.com/tesseract-ocr/tessdata/raw/main/ind.traineddata',
        'msa.traineddata': 'https://github.com/tesseract-ocr/tessdata/raw/main/msa.traineddata'
    }
    
    downloaded_files = []
    
    for filename, url in language_packs.items():
        target_file = temp_dir / filename
        
        try:
            print(f"⬇️  Downloading {filename}...")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(target_file, 'wb') as f:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"   Progress: {percent:.1f}%", end='\r')
            
            print()
            print(f"✅ {filename} downloaded successfully")
            downloaded_files.append(target_file)
            
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
    
    return temp_dir, downloaded_files

def find_tesseract_tessdata():
    """Find Tesseract tessdata directory"""
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tessdata",
        r"C:\Program Files (x86)\Tesseract-OCR\tessdata", 
        r"C:\Users\{}\AppData\Local\Tesseract-OCR\tessdata".format(os.getenv('USERNAME')),
        r"C:\tools\tesseract\tessdata"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return Path(path)
    
    return None

def create_installation_guide(temp_dir, downloaded_files):
    """Create detailed installation guide"""
    
    tessdata_dir = find_tesseract_tessdata()
    
    guide = f"""
🇮🇩 INDONESIAN OCR INSTALLATION GUIDE
{'='*50}

FILES DOWNLOADED TO:
{temp_dir}

MANUAL INSTALLATION STEPS:
"""
    
    if tessdata_dir:
        guide += f"""
1. COPY FILES TO TESSERACT:
   Target Directory: {tessdata_dir}
   
   Copy these files:
"""
        for file_path in downloaded_files:
            guide += f"   - {file_path.name}\n"
        
        guide += f"""
2. COPY COMMAND (Run as Administrator):
   Option A - File Explorer:
   - Open: {temp_dir}
   - Select all .traineddata files
   - Copy and paste to: {tessdata_dir}
   
   Option B - Command Prompt (as Admin):
   copy "{temp_dir}\\*.traineddata" "{tessdata_dir}\\"
"""
    else:
        guide += f"""
1. FIND TESSERACT TESSDATA DIRECTORY:
   Common locations:
   - C:\\Program Files\\Tesseract-OCR\\tessdata\\
   - C:\\Program Files (x86)\\Tesseract-OCR\\tessdata\\
   
2. COPY FILES:
   Copy all .traineddata files from:
   {temp_dir}
   
   To your Tesseract tessdata directory
"""
    
    guide += f"""
3. VERIFY INSTALLATION:
   tesseract --list-langs
   
   Should show:
   ✅ eng (English)
   ✅ ind (Indonesian) 
   ✅ msa (Malay)
   ✅ osd (Orientation and script detection)

4. TEST ENG+IND COMBINATION:
   tesseract input.pdf output.txt -l eng+ind

5. USAGE IN MCP TOOLS:
   - process_pdf_smart(pdf_path, language='eng+ind')
   - perform_ocr(file_path, language='eng+ind')  
   - batch_process_pdfs(directory, language='eng+ind')

OPTIMAL LANGUAGE SETTINGS:
- Mixed documents: lang='eng+ind' (RECOMMENDED)
- Fallback: lang='eng' (English only)

AFTER INSTALLATION:
- Test with: python test_indonesian_support.py
- Check tools: python validate_tools.py
"""
    
    print(guide)
    
    # Save guide to file
    guide_file = temp_dir / "INSTALLATION_GUIDE.txt"
    try:
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
        print(f"\n📖 Installation guide saved: {guide_file}")
    except Exception as e:
        print(f"⚠️  Could not save guide file: {e}")

def main():
    """Main setup process"""
    
    try:
        # Download files
        temp_dir, downloaded_files = download_to_temp()
        
        if downloaded_files:
            print(f"\n✅ {len(downloaded_files)} language packs downloaded")
            
            # Create installation guide
            create_installation_guide(temp_dir, downloaded_files)
            
            print(f"\n🎯 NEXT STEPS:")
            print(f"1. Run Command Prompt as Administrator")
            print(f"2. Copy files from {temp_dir} to Tesseract tessdata folder")
            print(f"3. Verify with: tesseract --list-langs")
            print(f"4. Test with: python test_indonesian_support.py")
            
            # Keep temp directory
            print(f"\n📁 Files will remain in temp directory until reboot")
            print(f"   Location: {temp_dir}")
            
        else:
            print(f"\n❌ No files downloaded successfully")
            print(f"Manual download:")
            print(f"1. Go to: https://github.com/tesseract-ocr/tessdata")
            print(f"2. Download: ind.traineddata, msa.traineddata")
            print(f"3. Copy to Tesseract tessdata folder")
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")

if __name__ == "__main__":
    main()