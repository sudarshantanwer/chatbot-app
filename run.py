#!/usr/bin/env python3
"""
Run script for SmartBot Pro.
Provides multiple ways to start the application.
"""

import sys
import subprocess
import os
from pathlib import Path

def run_main():
    """Run the main modular application."""
    print("🚀 Starting SmartBot Pro (Modular Version)...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py"])

def run_legacy():
    """Run the legacy application."""
    print("🚀 Starting SmartBot Pro (Legacy Version)...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import streamlit
        import transformers
        import torch
        print("✅ All core dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--legacy":
            if check_dependencies():
                run_legacy()
        elif sys.argv[1] == "--check":
            check_dependencies()
        else:
            print("Usage: python run.py [--legacy|--check]")
    else:
        if check_dependencies():
            run_main()

if __name__ == "__main__":
    main()
