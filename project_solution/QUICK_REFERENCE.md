# Quick Reference Card - Project Sentinel

## One-Line Execution

```bash
cd project_solution/evidence/executables && python run_demo.py
```

## File Locations

| What | Where |
|------|-------|
| Source Code | `src/` |
| Documentation | `*.md` files in root |
| Input Data | `data/input/` |
| Output Events | `evidence/output/test/events.jsonl` |
| Automation | `evidence/executables/run_demo.py` |
| Tests | `src/test_suite.py` |

## Commands

```bash
# Run everything (automated)
python run_demo.py

# With dashboard
python run_demo.py --with-dashboard

# Run pipeline only
python main_pipeline.py

# Run dashboard only
python dashboard.py

# Run tests
python test_suite.py
```

## Output Format

```json
{
  "timestamp": "2025-08-13T16:05:45",
  "event_id": "E001",
  "event_data": {
    "event_name": "Scanner Avoidance",
    "station_id": "SCC1",
    "product_sku": "PRD_S_04"
  }
}
```

## Event Types Detected

1. Scanner Avoidance
2. Barcode Switching
3. Weight Discrepancies
4. Long Queue Length
5. Long Wait Time
6. Inventory Discrepancy
7. System Crashes
8. Staffing Needs

## Algorithms Used

1. Time-Series Correlation
2. Cross-Validation Matching
3. Statistical Outlier Detection
4. Threshold-Based Monitoring
5. State Comparison Analysis
6. Activity Gap Detection

## Configuration

```python
config = {
    'weight_tolerance_percent': 10,
    'queue_length_threshold': 5,
    'wait_time_threshold': 300,
    'recognition_confidence_min': 0.7,
    'inventory_check_interval': 600,
    'station_inactive_threshold': 180,
}
```

## Dependencies

```bash
pip install dash plotly pandas
```

## Documentation Files

- **README.md** - Main system documentation
- **USAGE_GUIDE.md** - Detailed usage instructions
- **ALGORITHMS.md** - Algorithm explanations
- **ARCHITECTURE.md** - Technical architecture
- **SOLUTION_SUMMARY.md** - Complete summary

## Key Statistics

- **654 events** detected from sample data
- **25 tests** all passing
- **1,100+ lines** of source code
- **1,700+ lines** of documentation
- **< 5 seconds** processing time

## Support

1. Read README.md first
2. Check USAGE_GUIDE.md for commands
3. Review ALGORITHMS.md for detection details
4. Examine source code comments
5. Run test_suite.py to verify setup

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Import errors | Run from correct directory |
| Missing packages | `pip install -r requirements.txt` |
| Port in use | Use `--port` flag with different number |
| No events | Check input data exists and is valid |

## Project Structure

```
project_solution/
├── src/               # Source code
├── data/              # Input data
├── evidence/          # Outputs & automation
├── *.md               # Documentation
└── requirements.txt   # Dependencies
```

---

**Status**: ✅ Complete & Ready

**Quick Start**: `python run_demo.py`

**Dashboard**: Add `--with-dashboard` flag
