# System Flow Diagram

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER STARTS HERE                           │
└─────────────────────────────────────────────────────────────────────┘
                                   ↓
                    ┌──────────────────────────┐
                    │   Run Automation Script   │
                    │  python run_demo.py      │
                    └──────────────────────────┘
                                   ↓
        ┌──────────────────────────┴──────────────────────────┐
        │  1. Check Python Version (3.9+)                     │
        │  2. Install Dependencies (dash, plotly, pandas)     │
        └──────────────────────────┬──────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA LOADING PHASE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────┐                                            │
│  │  DataLoader Module  │                                            │
│  └──────────┬──────────┘                                            │
│             │                                                         │
│             ├─→ Load pos_transactions.jsonl (252 records)           │
│             ├─→ Load product_recognition.jsonl (264 records)        │
│             ├─→ Load queue_monitoring.jsonl (7,181 records)         │
│             ├─→ Load rfid_readings.jsonl (5,753 records)            │
│             ├─→ Load inventory_snapshots.jsonl (13 records)         │
│             ├─→ Load products_list.csv (50 products)                │
│             └─→ Load customer_data.csv (60 customers)               │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                       EVENT DETECTION PHASE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    EventDetector Engine                       │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                               │  │
│  │  Algorithm 1: Time-Series Correlation                        │  │
│  │  ├─→ Match vision events with POS transactions              │  │
│  │  └─→ Output: Scanner Avoidance events (9 detected)          │  │
│  │                                                               │  │
│  │  Algorithm 2: Cross-Validation Matching                      │  │
│  │  ├─→ Compare predicted SKU vs scanned SKU                   │  │
│  │  └─→ Output: Barcode Switching events (241 detected)        │  │
│  │                                                               │  │
│  │  Algorithm 3: Statistical Outlier Detection                  │  │
│  │  ├─→ Compare actual weight vs expected weight               │  │
│  │  └─→ Output: Weight Discrepancy events (10 detected)        │  │
│  │                                                               │  │
│  │  Algorithm 4: Threshold-Based Monitoring                     │  │
│  │  ├─→ Check queue length and wait times                      │  │
│  │  └─→ Output: Queue/Wait events (195 detected)               │  │
│  │                                                               │  │
│  │  Algorithm 5: State Comparison Analysis                      │  │
│  │  ├─→ Compare inventory snapshots                            │  │
│  │  └─→ Output: Inventory Discrepancy events (4 detected)      │  │
│  │                                                               │  │
│  │  Algorithm 6: Activity Gap Detection                         │  │
│  │  ├─→ Find gaps in station activity                          │  │
│  │  └─→ Output: System Crash events                            │  │
│  │                                                               │  │
│  │  Additional: Staffing Need Detection                         │  │
│  │  └─→ Output: Staffing Need events (195 detected)            │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│                Total Events Detected: 654                             │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                          OUTPUT PHASE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Events sorted by timestamp and assigned sequential IDs              │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Save to: evidence/output/test/events.jsonl                 │    │
│  │ Format: JSON Lines (one event per line)                    │    │
│  │ Size: 654 events                                            │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Save to: evidence/output/final/events.jsonl                │    │
│  │ (Same format, ready for final dataset)                     │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                ↓
        ┌───────────────────────────────────────┐
        │   If --with-dashboard flag used:      │
        └───────────────────┬───────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      VISUALIZATION PHASE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Dashboard Application                      │  │
│  │                  (Plotly Dash + Pandas)                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │  Event Type     │  │  Timeline       │  │  Station        │   │
│  │  Distribution   │  │  Scatter Plot   │  │  Breakdown      │   │
│  │  (Bar Chart)    │  │                 │  │  (Stacked Bar)  │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                                                                       │
│  ┌─────────────────┐  ┌──────────────────────────────────────┐    │
│  │  Hourly Trends  │  │  Detailed Event Table (Paginated)    │    │
│  │  (Line Chart)   │  │                                        │    │
│  └─────────────────┘  └──────────────────────────────────────┘    │
│                                                                       │
│  Accessible at: http://localhost:8050                                │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                           USER REVIEWS                               │
└─────────────────────────────────────────────────────────────────────┘
```

## Module Interaction Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                      run_demo.py (Automation)                       │
│  • Validates environment                                            │
│  • Installs dependencies                                            │
│  • Orchestrates entire workflow                                     │
└────────┬───────────────────────────────────────────────────────────┘
         │
         ├─────→ main_pipeline.py
         │       └─┬─→ data_loader.py (loads all input files)
         │         │
         │         └─→ event_detector.py (runs all algorithms)
         │
         └─────→ dashboard.py (if --with-dashboard flag)
                 └─→ Loads events.jsonl and creates visualizations
```

## Data Relationship Diagram

