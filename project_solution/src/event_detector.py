"""
Event Detector Module for Project Sentinel

This module detects various types of events from retail sensor data streams:
- Scanner Avoidance: Products detected by vision but not scanned
- Barcode Switching: Different product scanned than detected
- Weight Discrepancies: Actual weight differs from expected
- Long Queue Length: Too many customers waiting
- Long Wait Time: Excessive customer wait times
- Inventory Discrepancies: Mismatch between expected and actual inventory
- System Crashes: Station downtime detection
- Staffing Needs: When additional staff are required
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict


class EventDetector:
    """
    Main event detection engine that processes streaming retail data
    and identifies anomalies and issues requiring attention.
    """
    
    def __init__(self, products_catalog: Dict[str, Any], config: Dict[str, Any] = None):
        """
        Initialize the event detector with product catalog and configuration.
        
        Args:
            products_catalog: Dictionary mapping SKU to product details
            config: Configuration parameters for thresholds
        """
        self.products_catalog = products_catalog
        self.config = config or self._default_config()
        
        # State tracking for event detection
        self.pos_transactions = []
        self.product_recognitions = []
        self.queue_monitoring = []
        self.rfid_readings = []
        self.inventory_snapshots = []
        
        # Temporal tracking
        self.station_activity = defaultdict(list)
        self.customer_sessions = defaultdict(list)
        self.last_inventory_check = {}
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration thresholds for event detection."""
        return {
            'weight_tolerance_percent': 10,  # Allow 10% variance
            'queue_length_threshold': 5,     # Alert when 5+ customers
            'wait_time_threshold': 300,      # Alert when 300+ seconds
            'recognition_confidence_min': 0.7,  # Minimum confidence for matching
            'inventory_check_interval': 600,  # Check every 10 minutes
            'station_inactive_threshold': 180,  # Consider crashed after 3 min
        }
    
    # @algorithm Time-Series Correlation | Match POS transactions with vision recognition by timestamp
    def detect_scanner_avoidance(self) -> List[Dict[str, Any]]:
        """
        Detect cases where product recognition detected an item
        but no corresponding POS transaction occurred.
        
        Returns:
            List of scanner avoidance events
        """
        events = []
        
        # Group recognition events by station and timestamp window
        for recognition in self.product_recognitions:
            timestamp = datetime.fromisoformat(recognition['timestamp'])
            station_id = recognition['station_id']
            predicted_sku = recognition['data']['predicted_product']
            confidence = recognition['data']['accuracy']
            
            # Only consider high-confidence predictions
            if confidence < self.config['recognition_confidence_min']:
                continue
            
            # Look for matching POS transaction within time window
            time_window_start = timestamp - timedelta(seconds=5)
            time_window_end = timestamp + timedelta(seconds=10)
            
            matching_transaction = False
            for pos in self.pos_transactions:
                pos_time = datetime.fromisoformat(pos['timestamp'])
                if (pos['station_id'] == station_id and
                    time_window_start <= pos_time <= time_window_end and
                    pos['data']['sku'] == predicted_sku):
                    matching_transaction = True
                    break
            
            # Scanner avoidance detected
            if not matching_transaction:
                events.append({
                    'timestamp': recognition['timestamp'],
                    'event_id': f"E_SA_{len(events)}",
                    'event_data': {
                        'event_name': 'Scanner Avoidance',
                        'station_id': station_id,
                        'product_sku': predicted_sku,
                        'confidence': confidence
                    }
                })
        
        return events
    
    # @algorithm Cross-Validation Matching | Compare vision predictions with scanned items
    def detect_barcode_switching(self) -> List[Dict[str, Any]]:
        """
        Detect cases where the scanned barcode doesn't match
        the product detected by the vision system.
        
        Returns:
            List of barcode switching events
        """
        events = []
        
        for pos in self.pos_transactions:
            pos_time = datetime.fromisoformat(pos['timestamp'])
            station_id = pos['station_id']
            scanned_sku = pos['data']['sku']
            
            # Find corresponding vision recognition
            time_window = timedelta(seconds=10)
            for recognition in self.product_recognitions:
                recog_time = datetime.fromisoformat(recognition['timestamp'])
                
                if (recognition['station_id'] == station_id and
                    abs((pos_time - recog_time).total_seconds()) <= time_window.total_seconds()):
                    
                    predicted_sku = recognition['data']['predicted_product']
                    confidence = recognition['data']['accuracy']
                    
                    # High confidence mismatch indicates switching
                    if (predicted_sku != scanned_sku and 
                        confidence >= self.config['recognition_confidence_min']):
                        
                        # Get customer_id if available
                        customer_id = pos['data'].get('customer_id', 'Unknown')
                        
                        events.append({
                            'timestamp': pos['timestamp'],
                            'event_id': f"E_BS_{len(events)}",
                            'event_data': {
                                'event_name': 'Barcode Switching',
                                'station_id': station_id,
                                'customer_id': customer_id,
                                'actual_sku': predicted_sku,
                                'scanned_sku': scanned_sku
                            }
                        })
                        break
        
        return events
    
    # @algorithm Statistical Outlier Detection | Identify weight anomalies beyond threshold
    def detect_weight_discrepancies(self) -> List[Dict[str, Any]]:
        """
        Detect cases where the actual scanned weight differs
        significantly from the expected product weight.
        
        Returns:
            List of weight discrepancy events
        """
        events = []
        
        for pos in self.pos_transactions:
            sku = pos['data']['sku']
            actual_weight = pos['data'].get('weight_g', 0)
            
            if sku in self.products_catalog:
                expected_weight = self.products_catalog[sku]['weight']
                tolerance = expected_weight * (self.config['weight_tolerance_percent'] / 100)
                
                # Check if weight is outside tolerance range
                if abs(actual_weight - expected_weight) > tolerance:
                    customer_id = pos['data'].get('customer_id', 'Unknown')
                    
                    events.append({
                        'timestamp': pos['timestamp'],
                        'event_id': f"E_WD_{len(events)}",
                        'event_data': {
                            'event_name': 'Weight Discrepancies',
                            'station_id': pos['station_id'],
                            'customer_id': customer_id,
                            'product_sku': sku,
                            'expected_weight': int(expected_weight),
                            'actual_weight': int(actual_weight)
                        }
                    })
        
        return events
    
    # @algorithm Threshold-Based Monitoring | Detect queue congestion metrics
    def detect_queue_issues(self) -> List[Dict[str, Any]]:
        """
        Detect long queue lengths and excessive wait times.
        
        Returns:
            List of queue-related events
        """
        events = []
        
        for queue_data in self.queue_monitoring:
            station_id = queue_data['station_id']
            customer_count = queue_data['data']['customer_count']
            avg_dwell_time = queue_data['data']['average_dwell_time']
            
            # Long queue length
            if customer_count >= self.config['queue_length_threshold']:
                events.append({
                    'timestamp': queue_data['timestamp'],
                    'event_id': f"E_QL_{len(events)}",
                    'event_data': {
                        'event_name': 'Long Queue Length',
                        'station_id': station_id,
                        'num_of_customers': customer_count
                    }
                })
            
            # Long wait time
            if avg_dwell_time >= self.config['wait_time_threshold']:
                events.append({
                    'timestamp': queue_data['timestamp'],
                    'event_id': f"E_WT_{len(events)}",
                    'event_data': {
                        'event_name': 'Long Wait Time',
                        'station_id': station_id,
                        'wait_time_seconds': int(avg_dwell_time)
                    }
                })
        
        return events
    
    # @algorithm State Comparison | Compare inventory snapshots to detect discrepancies
    def detect_inventory_discrepancies(self) -> List[Dict[str, Any]]:
        """
        Compare inventory snapshots with expected inventory based on
        POS transactions to detect theft or misplacement.
        
        Returns:
            List of inventory discrepancy events
        """
        events = []
        
        if len(self.inventory_snapshots) < 2:
            return events
        
        # Compare consecutive snapshots
        for i in range(len(self.inventory_snapshots) - 1):
            prev_snapshot = self.inventory_snapshots[i]
            curr_snapshot = self.inventory_snapshots[i + 1]
            
            prev_data = prev_snapshot['data']
            curr_data = curr_snapshot['data']
            
            # Calculate expected inventory change based on POS transactions
            snapshot_start = datetime.fromisoformat(prev_snapshot['timestamp'])
            snapshot_end = datetime.fromisoformat(curr_snapshot['timestamp'])
            
            # Count items sold in this period
            items_sold = defaultdict(int)
            for pos in self.pos_transactions:
                pos_time = datetime.fromisoformat(pos['timestamp'])
                if snapshot_start <= pos_time < snapshot_end:
                    items_sold[pos['data']['sku']] += 1
            
            # Check each SKU for discrepancies
            for sku in prev_data.keys():
                expected_inventory = prev_data[sku] - items_sold.get(sku, 0)
                actual_inventory = curr_data.get(sku, 0)
                
                # Significant discrepancy detected
                if expected_inventory != actual_inventory:
                    discrepancy = abs(expected_inventory - actual_inventory)
                    # Only report if discrepancy is significant (more than 2 units)
                    if discrepancy > 2:
                        events.append({
                            'timestamp': curr_snapshot['timestamp'],
                            'event_id': f"E_ID_{len(events)}",
                            'event_data': {
                                'event_name': 'Inventory Discrepancy',
                                'SKU': sku,
                                'Expected_Inventory': expected_inventory,
                                'Actual_Inventory': actual_inventory
                            }
                        })
        
        return events
    
    # @algorithm Activity Gap Detection | Identify system downtime from inactive stations
    def detect_system_crashes(self) -> List[Dict[str, Any]]:
        """
        Detect when stations become inactive for extended periods,
        indicating possible system crashes.
        
        Returns:
            List of system crash events
        """
        events = []
        
        # Group activities by station
        station_activities = defaultdict(list)
        for pos in self.pos_transactions:
            station_activities[pos['station_id']].append(pos)
        for queue in self.queue_monitoring:
            station_activities[queue['station_id']].append(queue)
        
        # Check for gaps in activity
        for station_id, activities in station_activities.items():
            # Sort by timestamp
            sorted_activities = sorted(activities, key=lambda x: x['timestamp'])
            
            for i in range(len(sorted_activities) - 1):
                current_time = datetime.fromisoformat(sorted_activities[i]['timestamp'])
                next_time = datetime.fromisoformat(sorted_activities[i + 1]['timestamp'])
                
                gap_seconds = (next_time - current_time).total_seconds()
                
                # Inactive for too long - potential crash
                if gap_seconds >= self.config['station_inactive_threshold']:
                    events.append({
                        'timestamp': sorted_activities[i + 1]['timestamp'],
                        'event_id': f"E_SC_{len(events)}",
                        'event_data': {
                            'event_name': 'Unexpected Systems Crash',
                            'station_id': station_id,
                            'duration_seconds': int(gap_seconds)
                        }
                    })
        
        return events
    
    def detect_staffing_needs(self) -> List[Dict[str, Any]]:
        """
        Detect when additional staff are needed based on queue metrics.
        
        Returns:
            List of staffing need events
        """
        events = []
        
        for queue_data in self.queue_monitoring:
            # If queue is long or wait time is high, suggest staffing
            if (queue_data['data']['customer_count'] >= self.config['queue_length_threshold'] or
                queue_data['data']['average_dwell_time'] >= self.config['wait_time_threshold']):
                
                events.append({
                    'timestamp': queue_data['timestamp'],
                    'event_id': f"E_SN_{len(events)}",
                    'event_data': {
                        'event_name': 'Staffing Needs',
                        'station_id': queue_data['station_id'],
                        'Staff_type': 'Cashier'
                    }
                })
        
        return events
    
    def load_data(self, data_dict: Dict[str, List[Dict]]):
        """
        Load streaming data into the detector for processing.
        
        Args:
            data_dict: Dictionary containing lists of data by type
        """
        self.pos_transactions = data_dict.get('pos_transactions', [])
        self.product_recognitions = data_dict.get('product_recognition', [])
        self.queue_monitoring = data_dict.get('queue_monitoring', [])
        self.rfid_readings = data_dict.get('rfid_readings', [])
        self.inventory_snapshots = data_dict.get('inventory_snapshots', [])
    
    def detect_all_events(self) -> List[Dict[str, Any]]:
        """
        Run all event detection algorithms and return combined results.
        
        Returns:
            List of all detected events sorted by timestamp
        """
        all_events = []
        
        # Run all detection algorithms
        all_events.extend(self.detect_scanner_avoidance())
        all_events.extend(self.detect_barcode_switching())
        all_events.extend(self.detect_weight_discrepancies())
        all_events.extend(self.detect_queue_issues())
        all_events.extend(self.detect_inventory_discrepancies())
        all_events.extend(self.detect_system_crashes())
        all_events.extend(self.detect_staffing_needs())
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x['timestamp'])
        
        # Reassign event IDs sequentially
        for idx, event in enumerate(all_events):
            event['event_id'] = f"E{idx:03d}"
        
        return all_events
