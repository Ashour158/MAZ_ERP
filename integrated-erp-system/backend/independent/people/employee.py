# Independent Employee Class - Frappe-Free
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.base_document import BaseDocument
from core.validation import ValidationSystem
from core.utils import Utils
from typing import Dict, Any, List

class Employee(BaseDocument):
    """Frappe-independent Employee class"""
    
    def __init__(self, data: Dict[str, Any] = None):
        super().__init__(data)
    
    def validate(self):
        """Validate employee data"""
        self.validate_employee_data()
        self.set_defaults()
        self.calculate_employee_metrics()
        self.setup_hr_features()
    
    def validate_employee_data(self):
        """Validate employee information"""
        ValidationSystem.validate_required(self.data.get('first_name'), "First name")
        ValidationSystem.validate_required(self.data.get('last_name'), "Last name")
        ValidationSystem.validate_required(self.data.get('email'), "Email")
        ValidationSystem.validate_required(self.data.get('department'), "Department")
        
        if self.data.get('email') and not ValidationSystem.validate_email(self.data['email']):
            ValidationSystem.throw("Invalid email format")
    
    def set_defaults(self):
        """Set default values"""
        if not self.data.get('employment_status'):
            self.data['employment_status'] = "Active"
        if not self.data.get('employment_type'):
            self.data['employment_type'] = "Full-time"
        if not self.data.get('employee_id'):
            self.data['employee_id'] = Utils.make_autoname("EMP-.YYYY.-.#####")
    
    def calculate_employee_metrics(self):
        """Calculate employee metrics"""
        self.data['performance_score'] = self.calculate_performance_score()
        self.data['attendance_rate'] = self.calculate_attendance_rate()
        self.data['leave_balance'] = self.calculate_leave_balance()
        self.data['kpi_score'] = self.calculate_kpi_score()
    
    def calculate_performance_score(self) -> float:
        """Calculate performance score"""
        # Placeholder - implement actual logic
        return 0.85
    
    def calculate_attendance_rate(self) -> float:
        """Calculate attendance rate"""
        # Placeholder - implement actual logic
        return 0.95
    
    def calculate_leave_balance(self) -> Dict:
        """Calculate leave balance"""
        return {
            'annual_leave': 20,
            'sick_leave': 10,
            'personal_leave': 5,
            'total_available': 35
        }
    
    def calculate_kpi_score(self) -> float:
        """Calculate KPI score"""
        # Placeholder - implement actual logic
        return 0.78
    
    def setup_hr_features(self):
        """Setup HR features"""
        self.data['hr_features'] = {
            'leave_management': True,
            'kpi_tracking': True,
            'attendance_tracking': True,
            'performance_reviews': True,
            'equipment_management': True,
            'document_management': True
        }
    
    def apply_leave(self, leave_data: Dict):
        """Apply for leave"""
        leave_request = {
            'employee_id': self.data['employee_id'],
            'leave_type': leave_data.get('leave_type', 'Annual Leave'),
            'start_date': leave_data.get('start_date'),
            'end_date': leave_data.get('end_date'),
            'days': leave_data.get('days', 1),
            'reason': leave_data.get('reason', ''),
            'status': 'Pending',
            'applied_date': Utils.now().isoformat()
        }
        
        # Add to employee's leave history
        if 'leave_history' not in self.data:
            self.data['leave_history'] = []
        
        self.data['leave_history'].append(leave_request)
        return leave_request
    
    def record_attendance(self, attendance_data: Dict):
        """Record attendance with geolocation"""
        attendance_record = {
            'employee_id': self.data['employee_id'],
            'date': attendance_data.get('date', Utils.now().date().isoformat()),
            'check_in_time': attendance_data.get('check_in_time'),
            'check_out_time': attendance_data.get('check_out_time'),
            'check_in_location': attendance_data.get('check_in_location'),
            'check_out_location': attendance_data.get('check_out_location'),
            'work_hours': attendance_data.get('work_hours', 8.0),
            'status': 'Present'
        }
        
        # Add to employee's attendance history
        if 'attendance_history' not in self.data:
            self.data['attendance_history'] = []
        
        self.data['attendance_history'].append(attendance_record)
        return attendance_record
    
    def set_kpi(self, kpi_data: Dict):
        """Set KPI for employee"""
        kpi = {
            'employee_id': self.data['employee_id'],
            'kpi_name': kpi_data.get('kpi_name'),
            'target_value': kpi_data.get('target_value'),
            'actual_value': kpi_data.get('actual_value', 0),
            'period': kpi_data.get('period', 'Q1 2024'),
            'weight': kpi_data.get('weight', 1.0),
            'status': 'Active'
        }
        
        # Add to employee's KPIs
        if 'kpis' not in self.data:
            self.data['kpis'] = []
        
        self.data['kpis'].append(kpi)
        return kpi
    
    def assign_equipment(self, equipment_data: Dict):
        """Assign equipment to employee"""
        equipment = {
            'employee_id': self.data['employee_id'],
            'equipment_type': equipment_data.get('equipment_type'),
            'equipment_id': equipment_data.get('equipment_id'),
            'serial_number': equipment_data.get('serial_number'),
            'assigned_date': Utils.now().isoformat(),
            'status': 'Assigned',
            'return_date': equipment_data.get('return_date')
        }
        
        # Add to employee's equipment
        if 'equipment' not in self.data:
            self.data['equipment'] = []
        
        self.data['equipment'].append(equipment)
        return equipment
    
    def upload_document(self, document_data: Dict):
        """Upload document to employee profile"""
        document = {
            'employee_id': self.data['employee_id'],
            'document_type': document_data.get('document_type'),
            'document_name': document_data.get('document_name'),
            'file_path': document_data.get('file_path'),
            'upload_date': Utils.now().isoformat(),
            'status': 'Active'
        }
        
        # Add to employee's documents
        if 'documents' not in self.data:
            self.data['documents'] = []
        
        self.data['documents'].append(document)
        return document
    
    def get_performance_analytics(self) -> Dict:
        """Get performance analytics"""
        return {
            'overall_score': self.data.get('performance_score', 0),
            'attendance_rate': self.data.get('attendance_rate', 0),
            'kpi_score': self.data.get('kpi_score', 0),
            'leave_utilization': self.calculate_leave_utilization(),
            'equipment_usage': self.calculate_equipment_usage(),
            'document_compliance': self.calculate_document_compliance()
        }
    
    def calculate_leave_utilization(self) -> float:
        """Calculate leave utilization"""
        # Placeholder - implement actual logic
        return 0.6
    
    def calculate_equipment_usage(self) -> float:
        """Calculate equipment usage"""
        # Placeholder - implement actual logic
        return 0.8
    
    def calculate_document_compliance(self) -> float:
        """Calculate document compliance"""
        # Placeholder - implement actual logic
        return 0.9
