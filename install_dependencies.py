import sys
import subprocess
import os

def install_dependencies():
    """Install required dependencies for the product manager application."""
    print("Installing required dependencies...")
    
    # List of required packages
    required_packages = [
        "pandas",
        "xlsxwriter",
        "reportlab",
        "matplotlib",
        "python-barcode",
        "Pillow",
        "PyQt5"
    ]
    
    # Check if pip is available
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    except subprocess.CalledProcessError:
        print("Error: pip is not available. Please install pip first.")
        return False
    
    # Install each package
    for package in required_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Error installing {package}. Please try to install it manually.")
            return False
    
    print("\nAll dependencies installed successfully!")
    print("You can now run the product manager application.")
    return True

if __name__ == "__main__":
    install_dependencies()