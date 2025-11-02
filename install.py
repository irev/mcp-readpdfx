"""
Production Installation Script for OCR PDF MCP Server v1.0.0
Automated installer that sets up the server across different MCP clients
"""

import json
import logging
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import version info
try:
    from version import __version__, get_version_info
except ImportError:
    __version__ = "1.0.0"
    def get_version_info():
        return {"version": "1.0.0"}

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class ProductionInstaller:
    """Production installer for OCR PDF MCP Server"""
    
    def __init__(self):
        self.version = __version__
        self.current_dir = Path(__file__).parent.absolute()
        self.server_path = self.current_dir / "server.py"
        self.config_template = self._get_server_config_template()
        
    def _get_server_config_template(self) -> Dict:
        """Get server configuration template"""
        python_exe = sys.executable
        
        # Use full path to Python executable for reliability
        return {
            "command": python_exe,
            "args": [str(self.server_path)],
            "env": {
                "TESSERACT_PATH": self._get_tesseract_path(),
                "PYTHONPATH": str(self.current_dir),
                "OCR_LANGUAGE": "eng+ind",
                "MAX_WORKERS": "4",
                "LOG_LEVEL": "INFO"
            }
        }
    
    def _get_tesseract_path(self) -> str:
        """Detect Tesseract installation path"""
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
            "/opt/homebrew/bin/tesseract"
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        # Try to find in PATH
        tesseract_exe = shutil.which("tesseract")
        if tesseract_exe:
            return tesseract_exe
        
        # Default fallback
        if os.name == 'nt':
            return r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        else:
            return "/usr/bin/tesseract"
    
    def check_prerequisites(self) -> Tuple[bool, List[str]]:
        """Check if all prerequisites are met"""
        issues = []
        
        logger.info("🔍 Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ required, got {sys.version}")
        else:
            logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check server file
        if not self.server_path.exists():
            issues.append(f"Server file not found: {self.server_path}")
        else:
            logger.info(f"✅ Server file: {self.server_path}")
        
        # Check Tesseract
        tesseract_path = self._get_tesseract_path()
        if not Path(tesseract_path).exists():
            issues.append(f"Tesseract not found. Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        else:
            logger.info(f"✅ Tesseract: {tesseract_path}")
        
        # Check Python packages
        required_packages = {
            'mcp': 'mcp',
            'PyMuPDF': 'fitz',
            'pytesseract': 'pytesseract', 
            'Pillow': 'PIL',
            'pdf2image': 'pdf2image'
        }
        missing_packages = []
        
        for package_name, import_name in required_packages.items():
            try:
                __import__(import_name)
                logger.info(f"✅ Package: {package_name}")
            except ImportError:
                missing_packages.append(package_name)
        
        if missing_packages:
            issues.append(f"Missing packages: {', '.join(missing_packages)}. Install with: pip install -r requirements.txt")
        
        return len(issues) == 0, issues
    
    def install_vscode_claude_dev(self) -> bool:
        """Install for VS Code Claude Dev/Cline"""
        logger.info("🔧 Installing for VS Code Claude Dev...")
        
        config_paths = [
            Path.home() / "AppData/Roaming/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json",
            Path.home() / ".vscode/cline_mcp_settings.json",
            Path.home() / "Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
        ]
        
        success = False
        for config_path in config_paths:
            if config_path.parent.exists() or config_path.name == "cline_mcp_settings.json":
                try:
                    config_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Load existing config
                    config = {"mcpServers": {}}
                    if config_path.exists():
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        config.setdefault("mcpServers", {})
                    
                    # Add our server
                    config["mcpServers"]["ocr-pdf-server"] = self.config_template
                    
                    # Write config
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2)
                    
                    logger.info(f"✅ Config written to: {config_path}")
                    success = True
                    break
                    
                except Exception as e:
                    logger.warning(f"Failed to write {config_path}: {e}")
        
        if not success:
            logger.warning("❌ VS Code config directory not found")
        
        return success
    
    def install_claude_desktop(self) -> bool:
        """Install for Claude Desktop"""
        logger.info("🔧 Installing for Claude Desktop...")
        
        # Platform-specific config paths
        if os.name == 'nt':  # Windows
            config_path = Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
        elif sys.platform == 'darwin':  # macOS
            config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        else:  # Linux
            config_path = Path.home() / ".config/Claude/claude_desktop_config.json"
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing config
            config = {"mcpServers": {}}
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                config.setdefault("mcpServers", {})
            
            # Add our server
            config["mcpServers"]["ocr-pdf-server"] = self.config_template
            
            # Write config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"✅ Config written to: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to configure Claude Desktop: {e}")
            return False
    
    def install_continue_dev(self) -> bool:
        """Install for Continue.dev"""
        logger.info("🔧 Installing for Continue.dev...")
        
        config_path = Path.home() / ".continue/config.json"
        
        if not config_path.exists():
            logger.warning("❌ Continue.dev config not found")
            return False
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Add mcpServers if not exists
            config.setdefault("mcpServers", [])
            
            # Remove existing ocr-pdf-server if exists
            config["mcpServers"] = [s for s in config["mcpServers"] if s.get("name") != "ocr-pdf-server"]
            
            # Add new config
            server_config = self.config_template.copy()
            server_config["name"] = "ocr-pdf-server"
            config["mcpServers"].append(server_config)
            
            # Write config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"✅ Config updated: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to configure Continue.dev: {e}")
            return False
    
    def create_standalone_config(self) -> bool:
        """Create standalone configuration file"""
        logger.info("🔧 Creating standalone config...")
        
        try:
            config = {
                "ocr_pdf_mcp_server": {
                    "version": self.version,
                    "mcpServers": {
                        "ocr-pdf-server": self.config_template
                    }
                }
            }
            
            config_path = self.current_dir / "mcp_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"✅ Standalone config created: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create standalone config: {e}")
            return False
    
    def install_all(self) -> Dict[str, bool]:
        """Install for all supported clients"""
        results = {}
        
        results["vscode"] = self.install_vscode_claude_dev()
        results["claude_desktop"] = self.install_claude_desktop()
        results["continue_dev"] = self.install_continue_dev()
        results["standalone"] = self.create_standalone_config()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print installation summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 INSTALLATION SUMMARY")
        logger.info("="*60)
        
        successful = sum(results.values())
        total = len(results)
        
        for client, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(f"{client.replace('_', ' ').title():<20} {status}")
        
        logger.info(f"\nResult: {successful}/{total} installations successful")
        
        if successful > 0:
            logger.info("\n🎉 Installation completed!")
            logger.info("\n📝 Next steps:")
            logger.info("1. Restart your MCP client applications")
            logger.info("2. Look for 'ocr-pdf-server' in available tools")
            logger.info("3. Test with: 'Analyze this PDF: /path/to/file.pdf'")
            logger.info(f"\n🔧 Server: {self.server_path}")
            logger.info(f"🔧 Version: {self.version}")
        else:
            logger.error("\n❌ All installations failed. Check logs above.")

