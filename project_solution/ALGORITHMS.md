# Algorithm Documentation

This document provides detailed explanation of all algorithms used in the Project Sentinel event detection system.

## Overview

The system employs 6 main algorithmic approaches to detect various types of events:

1. Time-Series Correlation
2. Cross-Validation Matching
3. Statistical Outlier Detection
4. Threshold-Based Monitoring
5. State Comparison Analysis
6. Activity Gap Detection

---

## 1. Time-Series Correlation

**Purpose:** Match POS transactions with vision recognition events

**Algorithm Type:** Temporal pattern matching

**Implementation:** `detect_scanner_avoidance()`

**How it works:**

```
For each vision recognition event:
  1. Extract timestamp, station_id, predicted_sku, confidence
  2. If confidence < threshold: skip
  3. Define time window [timestamp-5s, timestamp+10s]
  4. Search for matching POS transaction in window
  5. Match criteria: same station_id AND same SKU
  6. If no match found: FLAG as Scanner Avoidance
```

**Complexity:** O(n × m) where n = recognition events, m = POS transactions

**Parameters:**
- `recognition_confidence_min`: Minimum confidence to consider (default: 0.7)
- Time window: -5 to +10 seconds from recognition timestamp

**Example:**
```
Vision sees PRD_S_04 at 16:05:45 with 0.95 confidence
No POS scan for PRD_S_04 between 16:05:40 and 16:05:55
→ Scanner Avoidance detected
```

---

## 2. Cross-Validation Matching

**Purpose:** Detect barcode switching by comparing vision with scanned items

**Algorithm Type:** Cross-modal validation

**Implementation:** `detect_barcode_switching()`

**How it works:**

```
For each POS transaction:
  1. Extract scanned_sku, timestamp, station_id
  2. Find vision recognition within ±10 second window
  3. If found:
     a. Compare predicted_sku with scanned_sku
     b. Check confidence level
     c. If SKUs differ AND confidence high: FLAG
```

**Complexity:** O(n × m) where n = POS transactions, m = recognition events

**Parameters:**
- `recognition_confidence_min`: 0.7 (minimum confidence for reliable mismatch)
- Time window: ±10 seconds

**Example:**
```
Vision predicts PRD_F_08 at 16:15:18 (confidence 0.92)
POS scans PRD_F_07 at 16:15:20 (same station)
→ Barcode Switching detected (customer scanned cheaper item)
```

---

## 3. Statistical Outlier Detection

**Purpose:** Identify products with abnormal weights

**Algorithm Type:** Statistical threshold testing

**Implementation:** `detect_weight_discrepancies()`

**How it works:**

```
For each POS transaction:
  1. Get scanned_sku and actual_weight
  2. Lookup expected_weight from product catalog
  3. Calculate tolerance = expected_weight × tolerance_percent / 100
  4. If |actual_weight - expected_weight| > tolerance:
     FLAG as Weight Discrepancy
```

**Complexity:** O(n) where n = POS transactions

**Parameters:**
- `weight_tolerance_percent`: 10% (allows for packaging variance)

**Example:**
```
PRD_S_05 expected: 1500g
PRD_S_05 scanned: 913g (39% lighter)
Tolerance: ±150g
→ Weight Discrepancy detected
```

**Why this works:**
- Catches partial items (e.g., half-full bottles)
- Detects multiple items bundled together
- Accounts for normal packaging variance

---

## 4. Threshold-Based Monitoring

**Purpose:** Detect operational issues from queue metrics

**Algorithm Type:** Simple threshold comparison

**Implementation:** `detect_queue_issues()`

**How it works:**

```
For each queue monitoring event:
  1. Extract customer_count and average_dwell_time
  2. If customer_count >= queue_length_threshold:
     FLAG Long Queue Length
  3. If average_dwell_time >= wait_time_threshold:
     FLAG Long Wait Time
```

**Complexity:** O(n) where n = queue monitoring records

**Parameters:**
- `queue_length_threshold`: 5 customers
- `wait_time_threshold`: 300 seconds (5 minutes)

**Example:**
```
SCC1 at 16:19:50: 6 customers, 350s average wait
→ Both Long Queue Length AND Long Wait Time detected
→ Triggers Staffing Needs recommendation
```

---

## 5. State Comparison Analysis

