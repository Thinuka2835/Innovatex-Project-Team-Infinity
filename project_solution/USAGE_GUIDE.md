# Usage Guide - Project Sentinel

## Quick Start (30 seconds)

```bash
cd project_solution/evidence/executables
python run_demo.py
```

That's it! The system will automatically:
- Install dependencies
- Process data
- Generate events.jsonl files

---

## Detailed Usage

### Option 1: Automated Execution (Recommended)

**For judges/evaluators:**

```bash
cd evidence/executables
python run_demo.py
```

**With dashboard:**

```bash
python run_demo.py --with-dashboard
```
Then open http://localhost:8050 in your browser.

---

### Option 2: Manual Execution

**Step 1: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 2: Run event detection**

```bash
cd src
python main_pipeline.py --input ../data/input --output ../evidence/output/test/events.jsonl
```

**Step 3: View dashboard**

```bash
python dashboard.py --events ../evidence/output/test/events.jsonl
```

---

### Option 3: Python API Usage

```python
from src.data_loader import DataLoader
from src.event_detector import EventDetector

# Load data
loader = DataLoader('data/input')
data = loader.load_all_data()

# Initialize detector
detector = EventDetector(data['products_catalog'])
detector.load_data(data)

# Run detection
events = detector.detect_all_events()

# Print results
for event in events[:5]:
    print(event)
```

---

## Command Reference

### run_demo.py

```bash
python run_demo.py [options]
```

**Options:**
- `--with-dashboard` or `-d` - Start web dashboard after processing
- No arguments - Process data only

**Examples:**
```bash
python run_demo.py                    # Process only
python run_demo.py --with-dashboard   # Process + dashboard
python run_demo.py -d                 # Short form
```

---

### main_pipeline.py

```bash
python main_pipeline.py --input <dir> --output <file> [--config <json>]
```

**Arguments:**
- `--input` - Path to input data directory (default: ../data/input)
- `--output` - Path to output events file (default: ../evidence/output/test/events.jsonl)
- `--config` - Optional configuration JSON file

**Examples:**
```bash
# Default paths
python main_pipeline.py

# Custom paths
python main_pipeline.py --input /path/to/data --output /path/to/events.jsonl

# With custom config
python main_pipeline.py --config custom_config.json
```

---

### dashboard.py

```bash
python dashboard.py --events <file> [--port <number>]
```

**Arguments:**
- `--events` - Path to events JSONL file (default: ../evidence/output/test/events.jsonl)
- `--port` - Port number for dashboard (default: 8050)

**Examples:**
```bash
# Default settings
python dashboard.py

# Custom port
python dashboard.py --port 9000

# Different events file
python dashboard.py --events ../evidence/output/final/events.jsonl
```

---

## Configuration

### Custom Thresholds

Create a `config.json` file:

```json
{
  "weight_tolerance_percent": 15,
  "queue_length_threshold": 6,
  "wait_time_threshold": 400,
  "recognition_confidence_min": 0.75,
  "inventory_check_interval": 600,
  "station_inactive_threshold": 200
}
```

Use it:

```bash
python main_pipeline.py --config config.json
```

---

## Output Files

### Events File Format

Location: `evidence/output/test/events.jsonl`

Format: JSON Lines (one event per line)

Example:
```json
{"timestamp":"2025-08-13T16:05:45","event_id":"E001","event_data":{"event_name":"Scanner Avoidance","station_id":"SCC1","product_sku":"PRD_S_04"}}
```

### Dashboard Screenshots

Save screenshots from the dashboard to:
`evidence/screenshots/`

Recommended naming:
- `dashboard-overview.png`
- `event-timeline.png`
- `station-breakdown.png`

---

## Workflow for Different Datasets

### Test Dataset

```bash
cd evidence/executables
python run_demo.py
# Output: evidence/output/test/events.jsonl
```

### Final Dataset

Replace input data in `data/input/` with final dataset files, then:

```bash
cd src
python main_pipeline.py --input ../data/input --output ../evidence/output/final/events.jsonl
```

---

## Troubleshooting

### Problem: ModuleNotFoundError

**Solution:**
```bash
pip install dash plotly pandas
```

### Problem: File not found errors

**Solution:** Check you're running from correct directory:
```bash
cd project_solution/evidence/executables  # For run_demo.py
cd project_solution/src                   # For other scripts
```

### Problem: Port already in use

**Solution:** Use different port:
```bash
python dashboard.py --port 9000
```

### Problem: No events detected

**Solution:**
1. Check input data exists in `data/input/`
2. Verify file formats (JSONL for streams, CSV for catalogs)
3. Check timestamps are in ISO format
4. Lower detection thresholds in config

---

## Performance Tips

### For Large Datasets

1. **Increase processing limits:**
   - Modify time windows for faster correlation
   - Skip low-confidence predictions early

2. **Memory optimization:**
   - Process in batches if dataset is huge
   - Use generators instead of loading all data

3. **Speed up detection:**
   - Pre-index events by station_id
   - Use binary search on sorted timestamps

### For Real-Time Processing

1. **Stream processing:**
   - Process events as they arrive
   - Maintain sliding windows

2. **Incremental detection:**
   - Only process new data
   - Cache intermediate results

---

## Best Practices

1. **Always run automated demo first** - Ensures everything works
2. **Check output file size** - Should be non-empty with valid JSON
3. **Review dashboard** - Visual inspection catches issues
4. **Save screenshots** - Required for submission evidence
5. **Test with sample data** - Before processing final dataset

---

## Integration Examples

### With Streaming Server

```python
import socket
import json
from src.event_detector import EventDetector

# Connect to stream
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8765))

# Process streaming events
detector = EventDetector(products_catalog)
while True:
    data = sock.recv(4096).decode('utf-8')
    event = json.loads(data)
    # Process event...
```

### With REST API

```python
from flask import Flask, jsonify
from src.event_detector import EventDetector

app = Flask(__name__)
detector = EventDetector(products_catalog)

@app.route('/detect', methods=['POST'])
def detect_events():
    data = request.json
    detector.load_data(data)
    events = detector.detect_all_events()
    return jsonify(events)
```

---

## Additional Resources

- **README.md** - Complete system documentation
- **ALGORITHMS.md** - Detailed algorithm explanations
- **requirements.txt** - Python dependencies
- **src/** - Source code with inline documentation

---

## Support

For issues or questions:
1. Check this usage guide
2. Review README.md for component details
3. Examine source code comments
4. Test with provided sample data first