```
┌──────────────────┐         ┌──────────────────┐
│ POS Transactions │◄────┐   │ Product          │
│  - timestamp     │     │   │ Recognition      │
│  - station_id    │     │   │  - timestamp     │
│  - sku           │     │   │  - station_id    │
│  - customer_id   │     │   │  - predicted_sku │
│  - weight        │     │   │  - confidence    │
└────────┬─────────┘     │   └────────┬─────────┘
         │               │            │
         │               │            │
         │  Cross-Validation          │
         │     Matching               │
         └───────────┬───────────────┘
                     ↓
         ┌──────────────────────┐
         │ Barcode Switching    │
         │ Events Detected      │
         └──────────────────────┘

┌──────────────────┐
│ Queue Monitoring │
│  - customer_count│
│  - dwell_time    │
└────────┬─────────┘
         │
         │ Threshold Check
         │
         ↓
┌──────────────────────┐
│ Queue Issue Events   │
│ Staffing Need Events │
└──────────────────────┘

┌──────────────────┐      ┌──────────────────┐
│ Inventory        │      │ POS Sales        │
│ Snapshot (T1)    │      │ Count (T1→T2)    │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         │                         │
         ↓                         ↓
┌──────────────────┐      ┌──────────────────┐
│ Expected         │      │ Actual           │
│ Inventory (T2)   │      │ Inventory (T2)   │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         └──────────┬──────────────┘
                    ↓
         ┌──────────────────────┐
         │ Inventory            │
         │ Discrepancy Events   │
         └──────────────────────┘
```

## Algorithm Decision Tree

```
                    ┌─────────────────┐
                    │  Input Event    │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │ Event Type?             │
                └────┬────────────────┬───┘
                     │                │
        ┌────────────┴────┐      ┌───┴────────────┐
        │ Vision          │      │ POS            │
        └────┬────────────┘      └───┬────────────┘
             │                       │
             │                       │
      ┌──────┴───────┐         ┌────┴─────────┐
      │ High         │         │ Check        │
      │ Confidence?  │         │ Weight       │
      └──────┬───────┘         └────┬─────────┘
             │                      │
        ┌────┴─────┐           ┌────┴─────────┐
        │ YES      │ NO        │ Within       │
        │          │           │ Tolerance?   │
        └────┬─────┘           └────┬─────────┘
             │                      │
      ┌──────┴────────┐        ┌────┴─────┐
      │ Match with    │        │ YES  NO  │
      │ POS in        │        │          │
      │ time window?  │        └────┬─────┘
      └──────┬────────┘             │
             │                  ┌───┴──────────┐
        ┌────┴─────┐           │ FLAG: Weight │
        │ YES  NO  │           │ Discrepancy  │
        │          │           └──────────────┘
        └────┬─────┘
             │
        ┌────┴──────────┐
        │ NO = Scanner  │
        │ Avoidance     │
        └───────────────┘

                 Queue Event
                      ↓
         ┌────────────┴────────────┐
         │ customer_count >= 5?    │
         └────┬───────────────┬────┘
              │               │
         ┌────┴───┐      ┌────┴───┐
         │ YES    │      │ NO     │
         │ FLAG   │      │ Skip   │
         └────────┘      └────────┘
```

## Testing Flow

```
┌──────────────────────────────────────────────────────────┐
│              Run test_suite.py                            │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────┴─────────┐      ┌───────┴─────────┐
   │ Test Data    │      │ Test Detection  │
   │ Loading      │      │ Algorithms      │
   └────┬─────────┘      └───────┬─────────┘
        │                        │
        │                        │
   ┌────┴─────────┐      ┌───────┴─────────┐
   │ Test Output  │      │ Test Config     │
   │ Format       │      │ Handling        │
   └────┬─────────┘      └───────┬─────────┘
        │                        │
        └────────────┬───────────┘
                     │
              ┌──────┴────────┐
              │ Print Summary │
              │ 25/25 PASSED  │
              └───────────────┘
```

## Submission Checklist Flow

```
✓ Source Code
  ├─ event_detector.py (all algorithms tagged)
  ├─ data_loader.py
  ├─ main_pipeline.py
  ├─ dashboard.py
  └─ test_suite.py

✓ Evidence
  ├─ executables/run_demo.py
  ├─ output/test/events.jsonl (654 events)
  └─ output/final/events.jsonl (ready)

✓ Documentation
  ├─ README.md (350+ lines)
  ├─ USAGE_GUIDE.md (400+ lines)
  ├─ ALGORITHMS.md (450+ lines)
  ├─ ARCHITECTURE.md (500+ lines)
  ├─ SOLUTION_SUMMARY.md
  └─ QUICK_REFERENCE.md

✓ Self-Contained
  └─ data/ (complete copy of input files)

✓ Tested
  └─ 25/25 tests passing

✓ Ready for Submission
```
