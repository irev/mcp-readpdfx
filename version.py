"""
OCR PDF MCP Server Version Information
"""

__version__ = "1.0.1"
__author__ = "OCR PDF MCP Team"
__description__ = "MCP Server for PDF OCR and Text Extraction"
__license__ = "MIT"

# Version components
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 1
VERSION_BUILD = "stable"

# Build info
BUILD_DATE = "2025-11-02"
PYTHON_MIN_VERSION = "3.8"
TESSERACT_MIN_VERSION = "4.0"

def get_version_string():
    """Get formatted version string"""
    return f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}-{VERSION_BUILD}"

def get_version_info():
    """Get detailed version information"""
    return {
        "version": __version__,
        "build": VERSION_BUILD,
        "build_date": BUILD_DATE,
        "author": __author__,
        "description": __description__,
        "license": __license__,
        "python_min": PYTHON_MIN_VERSION,
        "tesseract_min": TESSERACT_MIN_VERSION
    }

def print_version():
    """Print version information"""
    info = get_version_info()
    print(f"OCR PDF MCP Server v{info['version']}")
    print(f"Build: {info['build']} ({info['build_date']})")
    print(f"Python: {info['python_min']}+ required")
    print(f"Tesseract: {info['tesseract_min']}+ required")
    print(f"License: {info['license']}")