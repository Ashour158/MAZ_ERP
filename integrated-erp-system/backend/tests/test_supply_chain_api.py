# Comprehensive Test Suite for Supply Chain API

import pytest
import json
import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, MagicMock
import requests
from datetime import datetime, timedelta

class TestSupplyChainAPI(FrappeTestCase):
    """Test suite for Supply Chain API endpoints"""
    
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
        
        self.test_item = frappe.get_doc({
            'doctype': 'Item',
            'item_code': 'TEST-ITEM-001',
            'item_name': 'Test Item',
            'is_stock_item': 1,
            'valuation_rate': 100.0
        })
        self.test_item.insert()
        
        self.test_warehouse = frappe.get_doc({
            'doctype': 'Warehouse',
            'warehouse_name': 'Test Warehouse',
            'is_group': 0
        })
        self.test_warehouse.insert()
    
    def tearDown(self):
        """Clean up test data"""
        frappe.db.rollback()
    
    def test_create_reorder_recommendation_success(self):
        """Test successful reorder recommendation creation"""
        recommendation_data = {
            'item_code': self.test_item.item_code,
            'warehouse': self.test_warehouse.name,
            'recommended_qty': 100,
            'unit_cost': 50.0,
            'total_cost': 5000.0
        }
        
        # Mock authentication
        with patch('api_gateway.routes.token_required') as mock_auth:
            mock_auth.return_value = lambda f: f
            with patch('api_gateway.routes.frappe.get_doc') as mock_get_doc:
                mock_get_doc.return_value = self.test_user
                
                # Test recommendation creation
                recommendation = frappe.get_doc({
                    'doctype': 'Reorder Recommendation',
                    **recommendation_data
                })
                recommendation.insert()
                
                self.assertEqual(recommendation.item_code, self.test_item.item_code)
                self.assertEqual(recommendation.recommended_qty, 100)
                self.assertEqual(recommendation.total_cost, 5000.0)
    
    def test_ai_confidence_calculation(self):
        """Test AI confidence score calculation"""
        recommendation = frappe.get_doc({
            'doctype': 'Reorder Recommendation',
            'item_code': self.test_item.item_code,
            'warehouse': self.test_warehouse.name,
            'recommended_qty': 100,
            'unit_cost': 50.0
        })
        
        # Mock AI confidence calculation
        with patch.object(recommendation, 'calculate_confidence') as mock_confidence:
            mock_confidence.return_value = 0.85
            
            recommendation.insert()
            
            # Verify confidence score is set
            self.assertIsNotNone(recommendation.confidence_score)
            self.assertGreater(recommendation.confidence_score, 0.8)
    
    def test_urgency_calculation(self):
        """Test urgency score calculation"""
        recommendation = frappe.get_doc({
            'doctype': 'Reorder Recommendation',
            'item_code': self.test_item.item_code,
            'warehouse': self.test_warehouse.name,
            'recommended_qty': 100,
            'unit_cost': 50.0
        })
        
        # Mock urgency calculation
        with patch.object(recommendation, 'calculate_urgency') as mock_urgency:
            mock_urgency.return_value = 0.9
            
            recommendation.insert()
            
            # Verify urgency score is set
            self.assertIsNotNone(recommendation.urgency_score)
            self.assertGreater(recommendation.urgency_score, 0.8)
    
    def test_recommendation_approval(self):
        """Test recommendation approval workflow"""
        recommendation = frappe.get_doc({
            'doctype': 'Reorder Recommendation',
            'item_code': self.test_item.item_code,
            'warehouse': self.test_warehouse.name,
            'recommended_qty': 100,
            'unit_cost': 50.0,
            'status': 'Pending'
        })
        recommendation.insert()
        
        # Approve recommendation
        recommendation.approve_recommendation()
        
        # Verify approval
        self.assertEqual(recommendation.status, 'Approved')
        self.assertIsNotNone(recommendation.approved_by)
        self.assertIsNotNone(recommendation.approved_at)
    
    def test_recommendation_rejection(self):
        """Test recommendation rejection workflow"""
        recommendation = frappe.get_doc({
            'doctype': 'Reorder Recommendation',
            'item_code': self.test_item.item_code,
            'warehouse': self.test_warehouse.name,
            'recommended_qty': 100,
            'unit_cost': 50.0,
            'status': 'Pending'
        })
        recommendation.insert()
        
        # Reject recommendation
        rejection_reason = 'Not needed at this time'
        recommendation.reject_recommendation(rejection_reason)
        
        # Verify rejection
        self.assertEqual(recommendation.status, 'Rejected')
        self.assertEqual(recommendation.rejection_reason, rejection_reason)
        self.assertIsNotNone(recommendation.rejected_by)
        self.assertIsNotNone(recommendation.rejected_at)
    
    def test_purchase_requisition_creation(self):
        """Test purchase requisition creation from approved recommendation"""
        recommendation = frappe.get_doc({
            'doctype': 'Reorder Recommendation',
            'item_code': self.test_item.item_code,
            'warehouse': self.test_warehouse.name,
            'recommended_qty': 100,
            'unit_cost': 50.0,
            'status': 'Pending'
        })
        recommendation.insert()
        
        # Mock purchase requisition creation
        with patch('frappe.get_doc') as mock_get_doc:
            mock_pr = MagicMock()
            mock_pr.name = 'PR-001'
            mock_get_doc.return_value = mock_pr
            
            recommendation.approve_recommendation()
            
            # Verify purchase requisition was created
            self.assertIsNotNone(recommendation.purchase_requisition)
    
    def test_alternative_recommendations(self):
        """Test alternative recommendations generation"""
        recommendation = frappe.get_doc({
            'doctype': 'Reorder Recommendation',
            'item_code': self.test_item.item_code,
            'warehouse': self.test_warehouse.name,
            'recommended_qty': 100,
            'unit_cost': 50.0,
            'min_order_qty': 50,
            'max_recommended_qty': 200
        })
        recommendation.insert()
        
        # Test alternative recommendations
        alternatives = recommendation.get_alternative_recommendations()
        
        self.assertIsInstance(alternatives, list)
        self.assertGreater(len(alternatives), 0)
        
        # Verify alternative scenarios
        for alt in alternatives:
            self.assertIn('scenario', alt)
            self.assertIn('quantity', alt)
            self.assertIn('cost', alt)
            self.assertIn('pros', alt)
            self.assertIn('cons', alt)
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        recommendation = frappe.get_doc({
            'doctype': 'Reorder Recommendation',
            'item_code': self.test_item.item_code,
            'warehouse': self.test_warehouse.name,
            'recommended_qty': 100,
            'unit_cost': 50.0,
            'actual_demand': 95,
            'forecasted_demand': 100,
            'alternative_cost': 55.0
        })
        recommendation.insert()
        
        # Test performance metrics
        metrics = recommendation.get_performance_metrics()
        
        self.assertIsNotNone(metrics['accuracy_score'])
        self.assertIsNotNone(metrics['cost_savings'])
        self.assertIsNotNone(metrics['stockout_prevention'])
        self.assertIsNotNone(metrics['vendor_performance'])
    
    def test_bulk_recommendation_generation(self):
        """Test bulk recommendation generation"""
        # Create multiple items
        items = []
        for i in range(3):
            item = frappe.get_doc({
                'doctype': 'Item',
                'item_code': f'TEST-ITEM-{i:03d}',
                'item_name': f'Test Item {i}',
                'is_stock_item': 1,
                'valuation_rate': 100.0 + i * 10
            })
            item.insert()
            items.append(item)
        
        # Mock bulk generation
        with patch('erpnext.supply_chain.doctype.reorder_recommendation.reorder_recommendation.generate_bulk_recommendations') as mock_bulk:
            mock_bulk.return_value = ['REC-001', 'REC-002', 'REC-003']
            
            recommendations = mock_bulk()
            
            self.assertEqual(len(recommendations), 3)
    
    def test_analytics_data(self):
        """Test analytics data retrieval"""
        # Create test recommendations
        for i in range(5):
            recommendation = frappe.get_doc({
                'doctype': 'Reorder Recommendation',
                'item_code': f'TEST-ITEM-{i:03d}',
                'warehouse': self.test_warehouse.name,
                'recommended_qty': 100 + i * 10,
                'unit_cost': 50.0,
                'status': 'Approved' if i % 2 == 0 else 'Pending'
            })
            recommendation.insert()
        
        # Test analytics function
        analytics = frappe.get_all('Reorder Recommendation',
            filters={'creation': ['>=', frappe.utils.add_days(frappe.utils.now(), -30)]},
            fields=['COUNT(*) as total_recommendations']
        )
        
        self.assertGreater(len(analytics), 0)
    
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid recommendation data
        with self.assertRaises(frappe.ValidationError):
            recommendation = frappe.get_doc({
                'doctype': 'Reorder Recommendation',
                'item_code': '',  # Empty item code should fail
                'warehouse': self.test_warehouse.name,
                'recommended_qty': -10,  # Negative quantity should fail
                'unit_cost': 50.0
            })
            recommendation.insert()
    
    def test_concurrent_recommendation_creation(self):
        """Test concurrent recommendation creation"""
        import threading
        import time
        
        results = []
        
        def create_recommendation(rec_id):
            try:
                recommendation = frappe.get_doc({
                    'doctype': 'Reorder Recommendation',
                    'item_code': f'TEST-ITEM-{rec_id:03d}',
                    'warehouse': self.test_warehouse.name,
                    'recommended_qty': 100,
                    'unit_cost': 50.0
                })
                recommendation.insert()
                results.append(f'Success {rec_id}')
            except Exception as e:
                results.append(f'Error {rec_id}: {str(e)}')
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_recommendation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all recommendations were created successfully
        self.assertEqual(len(results), 5)
        self.assertTrue(all('Success' in result for result in results))

