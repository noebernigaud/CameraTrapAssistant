# DeepFaune - Wildlife Detection System

A comprehensive wildlife detection and classification system for camera trap images.

## Project Structure

```
DeepFaune/
├── src/                           # Main source code
│   ├── main.py                    # Application entry point
│   ├── core/                      # Core business logic
│   │   ├── prediction/            # AI prediction modules
│   │   ├── file_operations/       # File handling
│   │   ├── stats/                 # Statistics generation
│   │   └── run.py                 # Main processing logic
│   ├── gui/                       # GUI components
│   │   ├── main_window.py         # Main GUI interface
│   │   └── utils/                 # GUI utilities
│   ├── models/                    # AI models and weights
│   │   └── weights/               # Model weight files
│   ├── utils/                     # Utility modules
│   │   ├── resource_manager.py    # Resource path management
│   │   └── time_utils/            # Time/date utilities
│   └── config/                    # Configuration management
├── resources/                     # Static resources
│   ├── icons/                     # Application icons
│   ├── tools/                     # External tools (exiftool)
│   └── config/                    # Configuration files
├── build/                         # Build artifacts
│   ├── spec_files/                # PyInstaller spec files
│   └── dist/                      # Output executables
├── scripts/                       # Build and utility scripts
│   └── build_exe.py               # Executable build script
├── requirements/                  # Split requirements
│   ├── base.txt                   # Core dependencies
│   ├── gui.txt                    # GUI dependencies
│   └── build.txt                  # Build dependencies
├── pyproject.toml                 # Modern Python project config
└── README.md                      # This file
```

## Installation

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/noebernigaud/CameraTrapAssistant.git
cd CameraTrapAssistant/software
```

2. Install dependencies:
```bash
# For GUI version
pip install -r requirements/gui.txt

# For building executables
pip install -r requirements/build.txt
```

### Usage

#### Running the Application

```bash
# Run the application (GUI only)
python src/main.py
```

#### Building Executable

```bash
# Run the build script
python scripts/build_exe.py
```

The executable will be created in `build/dist/DeepFaune.exe`.

## Key Benefits of New Structure

1. **Clean Module Structure**: All imports are now predictable and organized
2. **Resource Management**: Handles paths correctly in both development and executable
3. **Single Entry Point**: `src/main.py` provides unified access to all modes
4. **Executable Ready**: Properly configured for PyInstaller packaging
5. **Modern Python**: Uses `pyproject.toml` and modern packaging standards
6. **Modular Design**: Easy to maintain, test, and extend

## Development

### Project Configuration

The project uses modern Python packaging with `pyproject.toml`:
- Metadata and dependencies managed in one place
- Supports optional dependencies for different features
- Ready for PyPI distribution if needed

### Resource Management

The `utils/resource_manager.py` module handles file paths that work both in:
- Development environment (direct file access)
- PyInstaller executable (bundled resources)

### Build Process

1. PyInstaller reads `build/spec_files/main.spec`
2. Bundles source code, resources, and dependencies
3. Creates single executable in `build/dist/`
4. Includes all necessary icons, tools, and model weights

## License

This software is governed by the CeCILL license under French law.