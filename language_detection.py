#!/usr/bin/env python3
"""
OCR Language Detection and Management
Provides comprehensive OCR language support including Indonesian
"""

import subprocess
import os
import sys
from pathlib import Path

def get_installed_tesseract_languages():
    """Get actually installed Tesseract languages"""
    try:
        result = subprocess.run(['tesseract', '--list-langs'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # Skip the header line
            langs = [line.strip() for line in lines[1:] if line.strip()]
            return langs
        else:
            return ['eng']  # fallback
    except Exception:
        return ['eng']  # fallback

def get_comprehensive_language_list():
    """Get comprehensive list of available OCR languages with Indonesian priority"""
    
    # Priority languages for Indonesian users
    priority_languages = {
        'ind': 'Indonesian (Bahasa Indonesia)', # WAJIB!
        'eng': 'English',
        'msa': 'Malay (Bahasa Malaysia)',
        'jpn': 'Japanese',
        'kor': 'Korean',
        'chi_sim': 'Chinese Simplified',
        'chi_tra': 'Chinese Traditional',
        'tha': 'Thai',
        'vie': 'Vietnamese'
    }
    
    # Common European languages
    common_languages = {
        'spa': 'Spanish',
        'fra': 'French', 
        'deu': 'German',
        'ita': 'Italian',
        'por': 'Portuguese',
        'rus': 'Russian',
        'ara': 'Arabic',
        'hin': 'Hindi'
    }
    
    # Get actually installed languages
    installed = get_installed_tesseract_languages()
    
    # Build comprehensive response
    language_info = {
        'installed_languages': installed,
        'priority_languages': priority_languages,
        'common_languages': common_languages,
        'indonesian_support': {
            'code': 'ind',
            'name': 'Indonesian (Bahasa Indonesia)',
            'installed': 'ind' in installed,
            'required': True,  # WAJIB!
            'install_command': 'Install: apt-get install tesseract-ocr-ind (Linux) or download from GitHub tessdata'
        },
        'installation_guide': {
            'windows': 'Download tessdata files from: https://github.com/tesseract-ocr/tessdata',
            'linux': 'sudo apt-get install tesseract-ocr-ind tesseract-ocr-msa tesseract-ocr-jpn',
            'macos': 'brew install tesseract-lang'
        },
        'total_available': len(priority_languages) + len(common_languages)
    }
    
    return language_info

if __name__ == "__main__":
    print("🌐 OCR Languages Analysis")
    print("=" * 50)
    
    info = get_comprehensive_language_list()
    
    print(f"📋 Currently Installed: {', '.join(info['installed_languages'])}")
    print(f"🎯 Indonesian Support: {'✅ INSTALLED' if info['indonesian_support']['installed'] else '❌ NOT INSTALLED (REQUIRED!)'}")
    
    print(f"\n🌏 Priority Languages for Indonesian Users:")
    for code, name in info['priority_languages'].items():
        status = "✅" if code in info['installed_languages'] else "❌"
        print(f"  {status} {code}: {name}")
    
    print(f"\n🌍 Common International Languages:")
    for code, name in info['common_languages'].items():
        status = "✅" if code in info['installed_languages'] else "❌"
        print(f"  {status} {code}: {name}")
    
    if 'ind' not in info['installed_languages']:
        print(f"\n⚠️  INDONESIAN NOT INSTALLED!")
        print(f"   Install command: {info['indonesian_support']['install_command']}")
        print(f"   This is REQUIRED for Indonesian text processing!")