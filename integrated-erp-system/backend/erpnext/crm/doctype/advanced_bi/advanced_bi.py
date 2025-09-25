# Advanced BI - Business Intelligence System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

class AdvancedBI(Document):
    def autoname(self):
        """Generate unique BI ID"""
        if not self.bi_id:
            self.bi_id = make_autoname("BI-.YYYY.-.MM.-.#####")
        self.name = self.bi_id

    def validate(self):
        """Validate BI data"""
        self.validate_bi_data()
        self.set_defaults()
        self.validate_bi_configuration()
        self.calculate_bi_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_bi_settings()
        self.setup_bi_permissions()
        self.generate_bi_insights()

    def after_insert(self):
        """Process after inserting new BI"""
        self.create_bi_profile()
        self.setup_bi_workflow()
        self.create_bi_analytics()
        self.initialize_bi_tracking()

    def on_update(self):
        """Process on BI update"""
        self.update_bi_analytics()
        self.sync_bi_data()
        self.update_bi_status()
        self.process_bi_changes()

    def validate_bi_data(self):
        """Validate BI information"""
        if not self.bi_name:
            frappe.throw(_("BI name is required"))
        
        if not self.bi_type:
            frappe.throw(_("BI type is required"))
        
        if not self.bi_configuration:
            frappe.throw(_("BI configuration is required"))

    def validate_bi_configuration(self):
        """Validate BI configuration"""
        if not self.bi_configuration:
            frappe.throw(_("BI configuration is required"))
        
        # Validate BI configuration format
        try:
            config = json.loads(self.bi_configuration)
            if not isinstance(config, dict):
                frappe.throw(_("BI configuration must be a valid JSON object"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format in BI configuration"))

    def set_defaults(self):
        """Set default values for new BI"""
        if not self.bi_status:
            self.bi_status = "Active"
        
        if not self.bi_priority:
            self.bi_priority = "High"
        
        if not self.bi_category:
            self.bi_category = "Analytics"
        
        if not self.is_bi_enabled:
            self.is_bi_enabled = 1

    def calculate_bi_metrics(self):
        """Calculate BI metrics"""
        # Calculate BI performance
        self.bi_performance = self.calculate_bi_performance()
        
        # Calculate BI accuracy
        self.bi_accuracy = self.calculate_bi_accuracy()
        
        # Calculate BI efficiency
        self.bi_efficiency = self.calculate_bi_efficiency()
        
        # Calculate BI value
        self.bi_value = self.calculate_bi_value()

    def calculate_bi_performance(self):
        """Calculate BI performance"""
        # Get BI performance data
        performance_data = frappe.db.sql("""
            SELECT AVG(query_time) as avg_query_time,
                   AVG(processing_time) as avg_processing_time,
                   AVG(accuracy_score) as avg_accuracy
            FROM `tabBI Performance`
            WHERE bi_system = %s
            AND performance_date >= DATE_SUB(NOW(), INTERVAL 24 HOURS)
        """, self.name, as_dict=True)[0]
        
        if performance_data['avg_query_time']:
            # Calculate performance score based on query time and accuracy
            query_score = max(0, 100 - (performance_data['avg_query_time'] / 10))
            processing_score = max(0, 100 - (performance_data['avg_processing_time'] / 10))
            accuracy_score = performance_data['avg_accuracy']
            
            performance = (query_score + processing_score + accuracy_score) / 3
            return min(performance, 100)
        else:
            return 0

    def calculate_bi_accuracy(self):
        """Calculate BI accuracy"""
        # Get BI accuracy data
        accuracy_data = frappe.db.sql("""
            SELECT AVG(accuracy_percentage) as avg_accuracy,
                   COUNT(*) as total_measurements
            FROM `tabBI Accuracy`
            WHERE bi_system = %s
            AND accuracy_date >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
        """, self.name, as_dict=True)[0]
        
        if accuracy_data['total_measurements'] > 0:
            return round(accuracy_data['avg_accuracy'], 2)
        else:
            return 0

    def calculate_bi_efficiency(self):
        """Calculate BI efficiency"""
        # Get BI efficiency data
        efficiency_data = frappe.db.sql("""
            SELECT AVG(efficiency_percentage) as avg_efficiency,
                   COUNT(*) as total_measurements
            FROM `tabBI Efficiency`
            WHERE bi_system = %s
            AND efficiency_date >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
        """, self.name, as_dict=True)[0]
        
        if efficiency_data['total_measurements'] > 0:
            return round(efficiency_data['avg_efficiency'], 2)
        else:
            return 0

    def calculate_bi_value(self):
        """Calculate BI value"""
        # Get BI value data
        value_data = frappe.db.sql("""
            SELECT AVG(value_score) as avg_value,
                   COUNT(*) as total_measurements
            FROM `tabBI Value`
            WHERE bi_system = %s
            AND value_date >= DATE_SUB(NOW(), INTERVAL 30 DAYS)
        """, self.name, as_dict=True)[0]
        
        if value_data['total_measurements'] > 0:
            return round(value_data['avg_value'], 2)
        else:
            return 0

    def update_bi_settings(self):
        """Update BI-specific settings"""
        # Update BI preferences
        if self.preferences:
            frappe.db.set_value("Advanced BI", self.name, "preferences", json.dumps(self.preferences))
        
        # Update BI tags
        if self.tags:
            frappe.db.set_value("Advanced BI", self.name, "tags", json.dumps(self.tags))

    def setup_bi_permissions(self):
        """Setup BI-specific permissions"""
        # Create BI-specific roles
        bi_roles = [
            f"BI - {self.bi_id}",
            f"Type - {self.bi_type}",
            f"Category - {self.bi_category}"
        ]
        
        for role_name in bi_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_bi_insights(self):
        """Generate BI insights"""
        insights = {
            "bi_performance": self.bi_performance,
            "bi_accuracy": self.bi_accuracy,
            "bi_efficiency": self.bi_efficiency,
            "bi_value": self.bi_value,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.bi_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify BI optimization opportunities"""
        opportunities = []
        
        # Check for performance improvements
        if self.bi_performance < 80:
            opportunities.append("Optimize BI performance")
        
        # Check for accuracy improvements
        if self.bi_accuracy < 90:
            opportunities.append("Improve BI accuracy")
        
        # Check for efficiency improvements
        if self.bi_efficiency < 85:
            opportunities.append("Enhance BI efficiency")
        
        # Check for value improvements
        if self.bi_value < 80:
            opportunities.append("Increase BI value")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.bi_status == "Active":
            actions.append("Monitor BI performance")
            actions.append("Update BI configuration")
            actions.append("Optimize BI settings")
        elif self.bi_status == "Testing":
            actions.append("Complete BI testing")
            actions.append("Validate BI performance")
            actions.append("Deploy BI system")
        else:
            actions.append("Review BI status")
            actions.append("Take appropriate action")
        
        return actions

    def create_bi_profile(self):
        """Create comprehensive BI profile"""
        profile_data = {
            "bi_id": self.bi_id,
            "bi_name": self.bi_name,
            "bi_type": self.bi_type,
            "bi_category": self.bi_category,
            "bi_status": self.bi_status,
            "bi_priority": self.bi_priority,
            "bi_performance": self.bi_performance,
            "bi_accuracy": self.bi_accuracy,
            "bi_efficiency": self.bi_efficiency,
            "bi_value": self.bi_value,
            "is_bi_enabled": self.is_bi_enabled
        }
        
        frappe.get_doc({
            "doctype": "BI Profile",
            "bi_system": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_bi_workflow(self):
        """Setup BI workflow"""
        workflow_data = {
            "bi_system": self.name,
            "workflow_type": "BI Management",
            "steps": [
                {"step": "BI Configuration", "status": "Completed"},
                {"step": "BI Testing", "status": "Pending"},
                {"step": "BI Deployment", "status": "Pending"},
                {"step": "BI Monitoring", "status": "Pending"},
                {"step": "BI Optimization", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "BI Workflow",
            "bi_system": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_bi_analytics(self):
        """Create BI analytics"""
        analytics_data = {
            "bi_system": self.name,
            "analytics_type": "BI Analytics",
            "metrics": {
                "bi_performance": self.bi_performance,
                "bi_accuracy": self.bi_accuracy,
                "bi_efficiency": self.bi_efficiency,
                "bi_value": self.bi_value
            },
            "insights": self.generate_bi_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "BI Analytics",
            "bi_system": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_bi_tracking(self):
        """Initialize BI tracking"""
        tracking_data = {
            "bi_system": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "query_count": 0,
            "report_count": 0
        }
        
        frappe.get_doc({
            "doctype": "BI Tracking",
            "bi_system": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_bi_analytics(self):
        """Update BI analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "bi_performance": self.calculate_bi_performance(),
            "bi_accuracy": self.calculate_bi_accuracy(),
            "bi_efficiency": self.calculate_bi_efficiency(),
            "bi_value": self.calculate_bi_value()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("BI Analytics", {"bi_system": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "bi_system": self.name,
                "analytics_type": "BI Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_bi_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_bi_data(self):
        """Sync BI data across systems"""
        # Sync with external BI systems if configured
        if self.external_bi_system_id:
            self.sync_with_external_bi_system()

    def update_bi_status(self):
        """Update BI status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("BI Tracking", {"bi_system": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_bi_changes(self):
        """Process BI changes"""
        # Log BI changes
        self.log_bi_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "BI Status Change",
            "bi_system": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.bi_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabBI Status Change`
            WHERE bi_system = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("BI Status Change", {"bi_system": self.name}) else "New"
        
        return previous_status

    def log_bi_changes(self):
        """Log BI changes"""
        frappe.get_doc({
            "doctype": "BI Change Log",
            "bi_system": self.name,
            "change_type": "Update",
            "change_description": "BI information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update BI performance
        self.update_bi_performance()
        
        # Update BI accuracy
        self.update_bi_accuracy()

    def update_bi_performance(self):
        """Update BI performance"""
        # Update performance status
        frappe.db.sql("""
            UPDATE `tabBI Performance`
            SET bi_system_status = %s
            WHERE bi_system = %s
        """, (self.bi_status, self.name))

    def update_bi_accuracy(self):
        """Update BI accuracy"""
        # Update accuracy status
        frappe.db.sql("""
            UPDATE `tabBI Accuracy`
            SET bi_system_status = %s
            WHERE bi_system = %s
        """, (self.bi_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify BI users
        self.notify_bi_users()
        
        # Notify BI administrators
        self.notify_bi_administrators()

    def notify_bi_users(self):
        """Notify BI users"""
        frappe.get_doc({
            "doctype": "BI Notification",
            "bi_system": self.name,
            "notification_type": "BI Update",
            "message": f"BI system {self.bi_name} has been updated",
            "recipients": "BI Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_bi_administrators(self):
        """Notify BI administrators"""
        frappe.get_doc({
            "doctype": "BI Notification",
            "bi_system": self.name,
            "notification_type": "BI Update",
            "message": f"BI system {self.bi_name} has been updated",
            "recipients": "BI Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_bi_system(self):
        """Sync BI data with external BI system"""
        # Implementation for external BI system sync
        pass

    @frappe.whitelist()
    def get_bi_dashboard_data(self):
        """Get BI dashboard data"""
        return {
            "bi_id": self.bi_id,
            "bi_name": self.bi_name,
            "bi_type": self.bi_type,
            "bi_category": self.bi_category,
            "bi_status": self.bi_status,
            "bi_priority": self.bi_priority,
            "bi_performance": self.bi_performance,
            "bi_accuracy": self.bi_accuracy,
            "bi_efficiency": self.bi_efficiency,
            "bi_value": self.bi_value,
            "is_bi_enabled": self.is_bi_enabled,
            "insights": self.generate_bi_insights()
        }

    @frappe.whitelist()
    def get_bi_insights(self):
        """Get BI insights"""
        return {
            "bi_performance": self.bi_performance,
            "bi_accuracy": self.bi_accuracy,
            "bi_efficiency": self.bi_efficiency,
            "bi_value": self.bi_value,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }

    @frappe.whitelist()
    def generate_bi_report(self, report_type, parameters):
        """Generate BI report"""
        try:
            # Generate BI report based on type and parameters
            report_data = self.execute_bi_report(report_type, parameters)
            
            # Log report generation
            frappe.get_doc({
                "doctype": "BI Report",
                "bi_system": self.name,
                "report_type": report_type,
                "report_parameters": json.dumps(parameters),
                "report_data": json.dumps(report_data),
                "report_date": now(),
                "generated_by": frappe.session.user
            }).insert(ignore_permissions=True)
            
            return {
                "status": "success",
                "message": "BI report generated successfully",
                "report_data": report_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"BI report generation failed: {str(e)}"
            }

    def execute_bi_report(self, report_type, parameters):
        """Execute BI report"""
        # Implementation for BI report execution
        return {
            "report_type": report_type,
            "parameters": parameters,
            "data": [],
            "summary": {},
            "generated_date": now().isoformat()
        }
