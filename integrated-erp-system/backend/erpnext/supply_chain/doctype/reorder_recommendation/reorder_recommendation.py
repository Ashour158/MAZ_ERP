# Reorder Recommendation with AI Intelligence

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days
import json
from datetime import datetime, timedelta
import random

class ReorderRecommendation(Document):
    def autoname(self):
        """Generate unique recommendation number"""
        if not self.recommendation_number:
            self.recommendation_number = frappe.generate_hash(length=8)
        self.name = self.recommendation_number

    def validate(self):
        """Validate recommendation data"""
        self.validate_quantities()
        self.calculate_ai_scores()
        self.set_defaults()

    def before_save(self):
        """Process before saving"""
        self.update_confidence_score()
        self.generate_explanation()
        self.check_urgency()

    def after_insert(self):
        """Process after inserting new recommendation"""
        self.send_notifications()
        self.update_analytics()

    def on_update(self):
        """Process on recommendation update"""
        self.log_status_change()
        self.update_ai_models()

    def validate_quantities(self):
        """Validate quantity recommendations"""
        if self.recommended_qty <= 0:
            frappe.throw(_("Recommended quantity must be greater than 0"))
        
        if self.recommended_qty > self.max_recommended_qty:
            frappe.msgprint(_("Recommended quantity exceeds maximum limit"))

    def calculate_ai_scores(self):
        """Calculate AI scores for the recommendation"""
        if not self.confidence_score:
            self.confidence_score = self.calculate_confidence()
        
        if not self.urgency_score:
            self.urgency_score = self.calculate_urgency()
        
        if not self.overall_score:
            self.overall_score = self.calculate_overall_score()

    def calculate_confidence(self):
        """Calculate confidence score using AI"""
        # This would integrate with ML models
        factors = {
            'historical_accuracy': 0.3,
            'demand_forecast_quality': 0.25,
            'vendor_reliability': 0.2,
            'market_conditions': 0.15,
            'seasonal_patterns': 0.1
        }
        
        # Simulate AI calculation
        confidence = 0
        for factor, weight in factors.items():
            confidence += random.uniform(0.6, 0.9) * weight
        
        return round(confidence, 2)

    def calculate_urgency(self):
        """Calculate urgency score"""
        urgency_factors = {
            'stockout_risk': 0.4,
            'lead_time': 0.3,
            'demand_volatility': 0.2,
            'supplier_capacity': 0.1
        }
        
        urgency = 0
        for factor, weight in urgency_factors.items():
            urgency += random.uniform(0.5, 1.0) * weight
        
        return round(urgency, 2)

    def calculate_overall_score(self):
        """Calculate overall recommendation score"""
        return round((self.confidence_score + self.urgency_score) / 2, 2)

    def set_defaults(self):
        """Set default values"""
        if not self.status:
            self.status = "Pending"
        
        if not self.recommendation_type:
            self.recommendation_type = "AI Generated"
        
        if not self.created_date:
            self.created_date = now()

    def update_confidence_score(self):
        """Update confidence score based on latest data"""
        # This would recalculate based on real-time data
        pass

    def generate_explanation(self):
        """Generate AI explanation for the recommendation"""
        explanations = []
        
        if self.urgency_score > 0.8:
            explanations.append("High urgency due to stockout risk")
        
        if self.confidence_score > 0.8:
            explanations.append("High confidence based on historical patterns")
        
        if self.demand_forecast_accuracy > 0.9:
            explanations.append("Excellent demand forecast accuracy")
        
        if self.vendor_reliability_score > 0.8:
            explanations.append("Reliable vendor with good performance")
        
        self.ai_explanation = json.dumps(explanations)

    def check_urgency(self):
        """Check if recommendation is urgent"""
        if self.urgency_score > 0.8:
            self.is_urgent = 1
            self.priority = "High"
        elif self.urgency_score > 0.6:
            self.priority = "Medium"
        else:
            self.priority = "Low"

    def send_notifications(self):
        """Send notifications for new recommendations"""
        # Send to procurement team
        procurement_users = frappe.get_all("User", 
            filters={"role_profile_name": "Procurement Manager"},
            fields=["email"]
        )
        
        for user in procurement_users:
            frappe.sendmail(
                recipients=[user.email],
                subject=f"New Reorder Recommendation: {self.item_code}",
                message=f"AI has generated a new reorder recommendation for {self.item_code}",
                reference_doctype=self.doctype,
                reference_name=self.name
            )

    def update_analytics(self):
        """Update analytics for the recommendation"""
        # Update item analytics
        if self.item_code:
            item_doc = frappe.get_doc("Item", self.item_code)
            if not hasattr(item_doc, 'ai_recommendations_count'):
                item_doc.ai_recommendations_count = 0
            item_doc.ai_recommendations_count += 1
            item_doc.save()

    def log_status_change(self):
        """Log status changes"""
        if self.has_value_changed('status'):
            frappe.get_doc({
                "doctype": "Supply Chain Communication",
                "recommendation_id": self.name,
                "communication_type": "Status Change",
                "content": f"Status changed to {self.status}",
                "created_by": frappe.session.user
            }).insert()

    def update_ai_models(self):
        """Update AI models with new data"""
        # This would feed data back to ML models for improvement
        pass

    def approve_recommendation(self):
        """Approve the recommendation"""
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approved_at = now()
        self.save()
        
        # Create purchase requisition
        self.create_purchase_requisition()

    def reject_recommendation(self, reason):
        """Reject the recommendation"""
        self.status = "Rejected"
        self.rejection_reason = reason
        self.rejected_by = frappe.session.user
        self.rejected_at = now()
        self.save()

    def create_purchase_requisition(self):
        """Create purchase requisition from approved recommendation"""
        pr_doc = frappe.get_doc({
            "doctype": "Purchase Requisition",
            "company": self.company,
            "transaction_date": now().date(),
            "items": [{
                "item_code": self.item_code,
                "qty": self.recommended_qty,
                "warehouse": self.warehouse,
                "required_date": self.required_date,
                "description": f"AI Generated Recommendation: {self.recommendation_number}"
            }]
        })
        
        pr_doc.insert()
        pr_doc.submit()
        
        self.purchase_requisition = pr_doc.name
        self.save()

    def get_alternative_recommendations(self):
        """Get alternative recommendations"""
        alternatives = []
        
        # Get different quantity scenarios
        if self.recommended_qty > self.min_order_qty:
            alternatives.append({
                "scenario": "Minimum Order",
                "quantity": self.min_order_qty,
                "cost": self.unit_cost * self.min_order_qty,
                "pros": ["Lower upfront cost", "Reduced inventory risk"],
                "cons": ["May not meet demand", "Higher per-unit cost"]
            })
        
        # Get maximum order scenario
        if self.max_recommended_qty > self.recommended_qty:
            alternatives.append({
                "scenario": "Maximum Order",
                "quantity": self.max_recommended_qty,
                "cost": self.unit_cost * self.max_recommended_qty,
                "pros": ["Volume discounts", "Reduced ordering frequency"],
                "cons": ["Higher upfront cost", "Increased inventory risk"]
            })
        
        return alternatives

    def get_performance_metrics(self):
        """Get performance metrics for the recommendation"""
        metrics = {
            "accuracy_score": None,
            "cost_savings": None,
            "stockout_prevention": None,
            "vendor_performance": None
        }
        
        # Calculate accuracy if recommendation was implemented
        if self.status == "Approved" and self.actual_demand:
            demand_variance = abs(self.actual_demand - self.forecasted_demand) / self.forecasted_demand
            metrics["accuracy_score"] = max(0, 1 - demand_variance)
        
        # Calculate cost savings
        if self.unit_cost and self.alternative_cost:
            savings = (self.alternative_cost - self.unit_cost) * self.recommended_qty
            metrics["cost_savings"] = savings
        
        return metrics

