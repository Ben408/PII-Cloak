#!/usr/bin/env python3
"""
Test script for the PII Detection Engine
Tests rule-based detection without requiring the ML model
"""

import sys
import os

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from detection_engine import PIIDetectionEngine

def test_detection_engine():
    """Test the detection engine with sample data"""
    
    print("🧪 Testing PII Detection Engine")
    print("=" * 50)
    
    # Initialize the engine
    engine = PIIDetectionEngine()
    
    # Test cases
    test_cases = [
        {
            "name": "Basic PII Detection",
            "text": "Hello, my name is John Smith and my email is john.smith@email.com. My phone number is (555) 123-4567."
        },
        {
            "name": "SSN and Credit Card",
            "text": "My SSN is 123-45-6789 and my credit card is 4111-1111-1111-1111."
        },
        {
            "name": "Address and IP",
            "text": "I live at 123 Main Street, Anytown, ST 12345. My server IP is 192.168.1.1."
        },
        {
            "name": "Complex Document",
            "text": """
            CONFIDENTIAL DOCUMENT
            
            Client: John Smith
            Email: john.smith@company.com
            Phone: (555) 987-6543
            Address: 456 Oak Avenue, Somewhere, CA 90210
            SSN: 987-65-4321
            Credit Card: 5555-4444-3333-2222
            IP Address: 10.0.0.1
            
            Project Details: This project involves sensitive data processing.
            """
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        # Run detection
        result = engine.detect_pii(test_case['text'])
        
        # Display results
        print("Original text:")
        print(test_case['text'][:100] + "..." if len(test_case['text']) > 100 else test_case['text'])
        
        print(f"\nDetected {len(result.entities_found)} entities:")
        for entity in result.entities_found:
            print(f"  • {entity.entity_type}: '{entity.value}' (confidence: {entity.confidence:.2f}, method: {entity.detection_method})")
        
        print(f"\nMasked text:")
        print(result.masked_content[:100] + "..." if len(result.masked_content) > 100 else result.masked_content)
        
        print(f"\nProcessing time: {result.processing_time:.3f} seconds")
        
        print("\n" + "="*50)
    
    print("\n✅ Detection engine test completed!")

def test_validation():
    """Test validation functions"""
    print("\n🔍 Testing Validation Functions")
    print("=" * 50)
    
    engine = PIIDetectionEngine()
    
    # Test credit card validation
    valid_cards = ["4111-1111-1111-1111", "5555-4444-3333-2222"]
    invalid_cards = ["4111-1111-1111-1112", "1234-5678-9012-3456"]
    
    print("Credit Card Validation:")
    for card in valid_cards:
        is_valid = engine._luhn_check(card.replace('-', ''))
        print(f"  {card}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    for card in invalid_cards:
        is_valid = engine._luhn_check(card.replace('-', ''))
        print(f"  {card}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test SSN validation
    valid_ssns = ["123-45-6789", "987-65-4321"]
    invalid_ssns = ["000-00-0000", "123-45-6780"]
    
    print("\nSSN Validation:")
    for ssn in valid_ssns:
        is_valid = engine._validate_ssn(ssn)
        print(f"  {ssn}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    for ssn in invalid_ssns:
        is_valid = engine._validate_ssn(ssn)
        print(f"  {ssn}: {'✅ Valid' if is_valid else '❌ Invalid'}")

if __name__ == "__main__":
    test_detection_engine()
    test_validation()
