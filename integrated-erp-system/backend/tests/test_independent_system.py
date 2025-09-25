#!/usr/bin/env python3
"""
Independent ERP System - Comprehensive Test Suite
Test all functionality without Frappe dependencies
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
import json

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import independent modules
from core.base_document import BaseDocument
from core.validation import ValidationSystem, ValidationError
from core.utils import Utils
from core.database import DatabaseManager, ContactModel, AccountModel, CustomerModel
from independent.crm.contact import Contact
from independent.crm.account import Account
from independent.crm.customer import Customer

class TestCoreInfrastructure(unittest.TestCase):
    """Test core infrastructure components"""
    
    def test_base_document(self):
        """Test BaseDocument functionality"""
        print("🧪 Testing BaseDocument...")
        
        # Test document creation
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com'
        }
        
        doc = BaseDocument(data)
        self.assertIsNotNone(doc.name)
        self.assertEqual(doc.data['first_name'], 'John')
        self.assertEqual(doc.data['last_name'], 'Doe')
        
        # Test document methods
        doc.set('phone', '123-456-7890')
        self.assertEqual(doc.get('phone'), '123-456-7890')
        
        # Test as_dict conversion
        doc_dict = doc.as_dict()
        self.assertIn('name', doc_dict)
        self.assertIn('creation', doc_dict)
        self.assertIn('first_name', doc_dict)
        
        print("✅ BaseDocument test passed")
    
    def test_validation_system(self):
        """Test ValidationSystem functionality"""
        print("🧪 Testing ValidationSystem...")
        
        # Test email validation
        self.assertTrue(ValidationSystem.validate_email('test@example.com'))
        self.assertFalse(ValidationSystem.validate_email('invalid-email'))
        
        # Test phone validation
        self.assertTrue(ValidationSystem.validate_phone('+1-234-567-8900'))
        self.assertFalse(ValidationSystem.validate_phone('invalid-phone'))
        
        # Test required field validation
        with self.assertRaises(ValidationError):
            ValidationSystem.validate_required(None, "Test field")
        
        # Test length validation
        with self.assertRaises(ValidationError):
            ValidationSystem.validate_length("short", 10, 20, "Test field")
        
        print("✅ ValidationSystem test passed")
    
    def test_utils(self):
        """Test Utils functionality"""
        print("🧪 Testing Utils...")
        
        # Test now function
        now = Utils.now()
        self.assertIsInstance(now, datetime)
        
        # Test add_days function
        future_date = Utils.add_days(now, 7)
        self.assertEqual((future_date - now).days, 7)
        
        # Test get_time function
        time_str = Utils.get_time()
        self.assertIsInstance(time_str, str)
        self.assertRegex(time_str, r'\d{2}:\d{2}:\d{2}')
        
        # Test make_autoname function
        pattern = "TEST-.YYYY.-.MM.-.#####"
        name = Utils.make_autoname(pattern)
        self.assertIn(str(datetime.now().year), name)
        self.assertIn(str(datetime.now().month).zfill(2), name)
        
        print("✅ Utils test passed")

class TestCRMModules(unittest.TestCase):
    """Test CRM modules functionality"""
    
    def test_contact_creation(self):
        """Test Contact creation and validation"""
        print("🧪 Testing Contact creation...")
        
        # Test valid contact creation
        contact_data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'email_id': 'john.smith@example.com',
            'mobile_no': '+1-234-567-8900',
            'customer': 'CUST-001',
            'designation': 'CEO'
        }
        
        contact = Contact(contact_data)
        contact.validate()
        
        # Test contact properties
        self.assertEqual(contact.data['first_name'], 'John')
        self.assertEqual(contact.data['last_name'], 'Smith')
        self.assertEqual(contact.data['email_id'], 'john.smith@example.com')
        
        # Test contact metrics
        self.assertIn('contact_engagement_score', contact.data)
        self.assertIn('contact_influence_score', contact.data)
        self.assertIn('contact_priority', contact.data)
        
        print("✅ Contact creation test passed")
    
    def test_contact_validation(self):
        """Test Contact validation"""
        print("🧪 Testing Contact validation...")
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            contact = Contact({'email_id': 'test@example.com'})
            contact.validate()
        
        # Test invalid email
        with self.assertRaises(ValidationError):
            contact = Contact({
                'first_name': 'John',
                'last_name': 'Smith',
                'customer': 'CUST-001',
                'email_id': 'invalid-email'
            })
            contact.validate()
        
        # Test invalid phone
        with self.assertRaises(ValidationError):
            contact = Contact({
                'first_name': 'John',
                'last_name': 'Smith',
                'customer': 'CUST-001',
                'email_id': 'john@example.com',
                'mobile_no': 'invalid-phone'
            })
            contact.validate()
        
        print("✅ Contact validation test passed")
    
    def test_account_creation(self):
        """Test Account creation and validation"""
        print("🧪 Testing Account creation...")
        
        # Test valid account creation
        account_data = {
            'account_name': 'Acme Corporation',
            'account_type': 'Customer',
            'email': 'contact@acme.com',
            'phone': '+1-234-567-8900',
            'industry': 'Technology',
            'company_size': 'Large'
        }
        
        account = Account(account_data)
        account.validate()
        
        # Test account properties
        self.assertEqual(account.data['account_name'], 'Acme Corporation')
        self.assertEqual(account.data['account_type'], 'Customer')
        
        # Test account metrics
        self.assertIn('account_health_score', account.data)
        self.assertIn('account_value', account.data)
        self.assertIn('account_priority', account.data)
        
        print("✅ Account creation test passed")
    
    def test_customer_creation(self):
        """Test Customer creation and validation"""
        print("🧪 Testing Customer creation...")
        
        # Test valid customer creation
        customer_data = {
            'customer_name': 'TechStart Inc',
            'customer_type': 'Company',
            'email': 'info@techstart.com',
            'phone': '+1-234-567-8900',
            'industry': 'Technology',
            'company_size': 'Medium'
        }
        
        customer = Customer(customer_data)
        customer.validate()
        
        # Test customer properties
        self.assertEqual(customer.data['customer_name'], 'TechStart Inc')
        self.assertEqual(customer.data['customer_type'], 'Company')
        
        # Test customer metrics
        self.assertIn('health_score', customer.data)
        self.assertIn('churn_risk', customer.data)
        self.assertIn('total_spent', customer.data)
        self.assertIn('satisfaction', customer.data)
        
        print("✅ Customer creation test passed")

class TestDatabaseOperations(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Set up test database"""
        self.db_manager = DatabaseManager("sqlite:///:memory:")
    
    def test_database_connection(self):
        """Test database connection"""
        print("🧪 Testing database connection...")
        
        # Test database manager creation
        self.assertIsNotNone(self.db_manager)
        self.assertIsNotNone(self.db_manager.engine)
        
        # Test session creation
        session = self.db_manager.get_session()
        self.assertIsNotNone(session)
        session.close()
        
        print("✅ Database connection test passed")
    
    def test_database_models(self):
        """Test database models"""
        print("🧪 Testing database models...")
        
        # Test ContactModel
        contact_model = ContactModel(
            name='CON-001',
            first_name='John',
            last_name='Smith',
            email_id='john@example.com'
        )
        self.assertEqual(contact_model.first_name, 'John')
        self.assertEqual(contact_model.last_name, 'Smith')
        
        # Test AccountModel
        account_model = AccountModel(
            name='ACC-001',
            account_name='Acme Corp',
            account_type='Customer'
        )
        self.assertEqual(account_model.account_name, 'Acme Corp')
        self.assertEqual(account_model.account_type, 'Customer')
        
        # Test CustomerModel
        customer_model = CustomerModel(
            name='CUST-001',
            customer_name='TechStart',
            customer_type='Company'
        )
        self.assertEqual(customer_model.customer_name, 'TechStart')
        self.assertEqual(customer_model.customer_type, 'Company')
        
        print("✅ Database models test passed")

