# CameraTrap Assistant - Wildlife Detection System

A comprehensive wildlife detection and classification system for camera trap images.

## Quick Start

**Windows Users**: Simply run `CameraTrapAssistant_windows.bat` - it will automatically:
- Check for updates from GitHub
- Install Python if needed
- Install dependencies
- Launch the application

## Project Structure

```
software/
├── CameraTrapAssistant_windows.bat # Windows installer/launcher
├── installer/                      # Installer-generated files
│   ├── .installed_X.X.X           # Installation markers
│   └── CameraTrapAssistant_installer.log # Installation log
└── CameraTrapAssistant/
    ├── src/                        # Main source code
    │   ├── main.py                 # Application entry point
    │   ├── core/                   # Core business logic
    │   ├── gui/                    # GUI components
    │   ├── models/                 # AI models and weights
    │   ├── utils/                  # Utility modules
    │   └── config/                 # Configuration management
    ├── resources/                  # Static resources
    │   ├── icons/                  # Application icons
    │   ├── tools/                  # External tools (exiftool)
    │   └── config/                 # Configuration files
    ├── requirements.txt            # Python dependencies
    └── version.json                # Version information
```

## Installation & Usage

### Windows (Recommended)
Run `CameraTrapAssistant_windows.bat` - handles everything automatically.

### Manual Installation
```bash
git clone https://github.com/noebernigaud/CameraTrapAssistant.git
cd CameraTrapAssistant/software/CameraTrapAssistant
pip install -r requirements.txt
python src/main.py
```

## Auto-Update System

The Windows installer automatically:
- Checks GitHub releases for newer versions
- Downloads and installs updates
- Backs up current installation
- Rolls back on failure

## Version Management

Update version in `CameraTrapAssistant/version.json`:
```json
{
    "version": "1.0.1",
    "build_date": "2025-10-18",
    "min_python_version": "3.8",
    "description": "CameraTrap Assistant - Wildlife camera trap image analysis tool",
    "github_repo": "noebernigaud/CameraTrapAssistant"
}
```

Create GitHub release with tag `v1.0.1` - the installer will detect it automatically.

## License

This software is governed by the CeCILL license under French law.