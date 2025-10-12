"""
Build script for creating DeepFaune executable.
"""
import subprocess
import sys
import shutil
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller."""
    project_root = Path(__file__).parent.parent
    spec_file = project_root / 'build' / 'spec_files' / 'main.spec'
    
    # Clean previous builds
    dist_dir = project_root / 'build' / 'dist'
    work_dir = project_root / 'build' / 'build'
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if work_dir.exists():
        shutil.rmtree(work_dir)
    
    # Run PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--workpath', str(work_dir),
        '--distpath', str(dist_dir),
        str(spec_file)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=project_root, check=True)
        print(f"Executable built successfully in {dist_dir}")
        
        # List contents of dist directory
        if dist_dir.exists():
            print(f"\nContents of {dist_dir}:")
            for item in dist_dir.iterdir():
                print(f"  {item.name}")
                
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = build_executable()
    if not success:
        sys.exit(1)