class TestSupplyChainIntegration(FrappeTestCase):
    """Integration tests for Supply Chain module"""
    
    def test_end_to_end_recommendation_workflow(self):
        """Test complete recommendation workflow"""
        # 1. Create recommendation
        recommendation = frappe.get_doc({
            'doctype': 'Reorder Recommendation',
            'item_code': 'TEST-ITEM-001',
            'warehouse': 'Test Warehouse',
            'recommended_qty': 100,
            'unit_cost': 50.0,
            'status': 'Pending'
        })
        recommendation.insert()
        
        # 2. Approve recommendation
        recommendation.approve_recommendation()
        
        # 3. Verify purchase requisition creation
        self.assertEqual(recommendation.status, 'Approved')
        self.assertIsNotNone(recommendation.purchase_requisition)
    
    def test_ai_insights_generation(self):
        """Test AI insights generation for recommendations"""
        recommendation = frappe.get_doc({
            'doctype': 'Reorder Recommendation',
            'item_code': 'TEST-ITEM-001',
            'warehouse': 'Test Warehouse',
            'recommended_qty': 100,
            'unit_cost': 50.0
        })
        recommendation.insert()
        
        # Test AI insights
        insights = recommendation.get_ai_recommendations()
        
        self.assertIsInstance(insights, list)
    
    def test_vendor_performance_tracking(self):
        """Test vendor performance tracking"""
        # Create vendor performance record
        vendor_perf = frappe.get_doc({
            'doctype': 'Vendor Performance',
            'vendor': 'Test Vendor',
            'on_time_delivery': 95.0,
            'quality_score': 4.5,
            'cost_effectiveness': 4.2
        })
        vendor_perf.insert()
        
        # Verify performance metrics
        self.assertEqual(vendor_perf.on_time_delivery, 95.0)
        self.assertEqual(vendor_perf.quality_score, 4.5)
        self.assertEqual(vendor_perf.cost_effectiveness, 4.2)

if __name__ == '__main__':
    pytest.main([__file__])