@frappe.whitelist()
def generate_bulk_recommendations(filters=None):
    """Generate bulk reorder recommendations"""
    if not filters:
        filters = {}
    
    # Get items that need reorder recommendations
    items = frappe.get_all("Item",
        filters={
            "is_stock_item": 1,
            "disabled": 0
        },
        fields=["name", "item_code", "item_name"]
    )
    
    recommendations = []
    
    for item in items:
        # Check if item needs reorder
        if should_reorder_item(item.name):
            recommendation = create_reorder_recommendation(item.name)
            if recommendation:
                recommendations.append(recommendation)
    
    return recommendations

def should_reorder_item(item_code):
    """Check if item needs reorder recommendation"""
    # Get current stock
    stock_balance = frappe.get_all("Bin",
        filters={"item_code": item_code},
        fields=["sum(actual_qty) as total_qty"]
    )
    
    if stock_balance and stock_balance[0].total_qty:
        current_stock = stock_balance[0].total_qty
    else:
        current_stock = 0
    
    # Get reorder level
    reorder_level = frappe.get_value("Item", item_code, "reorder_level") or 0
    
    return current_stock <= reorder_level

def create_reorder_recommendation(item_code):
    """Create reorder recommendation for item"""
    try:
        # Get item details
        item = frappe.get_doc("Item", item_code)
        
        # Calculate recommended quantity using AI
        recommended_qty = calculate_ai_reorder_quantity(item_code)
        
        if recommended_qty <= 0:
            return None
        
        # Create recommendation
        recommendation = frappe.get_doc({
            "doctype": "Reorder Recommendation",
            "item_code": item_code,
            "item_name": item.item_name,
            "warehouse": get_default_warehouse(),
            "recommended_qty": recommended_qty,
            "unit_cost": get_item_cost(item_code),
            "total_cost": recommended_qty * get_item_cost(item_code),
            "required_date": add_days(now().date(), 7),
            "company": frappe.defaults.get_user_default("Company")
        })
        
        recommendation.insert()
        return recommendation.name
        
    except Exception as e:
        frappe.log_error(f"Error creating reorder recommendation for {item_code}: {str(e)}")
        return None

