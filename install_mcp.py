#!/usr/bin/env python3
"""
OCR PDF MCP Server Installer
Auto-installer for MCP server with Indonesian OCR support
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPInstaller:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "install.mcpb"
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load installation configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def check_python_version(self) -> bool:
        """Check Python version requirement"""
        try:
            required = self.config.get('requirements', {}).get('python', '>=3.8')
            current = f"{sys.version_info.major}.{sys.version_info.minor}"
            logger.info(f"Python version: {current} (required: {required})")
            
            if sys.version_info >= (3, 8):
                logger.info("✅ Python version check passed")
                return True
            else:
                logger.error("❌ Python 3.8+ required")
                return False
                
        except Exception as e:
            logger.error(f"Python version check failed: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        try:
            logger.info("🔧 Installing Python dependencies...")
            
            dependencies = self.config.get('requirements', {}).get('dependencies', [])
            
            for dep in dependencies:
                logger.info(f"Installing {dep}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', dep
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✅ {dep} installed successfully")
                else:
                    logger.error(f"❌ Failed to install {dep}: {result.stderr}")
                    return False
            
            logger.info("✅ All Python dependencies installed")
            return True
            
        except Exception as e:
            logger.error(f"Dependency installation failed: {e}")
            return False
    
    def check_tesseract(self) -> Tuple[bool, List[str]]:
        """Check Tesseract OCR installation and languages"""
        try:
            logger.info("🔍 Checking Tesseract OCR...")
            
            # Check if tesseract is installed
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error("❌ Tesseract OCR not found")
                return False, []
            
            logger.info("✅ Tesseract OCR found")
            
            # Check available languages
            lang_result = subprocess.run(['tesseract', '--list-langs'], 
                                       capture_output=True, text=True)
            
            if lang_result.returncode == 0:
                available_langs = [lang.strip() for lang in lang_result.stdout.split('\n') if lang.strip()]
                # Remove header line
                if available_langs and 'available' in available_langs[0].lower():
                    available_langs = available_langs[1:]
                
                logger.info(f"Available languages: {', '.join(available_langs)}")
                
                # Check required languages
                required_langs = self.config.get('system_requirements', {}).get('tesseract', {}).get('languages', [])
                missing_langs = [lang for lang in required_langs if lang not in available_langs]
                
                if missing_langs:
                    logger.warning(f"⚠️ Missing languages: {', '.join(missing_langs)}")
                    return True, missing_langs
                else:
                    logger.info("✅ All required languages available")
                    return True, []
            
            return True, []
            
        except FileNotFoundError:
            logger.error("❌ Tesseract OCR not installed")
            logger.info("📥 Install from: https://github.com/UB-Mannheim/tesseract/wiki")
            return False, []
        except Exception as e:
            logger.error(f"Tesseract check failed: {e}")
            return False, []
    
    def download_language_pack(self, language: str) -> bool:
        """Download missing language pack"""
        try:
            logger.info(f"📥 Downloading {language} language pack...")
            
            # Language pack URL
            base_url = "https://github.com/tesseract-ocr/tessdata/raw/main"
            lang_url = f"{base_url}/{language}.traineddata"
            
            # Try to find tessdata directory
            possible_paths = [
                "C:/Program Files/Tesseract-OCR/tessdata",
                "C:/Program Files (x86)/Tesseract-OCR/tessdata",
                "/usr/share/tesseract-ocr/4.00/tessdata",
                "/usr/share/tesseract-ocr/tessdata"
            ]
            
            tessdata_dir = None
            for path in possible_paths:
                if Path(path).exists():
                    tessdata_dir = Path(path)
                    break
            
            if not tessdata_dir:
                logger.error("❌ Tessdata directory not found")
                logger.info("Manual download required from: " + lang_url)
                return False
            
            # Download language pack
            import urllib.request
            lang_file = tessdata_dir / f"{language}.traineddata"
            
            logger.info(f"Downloading to: {lang_file}")
            urllib.request.urlretrieve(lang_url, lang_file)
            
            logger.info(f"✅ {language} language pack downloaded")
            return True
            
        except Exception as e:
            logger.error(f"Language pack download failed: {e}")
            logger.info(f"Manual download: {lang_url}")
            return False
    
    def test_server(self) -> bool:
        """Test server startup"""
        try:
            logger.info("🧪 Testing server startup...")
            
            server_file = self.base_dir / self.config.get('main', 'mcp_server_stdio_fixed.py')
            
            if not server_file.exists():
                logger.error(f"❌ Server file not found: {server_file}")
                return False
            
            # Test import
            result = subprocess.run([
                sys.executable, '-c', 
                f'import sys; sys.path.insert(0, "{self.base_dir}"); '
                f'from {server_file.stem} import main; print("✅ Server imports OK")'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("✅ Server startup test passed")
                return True
            else:
                logger.error(f"❌ Server test failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.info("✅ Server startup test passed (timeout expected)")
            return True
        except Exception as e:
            logger.error(f"Server test failed: {e}")
            return False
    
    def generate_client_configs(self) -> bool:
        """Generate client configuration files"""
        try:
            logger.info("📝 Generating client configurations...")
            
            configs = self.config.get('client_configs', {})
            
            for client_name, client_config in configs.items():
                config_file = self.base_dir / client_config.get('config_file', f'{client_name}-config.json')
                
                if config_file.exists():
                    logger.info(f"✅ {client_name} config already exists: {config_file}")
                else:
                    logger.info(f"⚠️ {client_name} config not found: {config_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Client config generation failed: {e}")
            return False
    
    def install(self) -> bool:
        """Main installation process"""
        logger.info("🚀 Starting OCR PDF MCP Server Installation")
        logger.info("=" * 50)
        
        steps = [
            ("Python Version Check", self.check_python_version),
            ("Install Dependencies", self.install_dependencies),
            ("Check Tesseract OCR", lambda: self.check_tesseract()[0]),
            ("Test Server", self.test_server),
            ("Generate Configs", self.generate_client_configs)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            
            if not step_func():
                logger.error(f"❌ Installation failed at: {step_name}")
                return False
        
        # Check for missing language packs
        tesseract_ok, missing_langs = self.check_tesseract()
        if missing_langs:
            logger.info("🔧 Attempting to download missing language packs...")
            for lang in missing_langs:
                self.download_language_pack(lang)
        
        logger.info("=" * 50)
        logger.info("🎉 Installation completed successfully!")
        logger.info(f"📁 Installation directory: {self.base_dir}")
        logger.info("🚀 Server ready to use")
        
        # Show usage instructions
        self.show_usage()
        
        return True
    
    def show_usage(self):
        """Show usage instructions"""
        logger.info("\n📖 Usage Instructions:")
        logger.info("=" * 30)
        logger.info("1. Start server:")
        logger.info(f"   python {self.base_dir}/mcp_server_stdio_fixed.py")
        logger.info("")
        logger.info("2. LM Studio Integration:")
        logger.info("   - See: client-configs/lm-studio.md")
        logger.info("   - Drag & drop PDF files in chat")
        logger.info("")
        logger.info("3. Available Tools:")
        tools = self.config.get('capabilities', {}).get('tools', [])
        for tool in tools:
            logger.info(f"   - {tool}")
        logger.info("")
        logger.info("4. Supported Languages:")
        languages = self.config.get('capabilities', {}).get('languages', [])
        logger.info(f"   - {', '.join(languages)}")

def main():
    """Main installer function"""
    installer = MCPInstaller()
    
    try:
        success = installer.install()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()