def main():
    """Main installation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description=f"OCR PDF MCP Server v{__version__} Installer")
    parser.add_argument("--client", 
                       choices=["vscode", "claude", "continue", "standalone", "all"],
                       default="all",
                       help="Client to install for (default: all)")
    parser.add_argument("--check-only", action="store_true", 
                       help="Only check prerequisites")
    parser.add_argument("--force", action="store_true",
                       help="Skip prerequisite checks")
    
    args = parser.parse_args()
    
    print(f"🚀 OCR PDF MCP Server v{__version__} - Production Installer")
    print("="*60)
    
    installer = ProductionInstaller()
    
    # Check prerequisites
    if not args.force:
        prereq_ok, issues = installer.check_prerequisites()
        
        if not prereq_ok:
            logger.error("❌ Prerequisites not met:")
            for issue in issues:
                logger.error(f"  • {issue}")
            
            if not args.check_only:
                logger.error("\nPlease fix issues above before installation.")
                logger.info("Use --force to skip prerequisite checks.")
            
            return 1
        else:
            logger.info("✅ All prerequisites met!")
    
    if args.check_only:
        logger.info("\n✅ Prerequisite check completed successfully!")
        return 0
    
    # Perform installation
    if args.client == "vscode":
        results = {"vscode": installer.install_vscode_claude_dev()}
    elif args.client == "claude":
        results = {"claude_desktop": installer.install_claude_desktop()}
    elif args.client == "continue":
        results = {"continue_dev": installer.install_continue_dev()}
    elif args.client == "standalone":
        results = {"standalone": installer.create_standalone_config()}
    else:  # all
        results = installer.install_all()
    
    installer.print_summary(results)
    
    return 0 if any(results.values()) else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Installation failed: {e}")
        sys.exit(1)