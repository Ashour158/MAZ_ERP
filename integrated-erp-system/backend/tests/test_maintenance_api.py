# Comprehensive Test Suite for Maintenance API

import pytest
import json
import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, MagicMock
import requests
from datetime import datetime, timedelta

class TestMaintenanceAPI(FrappeTestCase):
    """Test suite for Maintenance API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.test_user = frappe.get_doc({
            'doctype': 'User',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'enabled': 1
        })
        self.test_user.insert()
        
        self.test_customer = frappe.get_doc({
            'doctype': 'Customer',
            'customer_name': 'Test Customer',
            'customer_type': 'Individual'
        })
        self.test_customer.insert()
    
    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()
    
    def test_create_ticket_success(self):
        """Test successful ticket creation"""
        ticket_data = {
            'subject': 'Test Ticket',
            'description': 'Test Description',
            'priority': 'Medium',
            'customer': self.test_customer.name,
            'ticket_type': 'Support'
        }
        
        # Mock authentication
        with patch('api_gateway.routes.token_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            with patch('api_gateway.routes.frappe.get_doc') as mock_get_doc:
                mock_get_doc.return_value = self.test_user
                
                # Test ticket creation
                ticket = frappe.get_doc({
                    'doctype': 'Maintenance Ticket',
                    **ticket_data
                })
                ticket.insert()
                
                self.assertEqual(ticket.subject, 'Test Ticket')
                self.assertEqual(ticket.priority, 'Medium')
                self.assertEqual(ticket.customer, self.test_customer.name)
    
    def test_ticket_validation_rules(self):
        """Test ticket validation rules"""
        # Test critical ticket without assignment
        ticket = frappe.get_doc({
            'doctype': 'Maintenance Ticket',
            'subject': 'Critical Issue',
            'description': 'Critical system failure',
            'priority': 'Critical',
            'customer': self.test_customer.name
        })
        
        with self.assertRaises(frappe.ValidationError):
            ticket.insert()
    
    def test_ai_sentiment_analysis(self):
        """Test AI sentiment analysis"""
        ticket = frappe.get_doc({
            'doctype': 'Maintenance Ticket',
            'subject': 'Urgent Issue',
            'description': 'This is a very urgent and critical problem that needs immediate attention!',
            'priority': 'Medium',
            'customer': self.test_customer.name
        })
        
        # Mock AI sentiment calculation
        with patch.object(ticket, 'analyze_sentiment') as mock_sentiment:
            mock_sentiment.return_value = 0.2  # Negative sentiment
            
            ticket.insert()
            
            # Verify sentiment score is set
            self.assertIsNotNone(ticket.ai_sentiment_score)
            self.assertLess(ticket.ai_sentiment_score, 0.5)
    
    def test_sla_status_calculation(self):
        """Test SLA status calculation"""
        ticket = frappe.get_doc({
            'doctype': 'Maintenance Ticket',
            'subject': 'SLA Test',
            'description': 'Testing SLA calculation',
            'priority': 'High',
            'customer': self.test_customer.name,
            'expected_resolution': datetime.now() + timedelta(hours=2)
        })
        
        ticket.insert()
        
        # Test SLA status update
        ticket.update_sla_status()
        
        # Verify SLA status is calculated
        self.assertIn(ticket.sla_status, ['On Track', 'At Risk', 'Breached'])
    
    def test_escalation_logic(self):
        """Test ticket escalation logic"""
        ticket = frappe.get_doc({
            'doctype': 'Maintenance Ticket',
            'subject': 'Escalation Test',
            'description': 'Testing escalation',
            'priority': 'Medium',
            'customer': self.test_customer.name
        })
        
        ticket.insert()
        
        # Simulate SLA breach
        ticket.sla_status = 'Breached'
        ticket.check_escalation()
        
        # Verify escalation
        self.assertTrue(ticket.escalated)
        self.assertEqual(ticket.priority, 'High')
    
    def test_notification_sending(self):
        """Test notification sending"""
        ticket = frappe.get_doc({
            'doctype': 'Maintenance Ticket',
            'subject': 'Notification Test',
            'description': 'Testing notifications',
            'priority': 'Medium',
            'customer': self.test_customer.name,
            'assigned_to': self.test_user.email
        })
        
        with patch('frappe.sendmail') as mock_sendmail:
            ticket.insert()
            
            # Verify notifications were sent
            self.assertTrue(mock_sendmail.called)
    
    def test_analytics_data(self):
        """Test analytics data retrieval"""
        # Create test tickets
        for i in range(5):
            ticket = frappe.get_doc({
                'doctype': 'Maintenance Ticket',
                'subject': f'Test Ticket {i}',
                'description': f'Test Description {i}',
                'priority': 'Medium',
                'customer': self.test_customer.name,
                'status': 'Open' if i % 2 == 0 else 'Closed'
            })
            ticket.insert()
        
        # Test analytics function
        analytics = frappe.get_all('Maintenance Ticket',
            filters={'creation': ['>=', frappe.utils.add_days(frappe.utils.now(), -30)]},
            fields=['COUNT(*) as total_tickets']
        )
        
        self.assertGreater(len(analytics), 0)
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        ticket = frappe.get_doc({
            'doctype': 'Maintenance Ticket',
            'subject': 'Performance Test',
            'description': 'Testing performance metrics',
            'priority': 'Medium',
            'customer': self.test_customer.name,
            'first_response_time': datetime.now() + timedelta(hours=1),
            'resolution_time': datetime.now() + timedelta(hours=4)
        })
        
        ticket.insert()
        
        # Test performance metrics
        metrics = ticket.get_performance_metrics()
        
        self.assertIsNotNone(metrics['time_to_first_response'])
        self.assertIsNotNone(metrics['time_to_resolution'])
    
    def test_ai_insights_generation(self):
        """Test AI insights generation"""
        ticket = frappe.get_doc({
            'doctype': 'Maintenance Ticket',
            'subject': 'AI Insights Test',
            'description': 'Testing AI insights generation with urgent keywords',
            'priority': 'Medium',
            'customer': self.test_customer.name
        })
        
        ticket.insert()
        
        # Test AI insights
        insights = ticket.get_ai_recommendations()
        
        self.assertIsInstance(insights, list)
    
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid ticket data
        with self.assertRaises(frappe.ValidationError):
            ticket = frappe.get_doc({
                'doctype': 'Maintenance Ticket',
                'subject': '',  # Empty subject should fail
                'description': 'Test',
                'priority': 'Medium'
            })
            ticket.insert()
    
    def test_concurrent_ticket_creation(self):
        """Test concurrent ticket creation"""
        import threading
        import time
        
        results = []
        
        def create_ticket(ticket_id):
            try:
                ticket = frappe.get_doc({
                    'doctype': 'Maintenance Ticket',
                    'subject': f'Concurrent Ticket {ticket_id}',
                    'description': f'Concurrent test {ticket_id}',
                    'priority': 'Medium',
                    'customer': self.test_customer.name
                })
                ticket.insert()
                results.append(f'Success {ticket_id}')
            except Exception as e:
                results.append(f'Error {ticket_id}: {str(e)}')
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_ticket, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all tickets were created successfully
        self.assertEqual(len(results), 5)
        self.assertTrue(all('Success' in result for result in results))

class TestMaintenanceIntegration(FrappeTestCase):
    """Integration tests for Maintenance module"""
    
    def test_end_to_end_ticket_workflow(self):
        """Test complete ticket workflow"""
        # 1. Create ticket
        ticket = frappe.get_doc({
            'doctype': 'Maintenance Ticket',
            'subject': 'End-to-End Test',
            'description': 'Complete workflow test',
            'priority': 'High',
            'customer': 'Test Customer'
        })
        ticket.insert()
        
        # 2. Assign ticket
        ticket.assigned_to = 'test@example.com'
        ticket.save()
        
        # 3. Update status
        ticket.status = 'In Progress'
        ticket.save()
        
        # 4. Add resolution
        ticket.resolution = 'Issue resolved'
        ticket.status = 'Closed'
        ticket.save()
        
        # Verify final state
        self.assertEqual(ticket.status, 'Closed')
        self.assertIsNotNone(ticket.resolution)
    
    def test_sla_breach_scenario(self):
        """Test SLA breach scenario"""
        # Create ticket with past expected resolution
        ticket = frappe.get_doc({
            'doctype': 'Maintenance Ticket',
            'subject': 'SLA Breach Test',
            'description': 'Testing SLA breach',
            'priority': 'High',
            'customer': 'Test Customer',
            'expected_resolution': datetime.now() - timedelta(hours=1)
        })
        ticket.insert()
        
        # Update SLA status
        ticket.update_sla_status()
        
        # Verify breach detection
        self.assertEqual(ticket.sla_status, 'Breached')
        self.assertTrue(ticket.escalated)

if __name__ == '__main__':
    pytest.main([__file__])
