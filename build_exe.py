"""
Build script to create a standalone executable for Hixs Browser
Run this script to generate HixsBrowser.exe
"""

import os
import sys
import subprocess
import shutil

def install_requirements():
    """Install required packages"""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])

def build_exe():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if logo exists
    logo_path = os.path.join(script_dir, "logo.jpeg")
    
    # PyInstaller command with all necessary options
    cmd = [
        "pyinstaller",
        "--name=HixsBrowser",
        "--windowed",
        "--onefile",
        "--add-data=logo.jpeg;.",
        "--add-data=privacy.html;.",
        "--add-data=dev.html;.",
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.QtWebEngineWidgets",
        "--hidden-import=PyQt5.QtWebEngineCore",
        "--hidden-import=PyQt5.QtNetwork",
        "--hidden-import=PyQt5.QtPrintSupport",
        "--collect-all=PyQt5",
        "--collect-all=PyQtWebEngine",
        "--noconfirm",
        "--clean",
    ]
    
    # Add the main script (using brave.py for more features)
    cmd.append("brave.py")
    
    # Run PyInstaller
    try:
        result = subprocess.run(cmd, cwd=script_dir, text=True)
        if result.returncode != 0:
            print(f"Build failed with return code: {result.returncode}")
            return False
    except Exception as e:
        print(f"Build failed with error: {e}")
        return False
    
    print("\n" + "="*50)
    print("Build complete!")
    print("="*50)
    print(f"\nExecutable created at: {os.path.join(script_dir, 'dist', 'HixsBrowser.exe')}")
    print("\nYou can now share HixsBrowser.exe with your friends!")
    print("They just need to run it - no installation required!")
    
    return True

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Install requirements
    install_requirements()
    
    # Build the exe
    success = build_exe()
    
    if success:
        # Keep window open
        input("\nPress Enter to exit...")
