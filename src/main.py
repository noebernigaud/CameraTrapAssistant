"""
Main entry point for DeepFaune application.
Launches the GUI interface.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point - launches the GUI."""
    try:
        from gui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error importing GUI: {e}")
        print("Please ensure all dependencies are installed.")
        sys.exit(1)

if __name__ == "__main__":
    main()