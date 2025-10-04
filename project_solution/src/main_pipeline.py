"""
Main Pipeline for Project Sentinel Event Detection

This is the main entry point that orchestrates the entire event detection pipeline.

What it is: The primary execution script that ties all components together
Why created: To provide a simple, single-command interface for processing data
How it works:
    1. Loads all input data (POS, vision, queue, RFID, inventory)
    2. Initializes event detector with product catalog
    3. Runs all detection algorithms
    4. Saves results to output file
How to use: python main_pipeline.py --input <input_dir> --output <output_file>
"""

import argparse
import sys
from pathlib import Path

from data_loader import DataLoader, save_events
from event_detector import EventDetector


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Project Sentinel Event Detection Pipeline'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='../data/input',
        help='Path to input data directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='../evidence/output/test/events.jsonl',
        help='Path to output events file'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration JSON file (optional)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("PROJECT SENTINEL - EVENT DETECTION SYSTEM")
    print("=" * 70)
    print()
    
    # Load data
    loader = DataLoader(args.input)
    data = loader.load_all_data()
    
    # Initialize detector with product catalog
    config = None
    if args.config:
        import json
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    detector = EventDetector(
        products_catalog=data['products_catalog'],
        config=config
    )
    
    # Load streaming data into detector
    print("Loading data into event detector...")
    detector.load_data({
        'pos_transactions': data['pos_transactions'],
        'product_recognition': data['product_recognition'],
        'queue_monitoring': data['queue_monitoring'],
        'rfid_readings': data['rfid_readings'],
        'inventory_snapshots': data['inventory_snapshots']
    })
    
    # Run detection
    print("Running event detection algorithms...")
    print("  - Scanner Avoidance Detection")
    print("  - Barcode Switching Detection")
    print("  - Weight Discrepancy Detection")
    print("  - Queue Issue Detection")
    print("  - Inventory Discrepancy Detection")
    print("  - System Crash Detection")
    print("  - Staffing Need Detection")
    print()
    
    events = detector.detect_all_events()
    
    print(f"Detected {len(events)} total events")
    print()
    
    # Event breakdown by type
    event_types = {}
    for event in events:
        event_name = event['event_data']['event_name']
        event_types[event_name] = event_types.get(event_name, 0) + 1
    
    print("Event Breakdown:")
    for event_name, count in sorted(event_types.items()):
        print(f"  {event_name}: {count}")
    print()
    
    # Save results
    save_events(events, args.output)
    
    print()
    print("=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
