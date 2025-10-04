"""
Data Loader Module for Project Sentinel

This module handles loading and parsing of various data formats:
- JSONL (JSON Lines) files for streaming data
- CSV files for product catalogs and customer data
- Data validation and preprocessing

Why created: To provide a clean interface for loading diverse data sources
How it works: Reads files, parses JSON/CSV, validates structure, returns Python objects
How to use: Call load_all_data() with the input directory path
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any


class DataLoader:
    """Handles loading and parsing of input data files."""
    
    def __init__(self, input_dir: str):
        """
        Initialize data loader with input directory path.
        
        Args:
            input_dir: Path to directory containing input data files
        """
        self.input_dir = Path(input_dir)
        
    def load_jsonl(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load a JSONL (JSON Lines) file.
        
        Args:
            filename: Name of the JSONL file
            
        Returns:
            List of dictionaries, one per line
        """
        filepath = self.input_dir / filename
        data = []
        
        if not filepath.exists():
            print(f"Warning: File {filepath} not found")
            return data
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num} in {filename}: {e}")
        
        return data
    
    def load_csv(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load a CSV file.
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            List of dictionaries, one per row
        """
        filepath = self.input_dir / filename
        data = []
        
        if not filepath.exists():
            print(f"Warning: File {filepath} not found")
            return data
        
        with open(filepath, 'r', encoding='utf-8') as f:
            # Skip empty lines and get to header
            lines = [line for line in f if line.strip()]
            if not lines:
                return data
            
            # Read CSV
            reader = csv.DictReader(lines)
            for row in reader:
                # Clean up whitespace in keys and values
                cleaned_row = {k.strip(): v.strip() if isinstance(v, str) else v 
                              for k, v in row.items()}
                data.append(cleaned_row)
        
        return data
    
    def load_products_catalog(self) -> Dict[str, Dict[str, Any]]:
        """
        Load and parse the products catalog CSV.
        
        Returns:
            Dictionary mapping SKU to product details
        """
        products_list = self.load_csv('products_list.csv')
        catalog = {}
        
        for product in products_list:
            sku = product.get('SKU', '').strip()
            if not sku:
                continue
                
            catalog[sku] = {
                'sku': sku,
                'product_name': product.get('product_name', ''),
                'barcode': product.get('barcode', ''),
                'weight': float(product.get('weight', 0)),
                'price': float(product.get('price', 0)),
                'quantity': int(product.get('quantity', 0)),
                'epc_range': product.get('EPC_range', '')
            }
        
        return catalog
    
    def load_customer_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Load and parse the customer data CSV.
        
        Returns:
            Dictionary mapping customer ID to customer details
        """
        customer_list = self.load_csv('customer_data.csv')
        customers = {}
        
        for customer in customer_list:
            customer_id = customer.get('Customer_ID', '').strip()
            if not customer_id:
                continue
                
            customers[customer_id] = {
                'customer_id': customer_id,
                'name': customer.get('Customer_Name', ''),
                'email': customer.get('Email', ''),
                'phone': customer.get('Phone_Number', '')
            }
        
        return customers
    
    def load_all_data(self) -> Dict[str, Any]:
        """
        Load all input data files.
        
        Returns:
            Dictionary containing all loaded data:
            - pos_transactions: List of POS transaction events
            - product_recognition: List of vision system predictions
            - queue_monitoring: List of queue metrics
            - rfid_readings: List of RFID tag reads
            - inventory_snapshots: List of inventory snapshots
            - products_catalog: Dictionary of product details by SKU
            - customers: Dictionary of customer details by ID
        """
        print("Loading data files...")
        
        data = {
            'pos_transactions': self.load_jsonl('pos_transactions.jsonl'),
            'product_recognition': self.load_jsonl('product_recognition.jsonl'),
            'queue_monitoring': self.load_jsonl('queue_monitoring.jsonl'),
            'rfid_readings': self.load_jsonl('rfid_readings.jsonl'),
            'inventory_snapshots': self.load_jsonl('inventory_snapshots.jsonl'),
            'products_catalog': self.load_products_catalog(),
            'customers': self.load_customer_data()
        }
        
        # Print summary
        print(f"  POS Transactions: {len(data['pos_transactions'])} records")
        print(f"  Product Recognition: {len(data['product_recognition'])} records")
        print(f"  Queue Monitoring: {len(data['queue_monitoring'])} records")
        print(f"  RFID Readings: {len(data['rfid_readings'])} records")
        print(f"  Inventory Snapshots: {len(data['inventory_snapshots'])} records")
        print(f"  Products Catalog: {len(data['products_catalog'])} products")
        print(f"  Customers: {len(data['customers'])} customers")
        print("Data loading complete!\n")
        
        return data


def save_events(events: List[Dict[str, Any]], output_path: str):
    """
    Save detected events to a JSONL file.
    
    Args:
        events: List of event dictionaries
        output_path: Path to output file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for event in events:
            f.write(json.dumps(event) + '\n')
    
    print(f"Saved {len(events)} events to {output_path}")
