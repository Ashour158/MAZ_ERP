# Independent Maintenance Ticket Class - Frappe-Free
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.base_document import BaseDocument
from core.validation import ValidationSystem
from core.utils import Utils
from typing import Dict, Any, List

class MaintenanceTicket(BaseDocument):
    """Frappe-independent Maintenance Ticket class"""
    
    def __init__(self, data: Dict[str, Any] = None):
        super().__init__(data)
    
    def validate(self):
        """Validate maintenance ticket data"""
        self.validate_ticket_data()
        self.set_defaults()
        self.calculate_ai_insights()
        self.setup_maintenance_features()
    
    def validate_ticket_data(self):
        """Validate maintenance ticket information"""
        ValidationSystem.validate_required(self.data.get('title'), "Title")
        ValidationSystem.validate_required(self.data.get('description'), "Description")
        ValidationSystem.validate_required(self.data.get('priority'), "Priority")
        
        if self.data.get('customer_email') and not ValidationSystem.validate_email(self.data['customer_email']):
            ValidationSystem.throw("Invalid customer email format")
    
    def set_defaults(self):
        """Set default values"""
        if not self.data.get('status'):
            self.data['status'] = "Open"
        if not self.data.get('ticket_id'):
            self.data['ticket_id'] = Utils.make_autoname("TKT-.YYYY.-.#####")
        if not self.data.get('created_date'):
            self.data['created_date'] = Utils.now().isoformat()
    
    def calculate_ai_insights(self):
        """Calculate AI-powered insights"""
        self.data['ai_insights'] = {
            'failure_prediction': self.predict_failure_probability(),
            'maintenance_schedule': self.suggest_maintenance_schedule(),
            'recommended_actions': self.get_recommended_actions(),
            'risk_level': self.assess_risk_level(),
            'optimization_score': self.calculate_optimization_score()
        }
    
    def predict_failure_probability(self) -> float:
        """Predict failure probability using AI"""
        # Placeholder - implement actual AI logic
        return 0.25
    
    def suggest_maintenance_schedule(self) -> str:
        """Suggest maintenance schedule"""
        # Placeholder - implement actual AI logic
        return "2024-02-01"
    
    def get_recommended_actions(self) -> List[str]:
        """Get AI-recommended actions"""
        # Placeholder - implement actual AI logic
        return ["Check connections", "Update firmware", "Clean components"]
    
    def assess_risk_level(self) -> str:
        """Assess risk level"""
        failure_prob = self.data['ai_insights']['failure_prediction']
        if failure_prob > 0.7:
            return "High"
        elif failure_prob > 0.4:
            return "Medium"
        else:
            return "Low"
    
    def calculate_optimization_score(self) -> float:
        """Calculate optimization score"""
        # Placeholder - implement actual AI logic
        return 0.78
    
    def setup_maintenance_features(self):
        """Setup maintenance features"""
        self.data['maintenance_features'] = {
            'predictive_maintenance': True,
            'ai_recommendations': True,
            'failure_prediction': True,
            'optimization_suggestions': True,
            'scheduling_automation': True,
            'cost_optimization': True
        }
    
    def schedule_maintenance(self, schedule_data: Dict):
        """Schedule maintenance"""
        schedule = {
            'ticket_id': self.data['ticket_id'],
            'scheduled_date': schedule_data.get('scheduled_date'),
            'scheduled_time': schedule_data.get('scheduled_time'),
            'duration': schedule_data.get('duration', 2),
            'technician': schedule_data.get('technician'),
            'location': schedule_data.get('location'),
            'status': 'Scheduled'
        }
        
        # Add to ticket's maintenance schedule
        if 'maintenance_schedule' not in self.data:
            self.data['maintenance_schedule'] = []
        
        self.data['maintenance_schedule'].append(schedule)
        return schedule
    
    def record_maintenance_action(self, action_data: Dict):
        """Record maintenance action"""
        action = {
            'ticket_id': self.data['ticket_id'],
            'action_type': action_data.get('action_type'),
            'description': action_data.get('description'),
            'performed_by': action_data.get('performed_by'),
            'performed_date': Utils.now().isoformat(),
            'duration': action_data.get('duration', 1),
            'status': 'Completed'
        }
        
        # Add to ticket's maintenance history
        if 'maintenance_history' not in self.data:
            self.data['maintenance_history'] = []
        
        self.data['maintenance_history'].append(action)
        return action
    
    def update_ticket_status(self, new_status: str, notes: str = ""):
        """Update ticket status"""
        status_update = {
            'ticket_id': self.data['ticket_id'],
            'old_status': self.data.get('status'),
            'new_status': new_status,
            'updated_by': 'system',
            'updated_date': Utils.now().isoformat(),
            'notes': notes
        }
        
        self.data['status'] = new_status
        
        # Add to ticket's status history
        if 'status_history' not in self.data:
            self.data['status_history'] = []
        
        self.data['status_history'].append(status_update)
        return status_update
    
    def assign_technician(self, technician_data: Dict):
        """Assign technician to ticket"""
        assignment = {
            'ticket_id': self.data['ticket_id'],
            'technician_id': technician_data.get('technician_id'),
            'technician_name': technician_data.get('technician_name'),
            'assigned_date': Utils.now().isoformat(),
            'assigned_by': technician_data.get('assigned_by'),
            'status': 'Assigned'
        }
        
        self.data['assigned_technician'] = technician_data.get('technician_id')
        
        # Add to ticket's assignment history
        if 'assignment_history' not in self.data:
            self.data['assignment_history'] = []
        
        self.data['assignment_history'].append(assignment)
        return assignment
    
    def add_parts_used(self, parts_data: Dict):
        """Add parts used in maintenance"""
        parts = {
            'ticket_id': self.data['ticket_id'],
            'part_code': parts_data.get('part_code'),
            'part_name': parts_data.get('part_name'),
            'quantity': parts_data.get('quantity', 1),
            'unit_cost': parts_data.get('unit_cost', 0),
            'total_cost': parts_data.get('quantity', 1) * parts_data.get('unit_cost', 0),
            'used_date': Utils.now().isoformat()
        }
        
        # Add to ticket's parts used
        if 'parts_used' not in self.data:
            self.data['parts_used'] = []
        
        self.data['parts_used'].append(parts)
        return parts
    
    def calculate_maintenance_cost(self) -> float:
        """Calculate total maintenance cost"""
        total_cost = 0
        
        # Add labor cost
        if 'maintenance_history' in self.data:
            for action in self.data['maintenance_history']:
                total_cost += action.get('labor_cost', 0)
        
        # Add parts cost
        if 'parts_used' in self.data:
            for part in self.data['parts_used']:
                total_cost += part.get('total_cost', 0)
        
        return total_cost
    
    def get_maintenance_analytics(self) -> Dict:
        """Get maintenance analytics"""
        return {
            'total_cost': self.calculate_maintenance_cost(),
            'maintenance_duration': self.calculate_maintenance_duration(),
            'parts_used_count': len(self.data.get('parts_used', [])),
            'actions_performed': len(self.data.get('maintenance_history', [])),
            'ai_confidence': self.data['ai_insights']['optimization_score'],
            'risk_level': self.data['ai_insights']['risk_level']
        }
    
    def calculate_maintenance_duration(self) -> float:
        """Calculate total maintenance duration"""
        total_duration = 0
        
        if 'maintenance_history' in self.data:
            for action in self.data['maintenance_history']:
                total_duration += action.get('duration', 0)
        
        return total_duration