class TestAIFeatures(unittest.TestCase):
    """Test AI features"""
    
    def test_contact_metrics(self):
        """Test contact metrics calculation"""
        print("🧪 Testing contact metrics...")
        
        contact = Contact({
            'first_name': 'John',
            'last_name': 'Smith',
            'customer': 'CUST-001',
            'email_id': 'john@example.com'
        })
        
        # Test engagement score calculation
        engagement_score = contact.calculate_engagement_score()
        self.assertIsInstance(engagement_score, float)
        self.assertGreaterEqual(engagement_score, 0.0)
        self.assertLessEqual(engagement_score, 1.0)
        
        # Test influence score calculation
        influence_score = contact.calculate_influence_score()
        self.assertIsInstance(influence_score, float)
        self.assertGreaterEqual(influence_score, 0.0)
        self.assertLessEqual(influence_score, 1.0)
        
        print("✅ Contact metrics test passed")
    
    def test_customer_health_scoring(self):
        """Test customer health scoring"""
        print("🧪 Testing customer health scoring...")
        
        customer = Customer({
            'customer_name': 'TechStart Inc',
            'customer_type': 'Company',
            'email': 'info@techstart.com'
        })
        
        # Test health score calculation
        health_score = customer.calculate_health_score()
        self.assertIsInstance(health_score, float)
        self.assertGreaterEqual(health_score, 0.0)
        self.assertLessEqual(health_score, 1.0)
        
        # Test churn risk calculation
        churn_risk = customer.calculate_churn_risk()
        self.assertIn(churn_risk, ['Very Low', 'Low', 'Medium', 'High'])
        
        print("✅ Customer health scoring test passed")
    
    def test_insights_generation(self):
        """Test insights generation"""
        print("🧪 Testing insights generation...")
        
        contact = Contact({
            'first_name': 'John',
            'last_name': 'Smith',
            'customer': 'CUST-001',
            'email_id': 'john@example.com'
        })
        
        # Test insights generation
        insights = contact.generate_contact_insights()
        self.assertIsInstance(insights, dict)
        self.assertIn('contact_priority', insights)
        self.assertIn('engagement_level', insights)
        self.assertIn('influence_level', insights)
        self.assertIn('next_actions', insights)
        self.assertIn('relationship_stage', insights)
        
        print("✅ Insights generation test passed")

