# Independent Customer Class - Frappe-Free
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.base_document import BaseDocument
from core.validation import ValidationSystem
from core.utils import Utils
from core.database import db_manager
from typing import Dict, Any, List

class Customer(BaseDocument):
    """Frappe-independent Customer class"""
    
    def __init__(self, data: Dict[str, Any] = None):
        super().__init__(data)
    
    def validate(self):
        """Validate customer data"""
        self.validate_customer_data()
        self.set_defaults()
        self.calculate_customer_metrics()
        self.determine_customer_priority()
    
    def validate_customer_data(self):
        """Validate customer information"""
        ValidationSystem.validate_required(self.data.get('customer_name'), "Customer name")
        ValidationSystem.validate_required(self.data.get('customer_type'), "Customer type")
        
        if self.data.get('email') and not ValidationSystem.validate_email(self.data['email']):
            ValidationSystem.throw("Invalid email format")
        
        if self.data.get('phone') and not ValidationSystem.validate_phone(self.data['phone']):
            ValidationSystem.throw("Invalid phone number format")
    
    def set_defaults(self):
        """Set default values"""
        if not self.data.get('customer_status'):
            self.data['customer_status'] = "Active"
        if not self.data.get('customer_priority'):
            self.data['customer_priority'] = "Medium"
        if not self.data.get('customer_type'):
            self.data['customer_type'] = "Individual"
    
    def calculate_customer_metrics(self):
        """Calculate customer metrics"""
        self.data['health_score'] = self.calculate_health_score()
        self.data['churn_risk'] = self.calculate_churn_risk()
        self.data['total_spent'] = self.calculate_total_spent()
        self.data['satisfaction'] = self.calculate_satisfaction()
        self.data['last_activity'] = Utils.now()
    
    def calculate_health_score(self) -> float:
        """Calculate customer health score"""
        # Placeholder - implement actual logic
        return 0.85
    
    def calculate_churn_risk(self) -> str:
        """Calculate churn risk"""
        health_score = self.data.get('health_score', 0)
        if health_score >= 0.8:
            return "Very Low"
        elif health_score >= 0.6:
            return "Low"
        elif health_score >= 0.4:
            return "Medium"
        else:
            return "High"
    
    def calculate_total_spent(self) -> float:
        """Calculate total spent"""
        # Placeholder - implement actual logic
        return 50000.0
    
    def calculate_satisfaction(self) -> float:
        """Calculate satisfaction score"""
        # Placeholder - implement actual logic
        return 4.5
    
    def determine_customer_priority(self):
        """Determine customer priority"""
        health_score = self.data.get('health_score', 0)
        total_spent = self.data.get('total_spent', 0)
        
        if health_score >= 0.8 and total_spent >= 100000:
            self.data['customer_priority'] = "High"
        elif health_score >= 0.6 and total_spent >= 50000:
            self.data['customer_priority'] = "Medium"
        else:
            self.data['customer_priority'] = "Low"
    
    def before_save(self):
        """Process before saving"""
        self.update_customer_settings()
        self.setup_customer_permissions()
        self.generate_customer_insights()
    
    def after_insert(self):
        """Process after inserting"""
        self.create_customer_profile()
        self.setup_customer_workflow()
        self.create_customer_analytics()
        self.initialize_customer_tracking()
    
    def on_update(self):
        """Process on update"""
        self.update_customer_analytics()
        self.sync_customer_data()
        self.update_customer_priority()
        self.process_customer_changes()
    
    def update_customer_settings(self):
        """Update customer settings"""
        pass
    
    def setup_customer_permissions(self):
        """Setup customer permissions"""
        pass
    
    def generate_customer_insights(self):
        """Generate customer insights"""
        insights = {
            "customer_priority": self.data.get('customer_priority'),
            "health_level": self.determine_health_level(),
            "value_level": self.determine_value_level(),
            "growth_potential": self.analyze_growth_potential(),
            "next_actions": self.recommend_next_actions(),
            "relationship_stage": self.determine_relationship_stage()
        }
        self.data['customer_insights'] = insights
    
    def determine_health_level(self) -> str:
        """Determine health level"""
        score = self.data.get('health_score', 0)
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Poor"
    
    def determine_value_level(self) -> str:
        """Determine value level"""
        value = self.data.get('total_spent', 0)
        if value >= 1000000:
            return "Enterprise"
        elif value >= 100000:
            return "Large"
        elif value >= 10000:
            return "Medium"
        else:
            return "Small"
    
    def analyze_growth_potential(self) -> Dict:
        """Analyze growth potential"""
        return {
            "potential_score": 0.75,
            "growth_opportunities": ["Upsell", "Cross-sell", "Expansion"],
            "risk_factors": ["Competition", "Budget constraints"],
            "recommendations": ["Focus on high-value products", "Strengthen relationships"]
        }
    
    def recommend_next_actions(self) -> List[str]:
        """Recommend next actions"""
        priority = self.data.get('customer_priority', 'Medium')
        if priority == "High":
            return ["Schedule executive meeting", "Prepare custom proposal", "Monitor closely"]
        elif priority == "Medium":
            return ["Regular check-ins", "Identify growth opportunities", "Build relationships"]
        else:
            return ["Re-engage customer", "Understand needs", "Improve service"]
    
    def determine_relationship_stage(self) -> str:
        """Determine relationship stage"""
        health = self.data.get('health_score', 0)
        value = self.data.get('total_spent', 0)
        
        if health >= 0.8 and value >= 100000:
            return "Strategic Partner"
        elif health >= 0.6 and value >= 50000:
            return "Key Customer"
        elif health >= 0.4:
            return "Active Customer"
        else:
            return "Prospect"
    
    def create_customer_profile(self):
        """Create customer profile"""
        pass
    
    def setup_customer_workflow(self):
        """Setup customer workflow"""
        pass
    
    def create_customer_analytics(self):
        """Create customer analytics"""
        pass
    
    def initialize_customer_tracking(self):
        """Initialize customer tracking"""
        pass
    
    def update_customer_analytics(self):
        """Update customer analytics"""
        pass
    
    def sync_customer_data(self):
        """Sync customer data"""
        pass
    
    def update_customer_priority(self):
        """Update customer priority"""
        pass
    
    def process_customer_changes(self):
        """Process customer changes"""
        pass