def calculate_ai_reorder_quantity(item_code):
    """Calculate AI-powered reorder quantity"""
    # This would integrate with ML models
    # For now, using simple logic
    
    # Get historical demand
    historical_demand = get_historical_demand(item_code)
    
    # Get lead time
    lead_time = get_lead_time(item_code)
    
    # Get safety stock
    safety_stock = get_safety_stock(item_code)
    
    # Calculate reorder quantity
    avg_demand = sum(historical_demand) / len(historical_demand) if historical_demand else 0
    reorder_qty = (avg_demand * lead_time) + safety_stock
    
    return max(reorder_qty, 1)

def get_historical_demand(item_code, days=30):
    """Get historical demand for item"""
    # This would query actual stock movements
    # For now, returning mock data
    import random
    return [random.randint(10, 100) for _ in range(days)]

def get_lead_time(item_code):
    """Get lead time for item"""
    # This would query supplier data
    return 7  # Default 7 days

def get_safety_stock(item_code):
    """Get safety stock for item"""
    # This would calculate based on demand variability
    return 20  # Default safety stock

def get_default_warehouse():
    """Get default warehouse"""
    return frappe.get_value("Warehouse", {"is_group": 0}, "name") or "Stores - W"

def get_item_cost(item_code):
    """Get item cost"""
    return frappe.get_value("Item", item_code, "valuation_rate") or 0

@frappe.whitelist()
def get_recommendation_analytics(filters=None):
    """Get recommendation analytics"""
    if not filters:
        filters = {}
    
    # Get recommendation statistics
    stats = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_recommendations,
            SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) as approved_recommendations,
            SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) as rejected_recommendations,
            SUM(CASE WHEN is_urgent = 1 THEN 1 ELSE 0 END) as urgent_recommendations,
            AVG(confidence_score) as avg_confidence,
            AVG(urgency_score) as avg_urgency,
            SUM(total_cost) as total_recommended_cost
        FROM `tabReorder Recommendation`
        WHERE creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    """, as_dict=True)
    
    return stats[0] if stats else {}

@frappe.whitelist()
def approve_bulk_recommendations(recommendation_ids):
    """Approve multiple recommendations"""
    if isinstance(recommendation_ids, str):
        recommendation_ids = json.loads(recommendation_ids)
    
    approved_count = 0
    
    for rec_id in recommendation_ids:
        try:
            rec = frappe.get_doc("Reorder Recommendation", rec_id)
            rec.approve_recommendation()
            approved_count += 1
        except Exception as e:
            frappe.log_error(f"Error approving recommendation {rec_id}: {str(e)}")
    
    frappe.msgprint(f"Approved {approved_count} recommendations")
    return approved_count
