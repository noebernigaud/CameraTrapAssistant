# CameraTrap Assistant - Modular Script System

## Overview

The Windows installation system has been refactored into modular, maintainable scripts with clear separation of concerns.

## Script Architecture

### 🚀 **Main Entry Point**
- **`CameraTrapAssistant_windows_launcher.bat`** - Main launcher at project root
  - Checks if application is installed
  - Runs installer if needed
  - Launches the application

### 📦 **Modular Scripts** (`scripts/` folder)

1. **`installer.bat`** - Dependencies & Environment Setup
   - Checks and installs Python 3.12
   - Checks and installs pip
   - Installs Python dependencies from requirements.txt
   - Creates installation marker

2. **`launcher.bat`** - Application Launcher
   - Reads version information
   - Launches the main application
   - Provides version display

3. **`updater.bat`** - Update Management
   - Checks GitHub for new releases
   - Downloads and extracts updates
   - Backs up current installation
   - Installs new version with rollback capability
   - Updates dependencies

### 📁 **File Organization**
- **`scripts/installer_files_utils/`** - Generated files
  - `.installed` - Installation marker (simple, no version tracking)
  - `CameraTrapAssistant_installer.log` - Comprehensive installation log

## Usage Workflows

### First Time Setup
```bash
# 1. Download the application
scripts\updater.bat

# 2. Install dependencies and launch
CameraTrapAssistant_windows_launcher.bat
```

### Regular Usage
```bash
# Just run the main launcher
CameraTrapAssistant_windows_launcher.bat
```

### Manual Updates
```bash
# Check for and install updates
scripts\updater.bat
```

## Key Benefits

### ✅ **Separation of Concerns**
- Each script has a single, clear purpose
- Easy to maintain and debug individual components
- Modular testing possible

### ✅ **Improved Organization**
- All installer files in dedicated directory
- Scripts folder contains all automation logic
- Clean project root with single entry point

### ✅ **Enhanced Maintainability**
- Individual scripts can be updated independently
- Clear logging and error handling per component
- Easier troubleshooting

### ✅ **Flexible Usage**
- Users can run individual scripts as needed
- Main launcher provides simple one-click experience
- Advanced users can customize individual components

## File Structure
```
software/
├── CameraTrapAssistant_windows_launcher.bat # Main entry point
├── scripts/
│   ├── installer.bat                       # Dependencies installer
│   ├── launcher.bat                        # App launcher
│   ├── updater.bat                         # Update manager
│   └── installer_files_utils/
│       ├── .installed                      # Installation marker
│       └── CameraTrapAssistant_installer.log # Logs
└── CameraTrapAssistant/                     # Application files
```

## Error Handling

Each script includes:
- Comprehensive error checking
- Detailed logging to `installer_files_utils/CameraTrapAssistant_installer.log`
- Graceful failure with user feedback
- Automatic rollback for update failures

## Future Extensibility

The modular design allows for easy addition of:
- Configuration management scripts
- Backup/restore functionality
- Development environment setup
- Testing automation
- Custom deployment scenarios