class TestIntegration(unittest.TestCase):
    """Test system integration"""
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow"""
        print("🧪 Testing end-to-end workflow...")
        
        # Create customer
        customer_data = {
            'customer_name': 'Integration Test Corp',
            'customer_type': 'Company',
            'email': 'test@integration.com',
            'phone': '+1-234-567-8900'
        }
        
        customer = Customer(customer_data)
        customer.validate()
        customer.save()
        
        # Create account
        account_data = {
            'account_name': 'Integration Test Corp',
            'account_type': 'Customer',
            'email': 'test@integration.com',
            'phone': '+1-234-567-8900'
        }
        
        account = Account(account_data)
        account.validate()
        account.save()
        
        # Create contact
        contact_data = {
            'first_name': 'Integration',
            'last_name': 'Test',
            'email_id': 'integration.test@integration.com',
            'customer': 'Integration Test Corp',
            'designation': 'CEO'
        }
        
        contact = Contact(contact_data)
        contact.validate()
        contact.save()
        
        # Verify all objects were created successfully
        self.assertIsNotNone(customer.name)
        self.assertIsNotNone(account.name)
        self.assertIsNotNone(contact.name)
        
        print("✅ End-to-end workflow test passed")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive Independent ERP System Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCoreInfrastructure,
        TestCRMModules,
        TestDatabaseOperations,
        TestAIFeatures,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if not result.failures and not result.errors:
        print("\n🎉 ALL TESTS PASSED! Independent ERP System is working perfectly!")
    else:
        print(f"\n⚠️  {len(result.failures + result.errors)} test(s) failed. Please review the issues above.")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
