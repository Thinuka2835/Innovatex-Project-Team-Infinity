# Project Sentinel - Complete Solution

## Overview

This is a comprehensive event detection system for Project Sentinel that analyzes retail sensor data streams to identify various anomalies and issues in real-time.

## What This Solution Does

The system processes multiple data streams from a retail environment (POS transactions, vision recognition, queue monitoring, RFID, and inventory) to detect:

1. **Scanner Avoidance** - Items detected by vision but not scanned at checkout
2. **Barcode Switching** - Customer scans wrong/cheaper barcode instead of actual product
3. **Weight Discrepancies** - Product weight doesn't match expected weight
4. **Long Queue Length** - Too many customers waiting at checkout
5. **Long Wait Time** - Excessive customer wait times
6. **Inventory Discrepancies** - Mismatch between expected and actual inventory
7. **System Crashes** - Station downtime detection
8. **Staffing Needs** - When additional staff are required

## Directory Structure

```
project_solution/
├── README.md                          # This file
├── data/                              # Copy of input data for processing
│   ├── input/                         # Input data files
│   │   ├── pos_transactions.jsonl
│   │   ├── product_recognition.jsonl
│   │   ├── queue_monitoring.jsonl
│   │   ├── rfid_readings.jsonl
│   │   ├── inventory_snapshots.jsonl
│   │   ├── products_list.csv
│   │   └── customer_data.csv
│   └── output/                        # Reference output examples
├── src/                               # Source code
│   ├── event_detector.py              # Core event detection algorithms
│   ├── data_loader.py                 # Data loading and parsing
│   ├── main_pipeline.py               # Main execution pipeline
│   └── dashboard.py                   # Interactive visualization dashboard
├── evidence/
│   ├── executables/
│   │   └── run_demo.py                # Automated execution script
│   ├── output/
│   │   ├── test/
│   │   │   └── events.jsonl           # Generated test events
│   │   └── final/
│   │       └── events.jsonl           # Generated final events
│   └── screenshots/                   # Dashboard screenshots
└── docs/                              # Additional documentation
```

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation & Execution

The easiest way to run the entire solution is using the automated demo script:

```bash
cd evidence/executables
python run_demo.py
```

This will:
1. Check Python version
2. Install required dependencies (dash, plotly, pandas)
3. Process input data and detect events
4. Generate `events.jsonl` files in `evidence/output/test/` and `evidence/output/final/`

### With Dashboard

To also start the interactive visualization dashboard:

```bash
python run_demo.py --with-dashboard
```

Then open your browser to http://localhost:8050

## Component Documentation

### 1. Event Detector (`src/event_detector.py`)

**What it is:** The core event detection engine with multiple detection algorithms.

**Why it was created:** To analyze multi-modal sensor data and identify anomalies that indicate theft, operational issues, or customer experience problems.

**How it works:**
- Uses time-series correlation to match events across data streams
- Applies statistical outlier detection for weight anomalies
- Implements threshold-based monitoring for queue metrics
- Performs cross-validation between vision and POS systems
- Compares inventory snapshots to detect discrepancies

**Key Algorithms:**
- **Time-Series Correlation** - Matches POS transactions with vision recognition by timestamp windows
- **Cross-Validation Matching** - Compares vision predictions with scanned items
- **Statistical Outlier Detection** - Identifies weight anomalies beyond tolerance thresholds
- **Threshold-Based Monitoring** - Detects queue congestion metrics
- **State Comparison** - Compares inventory snapshots to detect discrepancies
- **Activity Gap Detection** - Identifies system downtime from inactive stations

**How to use:**
```python
from event_detector import EventDetector
from data_loader import DataLoader

# Load data
loader = DataLoader('data/input')
data = loader.load_all_data()

# Initialize detector
detector = EventDetector(data['products_catalog'])
detector.load_data(data)

# Detect events
events = detector.detect_all_events()
```

### 2. Data Loader (`src/data_loader.py`)

**What it is:** A utility module for loading and parsing various data formats.

**Why it was created:** To provide a clean, reusable interface for loading JSONL and CSV files with proper error handling.

**How it works:**
- Reads JSONL files line by line, parsing each as JSON
- Loads CSV files using Python's csv module
- Validates data structure and handles missing files gracefully
- Converts raw data into structured Python dictionaries

