import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.resource_manager import get_tools_path

def resource_path(relative_path):
    """Retourne le bon chemin même après compilation PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

EXIFTOOL_PATH = str(get_tools_path("exiftool/exiftool.exe"))

