# Technical Architecture - Project Sentinel

## System Overview

Project Sentinel is a multi-modal event detection system that processes streaming retail sensor data to identify anomalies, theft, and operational issues in real-time.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT DATA LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ POS Trans    │  │ Vision       │  │ Queue        │          │
│  │ (JSONL)      │  │ Recognition  │  │ Monitoring   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ RFID         │  │ Inventory    │  │ Product      │          │
│  │ Readings     │  │ Snapshots    │  │ Catalog      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LOADING LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              DataLoader Module                           │   │
│  │  - load_jsonl()     - load_csv()                        │   │
│  │  - load_products_catalog()                               │   │
│  │  - load_customer_data()                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EVENT DETECTION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              EventDetector Engine                        │   │
│  │                                                           │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │ Time-Series Correlation                          │  │   │
│  │  │ → detect_scanner_avoidance()                     │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │ Cross-Validation Matching                        │  │   │
│  │  │ → detect_barcode_switching()                     │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │ Statistical Outlier Detection                    │  │   │
│  │  │ → detect_weight_discrepancies()                  │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │ Threshold-Based Monitoring                       │  │   │
│  │  │ → detect_queue_issues()                          │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │ State Comparison Analysis                        │  │   │
│  │  │ → detect_inventory_discrepancies()               │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │ Activity Gap Detection                           │  │   │
│  │  │ → detect_system_crashes()                        │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       OUTPUT LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐                  ┌──────────────┐            │
│  │ Events JSONL │                  │ Dashboard    │            │
│  │ File         │◄─────────────────┤ (Plotly Dash)│            │
│  └──────────────┘                  └──────────────┘            │
│                                            ↓                     │
│                                     ┌──────────────┐            │
│                                     │ Web Browser  │            │
│                                     │ (localhost)  │            │
│                                     └──────────────┘            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Data Loading Layer

**Module:** `data_loader.py`

**Responsibilities:**
- Parse JSONL and CSV files
- Validate data structure
- Handle missing/malformed data
- Build lookup dictionaries

**Key Classes:**
- `DataLoader`: Main data loading interface

**Data Flow:**
```
File System → DataLoader → Structured Dictionaries → Event Detector
```

---

### 2. Event Detection Layer

**Module:** `event_detector.py`

**Responsibilities:**
- Implement detection algorithms
- Maintain temporal state
- Correlate multi-modal data
- Generate event objects

**Key Classes:**
- `EventDetector`: Main detection engine

**State Management:**
```python
{
    'pos_transactions': [],        # POS events
    'product_recognitions': [],    # Vision predictions
    'queue_monitoring': [],        # Queue metrics
    'rfid_readings': [],           # RFID tags
    'inventory_snapshots': [],     # Inventory states
    'station_activity': {},        # Activity tracking
    'customer_sessions': {},       # Session tracking
}
```

---

### 3. Pipeline Orchestration

**Module:** `main_pipeline.py`

**Responsibilities:**
- Command-line interface
- Data loading coordination
- Detection execution
- Output generation
- Statistics reporting

**Execution Flow:**
```
Parse Args → Load Data → Initialize Detector → 
Run Detection → Save Results → Print Summary
```

---

### 4. Visualization Layer

**Module:** `dashboard.py`

**Responsibilities:**
- Load event data
- Generate interactive charts
- Display metrics
- Provide event details

**Technology Stack:**
- Plotly Dash (web framework)
- Plotly.js (charting)
- Pandas (data manipulation)

---

### 5. Automation Layer

**Module:** `run_demo.py`

**Responsibilities:**
- Environment validation
- Dependency installation
- Pipeline execution
- Dashboard launch

---

## Data Models

### Event Object

```python
{
    "timestamp": "ISO-8601 datetime",
    "event_id": "E###",
    "event_data": {
        "event_name": "Event Type",
        # Event-specific fields
    }
}
```

### Product Catalog Entry

```python
{
    "sku": "PRD_X_##",
    "product_name": "string",
    "barcode": "string",
    "weight": float,
    "price": float,
    "quantity": int,
    "epc_range": "string"
}
```

### POS Transaction

```python
{
    "timestamp": "ISO-8601",
    "station_id": "SCC#",
    "status": "Active|Inactive",
    "data": {
        "customer_id": "C###",
        "sku": "PRD_X_##",
        "product_name": "string",
        "barcode": "string",
        "price": float,
        "weight_g": float
    }
}
```

---

## Algorithm Pipeline

### Detection Sequence

```
1. Load all input data
   ↓
2. Build product catalog lookup
   ↓
3. Initialize detector with config
   ↓
4. Run parallel detection algorithms:
   ├─ Scanner Avoidance (O(n×m))
   ├─ Barcode Switching (O(n×m))
   ├─ Weight Discrepancy (O(n))
   ├─ Queue Issues (O(n))
   ├─ Inventory Discrepancy (O(s×p))
   └─ System Crashes (O(n log n))
   ↓
5. Merge and sort events by timestamp
   ↓
6. Assign sequential event IDs
   ↓
7. Save to JSONL output
```

### Time Complexity Analysis

- **Best Case:** O(n) - All detections are linear
- **Average Case:** O(n×m) - Correlation algorithms dominate
- **Worst Case:** O(n×m) - All events need matching

