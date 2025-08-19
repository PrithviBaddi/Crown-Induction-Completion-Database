# build_exe.py
# Run this script to create a standalone executable

import os
import sys

def create_executable():
    """Create a standalone executable using PyInstaller"""
    
    print("Creating standalone executable...")
    
    # Determine the correct separator for add-data based on OS
    import platform
    separator = ";" if platform.system() == "Windows" else ":"
    
    # PyInstaller command to create the executable
    command = [
        "pyinstaller",
        "--onefile",              # Single executable file
        "--windowed",             # No console window (for Windows)
        "--name=CrownEmirates_Admin",  # Name of the executable
        f"--add-data=public{separator}public",    # Include the public folder (logo)
        "--hidden-import=psycopg2",    # Make sure psycopg2 is included
        "main.py"
    ]
    
    # Join command and run
    cmd_string = " ".join(command)
    print(f"Running: {cmd_string}")
    
    result = os.system(cmd_string)
    
    if result == 0:
        print("\n✅ Executable created successfully!")
        print("📁 Find your executable in the 'dist' folder")
        print("📦 File: dist/CrownEmirates_Admin.exe")
        print("\n📋 Next steps:")
        print("1. Copy the .exe file to your dad's computer")
        print("2. Copy the .env file to the same folder as the .exe")
        print("3. Your dad can double-click the .exe to run the app")
    else:
        print("❌ Error creating executable")
        print("Make sure PyInstaller is installed: pip install pyinstaller")

if __name__ == "__main__":
    create_executable()