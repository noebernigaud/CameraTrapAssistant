"""
Resource management for both development and packaged executable.
"""
import sys
from pathlib import Path

def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    Args:
        relative_path: Path relative to resources directory
        
    Returns:
        Absolute path to the resource
    """
    if hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Running in development
        base_path = Path(__file__).parent.parent.parent / 'resources'
    
    return base_path / relative_path

def get_icon_path(icon_name: str) -> Path:
    """Get path to icon file."""
    return get_resource_path(f'icons/{icon_name}')

def get_model_path(model_name: str) -> Path:
    """Get path to model file."""
    return get_resource_path(f'models/weights/{model_name}')

def get_config_path(config_name: str) -> Path:
    """Get path to configuration file."""
    return get_resource_path(f'config/{config_name}')

def get_tools_path(tool_name: str) -> Path:
    """Get path to external tool."""
    return get_resource_path(f'tools/{tool_name}')

def ensure_resource_exists(resource_path: Path) -> bool:
    """
    Check if a resource exists and log warning if not.
    
    Args:
        resource_path: Path to check
        
    Returns:
        True if resource exists, False otherwise
    """
    exists = resource_path.exists()
    if not exists:
        import logging
        logging.warning(f"Resource not found: {resource_path}")
    return exists