**Purpose:** Detect inventory discrepancies through delta analysis

**Algorithm Type:** State transition analysis

**Implementation:** `detect_inventory_discrepancies()`

**How it works:**

```
For consecutive inventory snapshots (t1, t2):
  1. For each SKU:
     a. Get inventory[t1] = prev_count
     b. Count items sold between t1 and t2 from POS
     c. Calculate expected[t2] = prev_count - items_sold
     d. Get actual[t2] = curr_count
     e. If |expected - actual| > threshold (2 units):
        FLAG Inventory Discrepancy
```

**Complexity:** O(s × p) where s = snapshots, p = POS transactions per period

**Parameters:**
- Discrepancy threshold: 2 units (ignore minor counting errors)

**Example:**
```
PRD_F_03 at 16:00:00: 120 units
POS sold: 0 units (16:00 to 16:10)
PRD_F_03 at 16:10:00: 120 units (expected: 120)
✓ No discrepancy

PRD_F_03 at 16:10:00: 120 units
POS sold: 5 units (16:10 to 16:20)
PRD_F_03 at 16:20:00: 112 units (expected: 115)
→ Inventory Discrepancy: -3 units (possible theft)
```

**Why this works:**
- Compares expected vs actual inventory
- Accounts for legitimate sales
- Detects shrinkage, theft, or data errors

---

## 6. Activity Gap Detection

**Purpose:** Identify system crashes from prolonged inactivity

**Algorithm Type:** Temporal gap analysis

**Implementation:** `detect_system_crashes()`

**How it works:**

```
For each station:
  1. Collect all activity timestamps (POS + queue)
  2. Sort chronologically
  3. For consecutive events (t1, t2):
     a. Calculate gap = t2 - t1
     b. If gap >= station_inactive_threshold:
        FLAG System Crash with duration
```

**Complexity:** O(n log n) where n = total station activities (for sorting)

**Parameters:**
- `station_inactive_threshold`: 180 seconds (3 minutes)

**Example:**
```
SCC1 last activity: 16:23:45
SCC1 next activity: 16:26:45
Gap: 180 seconds
→ System Crash detected (3 minute downtime)
```

---

## Algorithm Selection Rationale

| Event Type | Algorithm | Why This Algorithm? |
|------------|-----------|---------------------|
| Scanner Avoidance | Time-Series Correlation | Need to match events across different sensors with timing tolerance |
| Barcode Switching | Cross-Validation | Requires comparing independent data sources (vision vs POS) |
| Weight Discrepancy | Statistical Outlier | Simple, fast, handles normal variance while catching anomalies |
| Queue Issues | Threshold-Based | Direct metric monitoring, immediate actionable alerts |
| Inventory | State Comparison | Tracks state transitions, accounts for legitimate changes |
| System Crash | Activity Gap | Detects absence of expected events, simple and reliable |

---

## Performance Characteristics

| Algorithm | Time Complexity | Space Complexity | Best For |
|-----------|-----------------|------------------|----------|
| Time-Series Correlation | O(n×m) | O(n+m) | Medium-sized event streams |
| Cross-Validation | O(n×m) | O(n+m) | Real-time paired validation |
| Statistical Outlier | O(n) | O(1) | Large transaction volumes |
| Threshold-Based | O(n) | O(1) | Continuous monitoring |
| State Comparison | O(s×p) | O(s) | Periodic state checks |
| Activity Gap | O(n log n) | O(n) | Fault detection |

---

## Optimization Opportunities

1. **Time-Series Correlation**
   - Use time-indexed hash maps for O(1) lookup
   - Implement sliding window for streaming data

2. **Cross-Validation**
   - Pre-group events by station_id
   - Use binary search on sorted timestamps

3. **State Comparison**
   - Cache POS aggregations per period
   - Incremental updates vs full recalculation

4. **Activity Gap Detection**
   - Maintain sorted activity queues per station
   - Only check new events vs full resort

---

## Validation & Accuracy

Each algorithm is designed with:
- **Configurable thresholds** to balance sensitivity vs false positives
- **Confidence scoring** where applicable
- **Time windows** that account for sensor synchronization delays
- **Tolerance ranges** for natural variance

The system prioritizes **high precision** (few false positives) over recall, as false alarms in retail operations are costly and reduce trust in the system.
