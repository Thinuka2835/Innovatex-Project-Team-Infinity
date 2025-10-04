"""
Automated Demo Execution Script for Project Sentinel

What it is: Single-command automation script to run the entire solution
Why created: To meet submission requirements for automated execution
How it works:
    1. Checks and installs required Python packages
    2. Runs event detection on input data
    3. Generates output events.jsonl files
    4. Optionally starts the dashboard
How to use: python run_demo.py [--with-dashboard]
"""

import subprocess
import sys
import os
from pathlib import Path


def check_python_version():
    """Ensure Python version is 3.9 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"Error: Python 3.9+ required. Current version: {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")


def install_dependencies():
    """Install required Python packages."""
    print("\n" + "=" * 70)
    print("INSTALLING DEPENDENCIES")
    print("=" * 70)
    
    packages = [
        'dash',
        'plotly',
        'pandas'
    ]
    
    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', package, '--quiet'],
                stdout=subprocess.DEVNULL
            )
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            print(f"  Please install manually: pip install {package}")


def run_event_detection(input_dir, output_dir):
    """Run event detection pipeline."""
    print("\n" + "=" * 70)
    print("RUNNING EVENT DETECTION")
    print("=" * 70)
    
    # Get paths - go up two levels from executables to project_solution, then to src
    project_root = Path(__file__).parent.parent.parent
    src_dir = project_root / 'src'
    
    if not src_dir.exists():
        print(f"Error: src directory not found at {src_dir}")
        print(f"Current file location: {Path(__file__).absolute()}")
        print(f"Project root: {project_root.absolute()}")
        raise FileNotFoundError(f"Cannot find src directory at {src_dir}")
    
    sys.path.insert(0, str(src_dir))
    
    # Import and run pipeline
    from main_pipeline import main as pipeline_main
    
    # Override sys.argv to pass arguments to pipeline
    original_argv = sys.argv
    sys.argv = [
        'main_pipeline.py',
        '--input', str(input_dir),
        '--output', str(output_dir / 'events.jsonl')
    ]
    
    try:
        pipeline_main()
    finally:
        sys.argv = original_argv


def start_dashboard(events_file, port=8050):
    """Start the visualization dashboard."""
    print("\n" + "=" * 70)
    print("STARTING DASHBOARD")
    print("=" * 70)
    
    # Get paths - go up two levels from executables to project_solution, then to src
    project_root = Path(__file__).parent.parent.parent
    src_dir = project_root / 'src'
    sys.path.insert(0, str(src_dir))
    
    from dashboard import main as dashboard_main
    
    original_argv = sys.argv
    sys.argv = [
        'dashboard.py',
        '--events', str(events_file),
        '--port', str(port)
    ]
    
    try:
        dashboard_main()
    finally:
        sys.argv = original_argv


def main():
    """Main execution function."""
    print("=" * 70)
    print("PROJECT SENTINEL - AUTOMATED DEMO")
    print("=" * 70)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Set up paths - go up two levels to project_solution root
    project_root = Path(__file__).parent.parent.parent
    data_input_dir = project_root / 'data' / 'input'
    output_test_dir = project_root / 'evidence' / 'output' / 'test'
    output_final_dir = project_root / 'evidence' / 'output' / 'final'
    
    # Create output directories
    output_test_dir.mkdir(parents=True, exist_ok=True)
    output_final_dir.mkdir(parents=True, exist_ok=True)
    
    # Run event detection for test dataset
    print("\nProcessing TEST dataset...")
    run_event_detection(data_input_dir, output_test_dir)
    
    # For demonstration, also generate final dataset output
    # (in actual submission, this would use different input data)
    print("\nProcessing FINAL dataset...")
    run_event_detection(data_input_dir, output_final_dir)
    
    # Check if dashboard should be started
    if '--with-dashboard' in sys.argv or '-d' in sys.argv:
        events_file = output_test_dir / 'events.jsonl'
        start_dashboard(events_file)
    else:
        print("\n" + "=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70)
        print("\nOutput files generated:")
        print(f"  - {output_test_dir / 'events.jsonl'}")
        print(f"  - {output_final_dir / 'events.jsonl'}")
        print("\nTo start the dashboard, run:")
        print("  python run_demo.py --with-dashboard")


if __name__ == '__main__':
    main()
