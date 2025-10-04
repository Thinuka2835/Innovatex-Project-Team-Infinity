"""
Test Suite for Project Sentinel

What it is: Automated tests to verify system functionality
Why created: To ensure all components work correctly
How it works: Runs unit tests on each module
How to use: python test_suite.py
"""

import sys
import json
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from data_loader import DataLoader
from event_detector import EventDetector


class TestSuite:
    """Comprehensive test suite for Project Sentinel."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests_run = 0
    
    def assert_true(self, condition, message):
        """Assert a condition is true."""
        self.tests_run += 1
        if condition:
            self.passed += 1
            print(f"✓ {message}")
        else:
            self.failed += 1
            print(f"✗ {message}")
    
    def test_data_loading(self):
        """Test data loading functionality."""
        print("\n" + "=" * 60)
        print("TEST: Data Loading")
        print("=" * 60)
        
        data_input = Path(__file__).parent.parent / 'data' / 'input'
        loader = DataLoader(str(data_input))
        
        # Test JSONL loading
        pos_data = loader.load_jsonl('pos_transactions.jsonl')
        self.assert_true(
            len(pos_data) > 0,
            "POS transactions loaded"
        )
        self.assert_true(
            'timestamp' in pos_data[0],
            "POS data has timestamp field"
        )
        
        # Test CSV loading
        products = loader.load_products_catalog()
        self.assert_true(
            len(products) > 0,
            "Product catalog loaded"
        )
        self.assert_true(
            'weight' in list(products.values())[0],
            "Product has weight field"
        )
        
        # Test full data loading
        all_data = loader.load_all_data()
        self.assert_true(
            'pos_transactions' in all_data,
            "All data dict has POS transactions"
        )
        self.assert_true(
            'products_catalog' in all_data,
            "All data dict has product catalog"
        )
    
    def test_event_detection(self):
        """Test event detection algorithms."""
        print("\n" + "=" * 60)
        print("TEST: Event Detection")
        print("=" * 60)
        
        # Load test data
        data_input = Path(__file__).parent.parent / 'data' / 'input'
        loader = DataLoader(str(data_input))
        data = loader.load_all_data()
        
        # Initialize detector
        detector = EventDetector(data['products_catalog'])
        detector.load_data(data)
        
        # Test weight discrepancy detection
        weight_events = detector.detect_weight_discrepancies()
        self.assert_true(
            isinstance(weight_events, list),
            "Weight discrepancy detection returns list"
        )
        
        # Test queue issue detection
        queue_events = detector.detect_queue_issues()
        self.assert_true(
            len(queue_events) > 0,
            "Queue issues detected"
        )
        
        # Test inventory discrepancy detection
        inventory_events = detector.detect_inventory_discrepancies()
        self.assert_true(
            isinstance(inventory_events, list),
            "Inventory discrepancy detection returns list"
        )
        
        # Test barcode switching detection
        switching_events = detector.detect_barcode_switching()
        self.assert_true(
            isinstance(switching_events, list),
            "Barcode switching detection returns list"
        )
        
        # Test scanner avoidance detection
        avoidance_events = detector.detect_scanner_avoidance()
        self.assert_true(
            isinstance(avoidance_events, list),
            "Scanner avoidance detection returns list"
        )
        
        # Test full detection pipeline
        all_events = detector.detect_all_events()
        self.assert_true(
            len(all_events) > 0,
            "Events detected by full pipeline"
        )
        self.assert_true(
            all_events[0]['event_id'].startswith('E'),
            "Event IDs have correct format"
        )
        
        # Verify event structure
        if all_events:
            event = all_events[0]
            self.assert_true(
                'timestamp' in event,
                "Events have timestamp"
            )
            self.assert_true(
                'event_data' in event,
                "Events have event_data"
            )
            self.assert_true(
                'event_name' in event['event_data'],
                "Event data has event_name"
            )
    
    def test_output_format(self):
        """Test output file format."""
        print("\n" + "=" * 60)
        print("TEST: Output Format")
        print("=" * 60)
        
        output_file = Path(__file__).parent.parent / 'evidence' / 'output' / 'test' / 'events.jsonl'
        
        self.assert_true(
            output_file.exists(),
            "Output file exists"
        )
        
        if output_file.exists():
            with open(output_file, 'r') as f:
                lines = f.readlines()
            
            self.assert_true(
                len(lines) > 0,
                "Output file is not empty"
            )
            
            # Test first line is valid JSON
            try:
                event = json.loads(lines[0])
                self.assert_true(
                    True,
                    "Output lines are valid JSON"
                )
                
                # Test structure
                self.assert_true(
                    'timestamp' in event,
                    "Output events have timestamp"
                )
                self.assert_true(
                    'event_id' in event,
                    "Output events have event_id"
                )
                self.assert_true(
                    'event_data' in event,
                    "Output events have event_data"
                )
            except json.JSONDecodeError:
                self.assert_true(
                    False,
                    "Output lines are valid JSON"
                )
    
    def test_configuration(self):
        """Test configuration handling."""
        print("\n" + "=" * 60)
        print("TEST: Configuration")
        print("=" * 60)
        
        # Test default config
        products = {'PRD_TEST': {'weight': 100, 'price': 50}}
        detector = EventDetector(products)
        
        self.assert_true(
            detector.config is not None,
            "Default config loaded"
        )
        self.assert_true(
            'weight_tolerance_percent' in detector.config,
            "Config has weight tolerance"
        )
        
        # Test custom config
        custom_config = {
            'weight_tolerance_percent': 15,
            'queue_length_threshold': 6
        }
        detector2 = EventDetector(products, config=custom_config)
        
        self.assert_true(
            detector2.config['weight_tolerance_percent'] == 15,
            "Custom config applied"
        )
    
    def run_all_tests(self):
        """Run all tests and print summary."""
        print("\n" + "=" * 60)
        print("PROJECT SENTINEL - TEST SUITE")
        print("=" * 60)
        
        try:
            self.test_data_loading()
            self.test_event_detection()
            self.test_output_format()
            self.test_configuration()
        except Exception as e:
            print(f"\n✗ Test execution error: {e}")
            import traceback
            traceback.print_exc()
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Passed: {self.passed} ✓")
        print(f"Failed: {self.failed} ✗")
        
        if self.failed == 0:
            print("\n✓ ALL TESTS PASSED!")
            return 0
        else:
            print(f"\n✗ {self.failed} TEST(S) FAILED")
            return 1


if __name__ == '__main__':
    suite = TestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)
