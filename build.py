"""
SuperSupText - Build Script
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil


def build():
    """Build the application executable."""
    print("=" * 60)
    print("Building SuperSupText")
    print("=" * 60)
    
    # Get the directory of this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=SuperSupText",
        "--windowed",  # No console window
        "--onefile",   # Single executable
        "--clean",     # Clean cache
        f"--distpath={os.path.join(base_dir, 'dist')}",
        f"--workpath={os.path.join(base_dir, 'build')}",
        f"--specpath={base_dir}",
        # Exclude conflicting Qt packages
        "--exclude-module=PyQt5",
        "--exclude-module=PyQt6",
        "--exclude-module=PyQt5.Qsci",
        "--exclude-module=PyQt6.Qsci",
        # Main script
        os.path.join(base_dir, "main.py"),
    ]
    
    print("\nRunning PyInstaller...")
    print(" ".join(cmd))
    print()
    
    result = subprocess.run(cmd, cwd=base_dir)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("Build successful!")
        print(f"Executable: {os.path.join(base_dir, 'dist', 'SuperSupText.exe')}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Build failed!")
        print("=" * 60)
        sys.exit(1)


def clean():
    """Clean build artifacts."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['SuperSupText.spec']
    
    for d in dirs_to_remove:
        path = os.path.join(base_dir, d)
        if os.path.exists(path):
            print(f"Removing {path}")
            shutil.rmtree(path)
    
    for f in files_to_remove:
        path = os.path.join(base_dir, f)
        if os.path.exists(path):
            print(f"Removing {path}")
            os.remove(path)
    
    print("Clean complete!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean()
    else:
        build()