Where:
- n = number of events in primary stream
- m = number of events in secondary stream
- s = number of inventory snapshots
- p = POS transactions per snapshot period

---

## Scalability Considerations

### Current Implementation

- **In-Memory Processing**: Loads all data at once
- **Batch Processing**: Processes complete dataset
- **Single-Threaded**: Sequential execution

**Suitable for:**
- Datasets up to 100K events
- Batch analysis (hourly, daily)
- Single-server deployment

### Future Enhancements

#### 1. Streaming Architecture

```
Kafka/RabbitMQ → Stream Processor → Event Detector → Alert System
```

**Benefits:**
- Real-time detection
- Continuous monitoring
- Lower latency

#### 2. Distributed Processing

```
Data Sharding → Multiple Detectors → Result Aggregation
```

**Benefits:**
- Handle millions of events
- Horizontal scaling
- Fault tolerance

#### 3. Microservices

```
API Gateway
    ├─ Data Ingestion Service
    ├─ Detection Service
    ├─ Alerting Service
    └─ Dashboard Service
```

---

## Performance Optimization

### Current Optimizations

1. **Pre-filtered Confidence**: Skip low-confidence predictions early
2. **Dictionary Lookups**: O(1) product catalog access
3. **Sorted Processing**: Binary search opportunities
4. **Early Exit**: Stop searching after match found

### Potential Optimizations

1. **Indexing**:
   ```python
   # Index events by station_id for O(1) lookup
   station_index = defaultdict(list)
   for event in events:
       station_index[event['station_id']].append(event)
   ```

2. **Time Windows**:
   ```python
   # Use sorted arrays + binary search
   events_sorted_by_time = sorted(events, key=lambda x: x['timestamp'])
   # Find events in window: O(log n) + O(k)
   ```

3. **Parallel Processing**:
   ```python
   from multiprocessing import Pool
   with Pool(processes=4) as pool:
       results = pool.map(detect_events, data_chunks)
   ```

---

## Security Considerations

### Data Privacy

- No PII in event outputs (customer_id is anonymized reference)
- Secure file permissions on output directories
- Optional encryption for sensitive data

### Input Validation

- JSON schema validation
- Timestamp format checking
- SKU existence verification
- Numeric range validation

---

## Error Handling

### Robust Failure Modes

```python
try:
    events = detector.detect_all_events()
except Exception as e:
    logger.error(f"Detection failed: {e}")
    # Fallback: return partial results or empty list
    events = []
```

### Graceful Degradation

- Missing files: Skip and continue
- Malformed data: Log and skip record
- Invalid timestamps: Use default or estimate
- Lookup failures: Mark as "Unknown"

---

## Testing Strategy

### Unit Tests

```python
def test_scanner_avoidance():
    detector = EventDetector(catalog)
    # Test case: Vision detection without POS scan
    events = detector.detect_scanner_avoidance()
    assert len(events) > 0
```

### Integration Tests

```python
def test_full_pipeline():
    loader = DataLoader('test_data/')
    data = loader.load_all_data()
    detector = EventDetector(data['products_catalog'])
    events = detector.detect_all_events()
    assert events  # Non-empty result
```

### Performance Tests

```python
import time
def test_performance():
    start = time.time()
    events = detector.detect_all_events()
    duration = time.time() - start
    assert duration < 10.0  # Must complete in 10 seconds
```

---

## Deployment Architecture

### Development Environment

```
Local Machine
├─ Python 3.9+
├─ Virtual Environment
└─ Sample Data
```

### Production Environment (Future)

```
Load Balancer
    ↓
Application Servers (N instances)
    ↓
Message Queue (Kafka)
    ↓
Database (PostgreSQL/MongoDB)
    ↓
Cache (Redis)
```

---

## Monitoring & Observability

### Metrics to Track

1. **Performance**:
   - Processing time per event
   - Detection algorithm latency
   - Memory usage

2. **Quality**:
   - Events detected per hour
   - False positive rate
   - Detection accuracy

3. **System**:
   - CPU utilization
   - Disk I/O
   - API response times

### Logging Strategy

```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Processing {len(events)} events")
logger.warning(f"Low confidence detection: {confidence}")
logger.error(f"Failed to process event: {event_id}")
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Python 3.9+ | Core implementation |
| Data Processing | Pandas | Data manipulation |
| Visualization | Plotly Dash | Interactive dashboard |
| Charting | Plotly.js | Dynamic charts |
| I/O | json, csv | Data loading |
| CLI | argparse | Command-line interface |
| Automation | subprocess | Dependency management |

---

## Design Principles

1. **Modularity**: Each component is self-contained
2. **Extensibility**: Easy to add new detection algorithms
3. **Maintainability**: Clear documentation and structure
4. **Performance**: Optimized for batch processing
5. **Reliability**: Robust error handling
6. **Usability**: Simple command-line interface

---

## Future Roadmap

### Phase 1: Enhanced Detection
- Machine learning for pattern recognition
- Anomaly detection using statistical models
- Customer behavior profiling

### Phase 2: Real-Time Processing
- Stream processing integration
- Live dashboard updates
- Real-time alerting

### Phase 3: Enterprise Features
- Multi-store support
- Historical analytics
- Predictive modeling
- Integration APIs