**How to use:**
```python
from data_loader import DataLoader

loader = DataLoader('data/input')
all_data = loader.load_all_data()
```

### 3. Main Pipeline (`src/main_pipeline.py`)

**What it is:** The main orchestration script that runs the complete detection pipeline.

**Why it was created:** To provide a single command-line interface for processing data end-to-end.

**How it works:**
1. Parses command-line arguments
2. Loads all input data
3. Initializes event detector
4. Runs all detection algorithms
5. Saves results to output file
6. Prints summary statistics

**How to use:**
```bash
cd src
python main_pipeline.py --input ../data/input --output ../evidence/output/test/events.jsonl
```

### 4. Dashboard (`src/dashboard.py`)

**What it is:** An interactive web-based visualization dashboard built with Plotly Dash.

**Why it was created:** To provide real-time visualization of detected events, trends, and patterns for stakeholders.

**How it works:**
- Loads event data from JSONL file
- Creates interactive charts showing:
  - Event type distribution
  - Timeline of events
  - Station-wise breakdown
  - Hourly trends
- Displays detailed event table
- Provides summary statistics

**How to use:**
```bash
cd src
python dashboard.py --events ../evidence/output/test/events.jsonl --port 8050
```

Then navigate to http://localhost:8050 in your browser.

### 5. Automated Demo Script (`evidence/executables/run_demo.py`)

**What it is:** A one-command automation script for running the entire solution.

**Why it was created:** To meet submission requirements and provide easy execution for judges/evaluators.

**How it works:**
1. Validates Python version (3.9+)
2. Installs required packages automatically
3. Runs event detection pipeline
4. Generates output files
5. Optionally starts dashboard

**How to use:**
```bash
cd evidence/executables
python run_demo.py                    # Process data only
python run_demo.py --with-dashboard   # Process data and start dashboard
```

## Configuration

Event detection thresholds can be customized by modifying the config in `EventDetector.__init__()` or by passing a config dictionary:

```python
config = {
    'weight_tolerance_percent': 10,      # Allow 10% weight variance
    'queue_length_threshold': 5,         # Alert when 5+ customers
    'wait_time_threshold': 300,          # Alert when 300+ seconds
    'recognition_confidence_min': 0.7,   # Minimum vision confidence
    'inventory_check_interval': 600,     # Check every 10 minutes
    'station_inactive_threshold': 180,   # Crash after 3 min inactive
}
```

## Output Format

Events are saved as JSONL (JSON Lines), with one event per line:

```json
{
  "timestamp": "2025-08-13T16:05:45",
  "event_id": "E001",
  "event_data": {
    "event_name": "Scanner Avoidance",
    "station_id": "SCC1",
    "product_sku": "PRD_S_04",
    "confidence": 0.95
  }
}
```

## Dependencies

Required Python packages:
- `dash` - Web dashboard framework
- `plotly` - Interactive visualizations
- `pandas` - Data manipulation and analysis

Standard library only (no external dependencies):
- `json` - JSON parsing
- `csv` - CSV file handling
- `datetime` - Timestamp processing
- `pathlib` - Path handling
- `collections` - Data structures

## Testing

To test with the provided sample data:

```bash
cd evidence/executables
python run_demo.py
```

Check output files:
- `evidence/output/test/events.jsonl`
- `evidence/output/final/events.jsonl`

## Performance

- Processes 250+ POS transactions in < 5 seconds
- Handles 7000+ queue monitoring events efficiently
- Memory efficient streaming processing
- Scalable to larger datasets

## Troubleshooting

**Issue:** Import errors
- **Solution:** Run from correct directory or use `run_demo.py`

**Issue:** Missing dependencies
- **Solution:** Run `pip install dash plotly pandas`

**Issue:** No events detected
- **Solution:** Check input data format and paths

**Issue:** Dashboard won't start
- **Solution:** Check port 8050 is available, or use `--port` flag

## Future Enhancements

Potential improvements for production deployment:
1. Real-time streaming data processing
2. Machine learning for pattern recognition
3. Alert notifications (email, SMS)
4. Integration with retail management systems
5. Historical trend analysis
6. Predictive analytics for staffing

## Authors

Created for Project Sentinel InnovateX Challenge 2025

## License

Proprietary - Competition Submission
