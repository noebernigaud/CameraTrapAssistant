# CameraTrap Assistant - Wildlife Detection System

A comprehensive wildlife detection and classification system for camera trap images.

## Quick Start

**Windows Users**: 
1. First time: Run `scripts\updater.bat` to download the latest version
2. Then run: `CameraTrapAssistant_windows_launcher.bat` for automatic setup and launch
3. Subsequent runs: Just use `CameraTrapAssistant_windows_launcher.bat`

**Manual Update**: Run `scripts\updater.bat` anytime to check for and install updates

## Project Structure

```
software/
├── CameraTrapAssistant_windows_launcher.bat # 🆕 Main Windows launcher
├── scripts/                                 # 🆕 Modular scripts
│   ├── installer.bat                       # Python & dependencies installer
│   ├── launcher.bat                        # Application launcher
│   ├── updater.bat                         # GitHub update checker
│   └── installer_files_utils/              # Installer-generated files
│       ├── .installed                      # Installation marker
│       └── CameraTrapAssistant_installer.log # Installation log
└── CameraTrapAssistant/                     # Main application
    ├── src/                                 # Main source code
    │   ├── main.py                         # Application entry point
    │   ├── core/                           # Core business logic
    │   ├── gui/                            # GUI components
    │   ├── models/                         # AI models and weights
    │   ├── utils/                          # Utility modules
    │   └── config/                         # Configuration management
    ├── resources/                          # Static resources
    │   ├── icons/                          # Application icons
    │   ├── tools/                          # External tools (exiftool)
    │   └── config/                         # Configuration files
    ├── requirements.txt                    # Python dependencies
    └── version.json                        # Version information
```

## Installation & Usage

### Windows (Recommended)
1. **First time**: Run `scripts\updater.bat` to download the application
2. **Launch**: Run `CameraTrapAssistant_windows_launcher.bat` for automatic setup and launch
3. **Updates**: Run `scripts\updater.bat` anytime to check for updates

### Manual Installation
```bash
git clone https://github.com/noebernigaud/CameraTrapAssistant.git
cd CameraTrapAssistant/software/CameraTrapAssistant
pip install -r requirements.txt
python src/main.py
```

## Auto-Update System

The modular script system provides:
- **`scripts\updater.bat`**: Checks GitHub releases and downloads updates
- **`scripts\installer.bat`**: Installs Python, pip, and dependencies
- **`scripts\launcher.bat`**: Launches the application
- **Main launcher**: Orchestrates the process automatically

### Script Details

- **Updater**: Downloads from GitHub, backs up current version, installs updates
- **Installer**: Handles Python installation and dependency management  
- **Launcher**: Simple application launcher with version display
- **Main Launcher**: Checks installation status and runs appropriate scripts

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