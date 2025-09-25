# Enhanced Employee DocType with Complete HR Features

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import base64
import hashlib

class Employee(Document):
    def autoname(self):
        """Generate unique employee code"""
        if not self.employee_code:
            self.employee_code = make_autoname("EMP-.YYYY.-.MM.-.#####")
        self.name = self.employee_code

    def validate(self):
        """Validate employee data"""
        self.validate_employee_data()
        self.set_defaults()
        self.validate_contact_info()
        self.validate_employment_details()
        self.validate_documents()

    def before_save(self):
        """Process before saving"""
        self.update_employee_settings()
        self.setup_employee_permissions()
        self.generate_employee_qr_code()

    def after_insert(self):
        """Process after inserting new employee"""
        self.create_employee_profile()
        self.setup_employee_workflow()
        self.create_employee_documents()
        self.setup_equipment_tracking()

    def on_update(self):
        """Process on employee update"""
        self.update_employee_analytics()
        self.sync_employee_data()
        self.update_workflow_status()

    def validate_employee_data(self):
        """Validate employee information"""
        if not self.first_name:
            frappe.throw(_("First name is required"))
        
        if not self.last_name:
            frappe.throw(_("Last name is required"))
        
        if not self.email:
            frappe.throw(_("Email is required"))
        
        if not self.department:
            frappe.throw(_("Department is required"))
        
        if not self.designation:
            frappe.throw(_("Designation is required"))

    def validate_contact_info(self):
        """Validate contact information"""
        if self.email and not self.validate_email():
            frappe.throw(_("Invalid email format"))
        
        if self.phone and not self.validate_phone():
            frappe.throw(_("Invalid phone number format"))

    def validate_employment_details(self):
        """Validate employment details"""
        if self.date_of_joining and self.date_of_birth:
            if self.date_of_joining < self.date_of_birth:
                frappe.throw(_("Date of joining cannot be before date of birth"))
        
        if self.date_of_joining and self.date_of_joining > now().date():
            frappe.throw(_("Date of joining cannot be in the future"))

    def validate_documents(self):
        """Validate employee documents"""
        if self.documents:
            for doc in self.documents:
                if not doc.document_name:
                    frappe.throw(_("Document name is required for all documents"))
                
                if not doc.document_type:
                    frappe.throw(_("Document type is required for all documents"))

    def set_defaults(self):
        """Set default values for new employee"""
        if not self.status:
            self.status = "Active"
        
        if not self.employment_type:
            self.employment_type = "Full-time"
        
        if not self.work_location:
            self.work_location = "Office"
        
        if not self.reporting_manager:
            # Set default reporting manager based on department
            self.set_default_reporting_manager()

    def update_employee_settings(self):
        """Update employee-specific settings"""
        # Update employee timezone
        if self.timezone:
            frappe.db.set_value("Employee", self.name, "timezone", self.timezone)
        
        # Update employee language
        if self.language:
            frappe.db.set_value("Employee", self.name, "language", self.language)
        
        # Update employee preferences
        if self.preferences:
            frappe.db.set_value("Employee", self.name, "preferences", json.dumps(self.preferences))

    def setup_employee_permissions(self):
        """Setup employee-specific permissions"""
        # Create employee-specific roles
        employee_roles = [
            f"Employee - {self.employee_code}",
            f"Department - {self.department}",
            f"Designation - {self.designation}"
        ]
        
        for role_name in employee_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_employee_qr_code(self):
        """Generate QR code for employee"""
        qr_data = {
            "employee_code": self.employee_code,
            "employee_name": f"{self.first_name} {self.last_name}",
            "department": self.department,
            "designation": self.designation,
            "company": self.company
        }
        
        # Generate QR code
        qr_code = self.create_qr_code(json.dumps(qr_data))
        self.qr_code = qr_code

    def create_employee_profile(self):
        """Create comprehensive employee profile"""
        profile_data = {
            "employee_code": self.employee_code,
            "personal_info": {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email": self.email,
                "phone": self.phone,
                "date_of_birth": self.date_of_birth,
                "gender": self.gender,
                "marital_status": self.marital_status
            },
            "employment_info": {
                "department": self.department,
                "designation": self.designation,
                "date_of_joining": self.date_of_joining,
                "employment_type": self.employment_type,
                "work_location": self.work_location,
                "reporting_manager": self.reporting_manager
            },
            "contact_info": {
                "address": self.address,
                "city": self.city,
                "state": self.state,
                "country": self.country,
                "postal_code": self.postal_code
            },
            "emergency_contact": {
                "emergency_contact_name": self.emergency_contact_name,
                "emergency_contact_phone": self.emergency_contact_phone,
                "emergency_contact_relationship": self.emergency_contact_relationship
            }
        }
        
        frappe.get_doc({
            "doctype": "Employee Profile",
            "employee": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_employee_workflow(self):
        """Setup employee workflow"""
        # Create employee workflow
        workflow_data = {
            "employee": self.name,
            "workflow_type": "Employee Onboarding",
            "steps": [
                {"step": "Document Verification", "status": "Pending"},
                {"step": "Background Check", "status": "Pending"},
                {"step": "Equipment Assignment", "status": "Pending"},
                {"step": "Training Assignment", "status": "Pending"},
                {"step": "Final Approval", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Employee Workflow",
            "employee": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_employee_documents(self):
        """Create employee document structure"""
        if self.documents:
            for doc in self.documents:
                frappe.get_doc({
                    "doctype": "Employee Document",
                    "employee": self.name,
                    "document_name": doc.document_name,
                    "document_type": doc.document_type,
                    "document_file": doc.document_file,
                    "is_required": doc.is_required,
                    "expiry_date": doc.expiry_date
                }).insert(ignore_permissions=True)

    def setup_equipment_tracking(self):
        """Setup equipment tracking for employee"""
        if self.equipment:
            for equipment in self.equipment:
                frappe.get_doc({
                    "doctype": "Employee Equipment",
                    "employee": self.name,
                    "equipment_type": equipment.equipment_type,
                    "equipment_name": equipment.equipment_name,
                    "serial_number": equipment.serial_number,
                    "assigned_date": equipment.assigned_date,
                    "condition": equipment.condition,
                    "location": equipment.location
                }).insert(ignore_permissions=True)

    def update_employee_analytics(self):
        """Update employee analytics"""
        # Calculate employee metrics
        metrics = self.calculate_employee_metrics()
        
        # Update analytics
        frappe.db.set_value("Employee", self.name, "analytics", json.dumps(metrics))

    def sync_employee_data(self):
        """Sync employee data across systems"""
        # Sync with external HR systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_workflow_status(self):
        """Update workflow status"""
        # Update employee workflow status
        workflow = frappe.get_doc("Employee Workflow", {"employee": self.name})
        if workflow:
            workflow.update_status()
            workflow.save()

    def calculate_employee_metrics(self):
        """Calculate employee performance metrics"""
        # Get performance data
        performance_data = self.get_performance_data()
        
        # Calculate metrics
        metrics = {
            "attendance_rate": self.calculate_attendance_rate(),
            "leave_balance": self.calculate_leave_balance(),
            "performance_score": self.calculate_performance_score(),
            "kpi_score": self.calculate_kpi_score(),
            "okr_progress": self.calculate_okr_progress(),
            "equipment_status": self.get_equipment_status(),
            "document_compliance": self.get_document_compliance(),
            "last_updated": now().isoformat()
        }
        
        return metrics

    def calculate_attendance_rate(self):
        """Calculate employee attendance rate"""
        # Get attendance data for current month
        attendance_data = frappe.db.sql("""
            SELECT COUNT(*) as total_days, 
                   SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_days
            FROM `tabAttendance` 
            WHERE employee = %s 
            AND attendance_date >= %s
        """, (self.name, now().date().replace(day=1)))
        
        if attendance_data and attendance_data[0][0] > 0:
            return (attendance_data[0][1] / attendance_data[0][0]) * 100
        return 0

    def calculate_leave_balance(self):
        """Calculate employee leave balance"""
        # Get leave balance data
        leave_balance = frappe.db.sql("""
            SELECT leave_type, balance
            FROM `tabLeave Balance` 
            WHERE employee = %s
        """, self.name, as_dict=True)
        
        return {leave["leave_type"]: leave["balance"] for leave in leave_balance}

    def calculate_performance_score(self):
        """Calculate employee performance score"""
        # Get performance reviews
        performance_reviews = frappe.db.sql("""
            SELECT AVG(overall_rating) as avg_rating
            FROM `tabPerformance Review` 
            WHERE employee = %s 
            AND review_date >= %s
        """, (self.name, now().date() - timedelta(days=365)))
        
        if performance_reviews and performance_reviews[0][0]:
            return performance_reviews[0][0]
        return 0

    def calculate_kpi_score(self):
        """Calculate employee KPI score"""
        # Get KPI data
        kpi_data = frappe.db.sql("""
            SELECT AVG(achievement_percentage) as avg_achievement
            FROM `tabEmployee KPI` 
            WHERE employee = %s 
            AND kpi_date >= %s
        """, (self.name, now().date() - timedelta(days=90)))
        
        if kpi_data and kpi_data[0][0]:
            return kpi_data[0][0]
        return 0

    def calculate_okr_progress(self):
        """Calculate employee OKR progress"""
        # Get OKR data
        okr_data = frappe.db.sql("""
            SELECT AVG(progress_percentage) as avg_progress
            FROM `tabEmployee OKR` 
            WHERE employee = %s 
            AND okr_date >= %s
        """, (self.name, now().date() - timedelta(days=90)))
        
        if okr_data and okr_data[0][0]:
            return okr_data[0][0]
        return 0

    def get_equipment_status(self):
        """Get employee equipment status"""
        # Get equipment data
        equipment_data = frappe.db.sql("""
            SELECT equipment_type, condition, assigned_date
            FROM `tabEmployee Equipment` 
            WHERE employee = %s
        """, self.name, as_dict=True)
        
        return equipment_data

    def get_document_compliance(self):
        """Get employee document compliance status"""
        # Get document data
        document_data = frappe.db.sql("""
            SELECT document_type, is_required, expiry_date
            FROM `tabEmployee Document` 
            WHERE employee = %s
        """, self.name, as_dict=True)
        
        compliance_status = {}
        for doc in document_data:
            if doc["is_required"]:
                if doc["expiry_date"]:
                    if doc["expiry_date"] < now().date():
                        compliance_status[doc["document_type"]] = "Expired"
                    elif doc["expiry_date"] < now().date() + timedelta(days=30):
                        compliance_status[doc["document_type"]] = "Expiring Soon"
                    else:
                        compliance_status[doc["document_type"]] = "Valid"
                else:
                    compliance_status[doc["document_type"]] = "Valid"
            else:
                compliance_status[doc["document_type"]] = "Not Required"
        
        return compliance_status

    def get_performance_data(self):
        """Get employee performance data"""
        return frappe.db.sql("""
            SELECT 
                performance_review.overall_rating,
                performance_review.review_date,
                performance_review.reviewer
            FROM `tabPerformance Review` performance_review
            WHERE performance_review.employee = %s
            ORDER BY performance_review.review_date DESC
            LIMIT 5
        """, self.name, as_dict=True)

    def validate_email(self):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.email) is not None

    def validate_phone(self):
        """Validate phone number format"""
        import re
        pattern = r'^\+?[\d\s\-\(\)]+$'
        return re.match(pattern, self.phone) is not None

    def set_default_reporting_manager(self):
        """Set default reporting manager based on department"""
        # Get department head
        department_head = frappe.db.get_value("Department", self.department, "department_head")
        if department_head:
            self.reporting_manager = department_head

    def create_qr_code(self, data):
        """Create QR code for employee"""
        import qrcode
        import io
        import base64
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str

    def sync_with_external_system(self):
        """Sync employee data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_employee_dashboard_data(self):
        """Get employee dashboard data"""
        return {
            "employee_code": self.employee_code,
            "employee_name": f"{self.first_name} {self.last_name}",
            "department": self.department,
            "designation": self.designation,
            "metrics": self.calculate_employee_metrics(),
            "recent_activities": self.get_recent_activities(),
            "upcoming_events": self.get_upcoming_events(),
            "leave_balance": self.calculate_leave_balance(),
            "equipment_status": self.get_equipment_status()
        }

    def get_recent_activities(self):
        """Get recent employee activities"""
        return frappe.db.sql("""
            SELECT 
                activity_type,
                activity_date,
                description
            FROM `tabEmployee Activity` 
            WHERE employee = %s 
            ORDER BY activity_date DESC 
            LIMIT 10
        """, self.name, as_dict=True)

    def get_upcoming_events(self):
        """Get upcoming employee events"""
        return frappe.db.sql("""
            SELECT 
                event_type,
                event_date,
                description
            FROM `tabEmployee Event` 
            WHERE employee = %s 
            AND event_date >= %s
            ORDER BY event_date ASC 
            LIMIT 5
        """, (self.name, now().date()), as_dict=True)

    @frappe.whitelist()
    def check_in(self, location_data=None):
        """Employee check-in with geolocation"""
        # Validate location if provided
        if location_data:
            if not self.validate_location(location_data):
                frappe.throw(_("Invalid location data"))
        
        # Create attendance record
        attendance = frappe.get_doc({
            "doctype": "Attendance",
            "employee": self.name,
            "attendance_date": now().date(),
            "check_in": now().time(),
            "status": "Present",
            "location": location_data,
            "work_location": self.work_location
        })
        attendance.insert(ignore_permissions=True)
        
        return {
            "status": "success",
            "message": "Check-in successful",
            "check_in_time": now().time(),
            "location": location_data
        }

    @frappe.whitelist()
    def check_out(self, location_data=None):
        """Employee check-out with geolocation"""
        # Get today's attendance
        attendance = frappe.get_doc("Attendance", {
            "employee": self.name,
            "attendance_date": now().date()
        })
        
        if not attendance:
            frappe.throw(_("No check-in record found for today"))
        
        # Update attendance
        attendance.check_out = now().time()
        attendance.working_hours = self.calculate_working_hours(attendance.check_in, attendance.check_out)
        attendance.location_out = location_data
        attendance.save()
        
        return {
            "status": "success",
            "message": "Check-out successful",
            "check_out_time": now().time(),
            "working_hours": attendance.working_hours,
            "location": location_data
        }

    def validate_location(self, location_data):
        """Validate employee location"""
        # Basic location validation
        if not location_data.get("latitude") or not location_data.get("longitude"):
            return False
        
        # Check if location is within allowed radius
        if self.work_location == "Office":
            office_location = frappe.db.get_value("Company", self.company, "office_location")
            if office_location:
                distance = self.calculate_distance(
                    location_data["latitude"], 
                    location_data["longitude"],
                    office_location["latitude"],
                    office_location["longitude"]
                )
                if distance > 100:  # 100 meters radius
                    return False
        
        return True

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates"""
        import math
        
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    def calculate_working_hours(self, check_in, check_out):
        """Calculate working hours"""
        if not check_in or not check_out:
            return 0
        
        # Convert time to datetime for calculation
        check_in_dt = datetime.combine(now().date(), check_in)
        check_out_dt = datetime.combine(now().date(), check_out)
        
        # Calculate difference
        working_hours = (check_out_dt - check_in_dt).total_seconds() / 3600
        
        return working_hours
