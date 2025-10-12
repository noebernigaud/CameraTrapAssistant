"""
Main entry point for DeepFaune application.
Supports both GUI and CLI modes.
"""
import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='DeepFaune Wildlife Detection and Classification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py                    # Launch modern GUI (default)
  python src/main.py --gui              # Launch modern GUI explicitly  
  python src/main.py --legacy-gui       # Launch legacy GUI
        """
    )
    
    parser.add_argument(
        '--gui', 
        action='store_true', 
        help='Launch modern GUI mode'
    )
    parser.add_argument(
        '--legacy-gui', 
        action='store_true', 
        help='Launch legacy GUI mode'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='DeepFaune 1.0.0'
    )
    
    # Parse arguments, defaulting to GUI if no args provided
    if len(sys.argv) == 1:
        # Default to modern GUI if no arguments
        try:
            from gui.main_window import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"Error importing GUI: {e}")
            print("Please ensure all dependencies are installed.")
            sys.exit(1)
    else:
        args = parser.parse_args()
        
        if args.gui or not args.legacy_gui:
            try:
                from gui.main_window import main as gui_main
                gui_main()
            except ImportError as e:
                print(f"Error importing modern GUI: {e}")
                sys.exit(1)
        elif args.legacy_gui:
            try:
                from gui.legacy_gui import main as legacy_main
                legacy_main()
            except ImportError as e:
                print(f"Error importing legacy GUI: {e}")
                sys.exit(1)

if __name__ == "__main__":
    main()