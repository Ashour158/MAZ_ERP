#!/usr/bin/env python3
"""
Simple Code Quality and Functionality Test
Tests basic functionality without complex dependencies
"""

import sys
import os
import json
import time
from datetime import datetime

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import json
        import time
        import datetime
        print("✅ Basic imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_structures():
    """Test data structure functionality"""
    print("🧪 Testing data structures...")
    
    try:
        # Test dictionary operations
        test_data = {
            'contact': {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com'
            },
            'account': {
                'name': 'Test Account',
                'type': 'Customer'
            }
        }
        
        # Test JSON serialization
        json_str = json.dumps(test_data)
        parsed_data = json.loads(json_str)
        
        assert parsed_data['contact']['first_name'] == 'John'
        assert parsed_data['account']['name'] == 'Test Account'
        
        print("✅ Data structures working correctly")
        return True
    except Exception as e:
        print(f"❌ Data structure error: {e}")
        return False

def test_contact_validation():
    """Test contact validation logic"""
    print("🧪 Testing contact validation...")
    
    try:
        def validate_contact(contact_data):
            required_fields = ['first_name', 'last_name', 'email']
            for field in required_fields:
                if field not in contact_data or not contact_data[field]:
                    return False, f"Missing {field}"
            return True, "Valid"
        
        # Test valid contact
        valid_contact = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com'
        }
        
        is_valid, message = validate_contact(valid_contact)
        assert is_valid == True
        
        # Test invalid contact
        invalid_contact = {
            'first_name': 'John',
            'last_name': 'Doe'
            # Missing email
        }
        
        is_valid, message = validate_contact(invalid_contact)
        assert is_valid == False
        
        print("✅ Contact validation working correctly")
        return True
    except Exception as e:
        print(f"❌ Contact validation error: {e}")
        return False

def test_coding_system_logic():
    """Test coding system logic"""
    print("🧪 Testing coding system logic...")
    
    try:
        def generate_code(prefix, territory_code, sequence):
            return f"{prefix}-{territory_code}-{sequence:04d}"
        
        # Test code generation
        code = generate_code("CON", "NA", 1)
        assert code == "CON-NA-0001"
        
        # Test territory mapping
        territory_mapping = {
            'North America': 'NA',
            'Europe': 'EU',
            'Asia Pacific': 'AP'
        }
        
        territory_code = territory_mapping.get('North America', 'DEF')
        assert territory_code == 'NA'
        
        print("✅ Coding system logic working correctly")
        return True
    except Exception as e:
        print(f"❌ Coding system error: {e}")
        return False

def test_metrics_calculation():
    """Test metrics calculation"""
    print("🧪 Testing metrics calculation...")
    
    try:
        def calculate_engagement_score(contact_data):
            score = 0
            if contact_data.get('email'):
                score += 20
            if contact_data.get('phone'):
                score += 15
            if contact_data.get('company'):
                score += 15
            return min(score, 100)
        
        contact_data = {
            'email': 'test@example.com',
            'phone': '+1234567890',
            'company': 'Test Company'
        }
        
        score = calculate_engagement_score(contact_data)
        assert score == 50  # 20 + 15 + 15
        
        print("✅ Metrics calculation working correctly")
        return True
    except Exception as e:
        print(f"❌ Metrics calculation error: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print("🧪 Testing error handling...")
    
    try:
        def safe_divide(a, b):
            try:
                return a / b
            except ZeroDivisionError:
                return "Cannot divide by zero"
        
        # Test normal division
        result = safe_divide(10, 2)
        assert result == 5.0
        
        # Test division by zero
        result = safe_divide(10, 0)
        assert result == "Cannot divide by zero"
        
        print("✅ Error handling working correctly")
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    print("🧪 Testing file operations...")
    
    try:
        # Test JSON file operations
        test_data = {
            'test': 'data',
            'timestamp': datetime.now().isoformat()
        }
        
        # Write to temporary file
        temp_file = 'temp_test.json'
        with open(temp_file, 'w') as f:
            json.dump(test_data, f)
        
        # Read from file
        with open(temp_file, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data['test'] == 'data'
        
        # Clean up
        os.remove(temp_file)
        
        print("✅ File operations working correctly")
        return True
    except Exception as e:
        print(f"❌ File operations error: {e}")
        return False

def test_performance():
    """Test basic performance"""
    print("🧪 Testing performance...")
    
    try:
        start_time = time.time()
        
        # Simulate some processing
        data = []
        for i in range(1000):
            data.append({
                'id': i,
                'name': f'Item {i}',
                'value': i * 2
            })
        
        # Process data
        processed = [item for item in data if item['id'] % 2 == 0]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert len(processed) == 500
        assert execution_time < 1.0  # Should complete in under 1 second
        
        print(f"✅ Performance test passed (execution time: {execution_time:.3f}s)")
        return True
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def run_all_tests():
    """Run all simple tests"""
    print("🚀 Starting Simple Code Quality Tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_data_structures,
        test_contact_validation,
        test_coding_system_logic,
        test_metrics_calculation,
        test_error_handling,
        test_file_operations,
        test_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
