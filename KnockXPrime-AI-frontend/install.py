#!/usr/bin/env python3
"""
KnockXPrime AI CLI Installer
Automated installation script for the CLI frontend
"""
import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    requirements = [
        "pyfiglet==1.0.2",
        "rich==13.7.0", 
        "httpx==0.25.2",
        "click==8.1.7"
    ]
    
    for package in requirements:
        try:
            print(f"  Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"  ❌ Failed to install {package}")
            return False
    
    return True

def make_executable():
    """Make the CLI script executable on Unix systems"""
    if os.name != 'nt':  # Not Windows
        try:
            cli_path = Path("cli_app.py")
            if cli_path.exists():
                os.chmod(cli_path, 0o755)
                print("✅ Made cli_app.py executable")
        except Exception as e:
            print(f"⚠️  Could not make executable: {e}")

def create_desktop_shortcut():
    """Create desktop shortcut (optional)"""
    try:
        current_dir = Path.cwd()
        cli_path = current_dir / "cli_app.py"
        
        if os.name == 'nt':  # Windows
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "KnockXPrime AI.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = str(cli_path)
            shortcut.WorkingDirectory = str(current_dir)
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            print("✅ Desktop shortcut created")
        else:
            print("💡 Desktop shortcut creation not implemented for this OS")
            
    except ImportError:
        print("💡 Install 'pywin32' and 'winshell' for Windows shortcut support")
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {e}")

def test_installation():
    """Test if installation was successful"""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        import pyfiglet
        import rich
        import httpx
        import click
        
        print("✅ All packages imported successfully")
        
        # Test pyfiglet
        test_text = pyfiglet.figlet_format("Test", font="slant")
        if test_text:
            print("✅ pyfiglet working")
        
        # Test rich
        from rich.console import Console
        console = Console()
        print("✅ Rich library working")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main installation process"""
    print("🚀 KnockXPrime AI CLI Installer")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Installation failed")
        sys.exit(1)
    
    # Make executable
    make_executable()
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Make sure your KnockXPrime AI server is running")
    print("2. Run: python cli_app.py")
    print("3. Or if executable: ./cli_app.py")
    print("\n💡 Run 'python demo.py' to see a preview of the CLI")
    
    # Optional desktop shortcut
    create_shortcut = input("\n❓ Create desktop shortcut? (y/N): ").lower().strip()
    if create_shortcut in ['y', 'yes']:
        create_desktop_shortcut()
    
    print("\n🚀 Ready to use KnockXPrime AI CLI!")

if __name__ == "__main__":
    main()