# Advanced Integration - Enterprise Integration Management

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class AdvancedIntegration(Document):
    def autoname(self):
        """Generate unique integration ID"""
        if not self.integration_id:
            self.integration_id = make_autoname("INT-.YYYY.-.MM.-.#####")
        self.name = self.integration_id

    def validate(self):
        """Validate integration data"""
        self.validate_integration_data()
        self.set_defaults()
        self.validate_integration_configuration()
        self.calculate_integration_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_integration_settings()
        self.setup_integration_permissions()
        self.generate_integration_insights()

    def after_insert(self):
        """Process after inserting new integration"""
        self.create_integration_profile()
        self.setup_integration_workflow()
        self.create_integration_analytics()
        self.initialize_integration_tracking()

    def on_update(self):
        """Process on integration update"""
        self.update_integration_analytics()
        self.sync_integration_data()
        self.update_integration_status()
        self.process_integration_changes()

    def validate_integration_data(self):
        """Validate integration information"""
        if not self.integration_name:
            frappe.throw(_("Integration name is required"))
        
        if not self.integration_type:
            frappe.throw(_("Integration type is required"))
        
        if not self.integration_configuration:
            frappe.throw(_("Integration configuration is required"))

    def validate_integration_configuration(self):
        """Validate integration configuration"""
        if not self.integration_configuration:
            frappe.throw(_("Integration configuration is required"))
        
        # Validate integration configuration format
        try:
            config = json.loads(self.integration_configuration)
            if not isinstance(config, dict):
                frappe.throw(_("Integration configuration must be a valid JSON object"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format in integration configuration"))

    def set_defaults(self):
        """Set default values for new integration"""
        if not self.integration_status:
            self.integration_status = "Active"
        
        if not self.integration_priority:
            self.integration_priority = "Medium"
        
        if not self.integration_category:
            self.integration_category = "General"
        
        if not self.is_integration_enabled:
            self.is_integration_enabled = 1

    def calculate_integration_metrics(self):
        """Calculate integration metrics"""
        # Calculate integration performance
        self.integration_performance = self.calculate_integration_performance()
        
        # Calculate integration reliability
        self.integration_reliability = self.calculate_integration_reliability()
        
        # Calculate integration efficiency
        self.integration_efficiency = self.calculate_integration_efficiency()
        
        # Calculate integration scalability
        self.integration_scalability = self.calculate_integration_scalability()

    def calculate_integration_performance(self):
        """Calculate integration performance"""
        # Get integration performance data
        performance_data = frappe.db.sql("""
            SELECT AVG(response_time) as avg_response_time,
                   AVG(throughput) as avg_throughput,
                   AVG(success_rate) as avg_success_rate
            FROM `tabIntegration Performance`
            WHERE integration = %s
            AND performance_date >= DATE_SUB(NOW(), INTERVAL 24 HOURS)
        """, self.name, as_dict=True)[0]
        
        if performance_data['avg_response_time']:
            # Calculate performance score based on response time and throughput
            response_score = max(0, 100 - (performance_data['avg_response_time'] / 10))
            throughput_score = min(100, performance_data['avg_throughput'] * 10)
            success_score = performance_data['avg_success_rate']
            
            performance = (response_score + throughput_score + success_score) / 3
            return min(performance, 100)
        else:
            return 0

    def calculate_integration_reliability(self):
        """Calculate integration reliability"""
        # Get integration reliability data
        reliability_data = frappe.db.sql("""
            SELECT AVG(availability_percentage) as avg_availability,
                   AVG(uptime_percentage) as avg_uptime,
                   COUNT(*) as total_checks
            FROM `tabIntegration Reliability`
            WHERE integration = %s
            AND reliability_date >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
        """, self.name, as_dict=True)[0]
        
        if reliability_data['total_checks'] > 0:
            reliability = (reliability_data['avg_availability'] + reliability_data['avg_uptime']) / 2
            return round(reliability, 2)
        else:
            return 0

    def calculate_integration_efficiency(self):
        """Calculate integration efficiency"""
        # Get integration efficiency data
        efficiency_data = frappe.db.sql("""
            SELECT AVG(efficiency_percentage) as avg_efficiency,
                   COUNT(*) as total_measurements
            FROM `tabIntegration Efficiency`
            WHERE integration = %s
            AND efficiency_date >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
        """, self.name, as_dict=True)[0]
        
        if efficiency_data['total_measurements'] > 0:
            return round(efficiency_data['avg_efficiency'], 2)
        else:
            return 0

    def calculate_integration_scalability(self):
        """Calculate integration scalability"""
        # Get integration scalability data
        scalability_data = frappe.db.sql("""
            SELECT AVG(scalability_score) as avg_scalability,
                   COUNT(*) as total_tests
            FROM `tabIntegration Scalability`
            WHERE integration = %s
            AND scalability_date >= DATE_SUB(NOW(), INTERVAL 30 DAYS)
        """, self.name, as_dict=True)[0]
        
        if scalability_data['total_tests'] > 0:
            return round(scalability_data['avg_scalability'], 2)
        else:
            return 0

    def update_integration_settings(self):
        """Update integration-specific settings"""
        # Update integration preferences
        if self.preferences:
            frappe.db.set_value("Advanced Integration", self.name, "preferences", json.dumps(self.preferences))
        
        # Update integration tags
        if self.tags:
            frappe.db.set_value("Advanced Integration", self.name, "tags", json.dumps(self.tags))

    def setup_integration_permissions(self):
        """Setup integration-specific permissions"""
        # Create integration-specific roles
        integration_roles = [
            f"Integration - {self.integration_id}",
            f"Type - {self.integration_type}",
            f"Category - {self.integration_category}"
        ]
        
        for role_name in integration_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_integration_insights(self):
        """Generate integration insights"""
        insights = {
            "integration_performance": self.integration_performance,
            "integration_reliability": self.integration_reliability,
            "integration_efficiency": self.integration_efficiency,
            "integration_scalability": self.integration_scalability,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.integration_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify integration optimization opportunities"""
        opportunities = []
        
        # Check for performance improvements
        if self.integration_performance < 80:
            opportunities.append("Optimize integration performance")
        
        # Check for reliability improvements
        if self.integration_reliability < 95:
            opportunities.append("Improve integration reliability")
        
        # Check for efficiency improvements
        if self.integration_efficiency < 85:
            opportunities.append("Enhance integration efficiency")
        
        # Check for scalability improvements
        if self.integration_scalability < 80:
            opportunities.append("Improve integration scalability")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.integration_status == "Active":
            actions.append("Monitor integration performance")
            actions.append("Update integration configuration")
            actions.append("Optimize integration settings")
        elif self.integration_status == "Testing":
            actions.append("Complete integration testing")
            actions.append("Validate integration performance")
            actions.append("Deploy integration system")
        else:
            actions.append("Review integration status")
            actions.append("Take appropriate action")
        
        return actions

    def create_integration_profile(self):
        """Create comprehensive integration profile"""
        profile_data = {
            "integration_id": self.integration_id,
            "integration_name": self.integration_name,
            "integration_type": self.integration_type,
            "integration_category": self.integration_category,
            "integration_status": self.integration_status,
            "integration_priority": self.integration_priority,
            "integration_performance": self.integration_performance,
            "integration_reliability": self.integration_reliability,
            "integration_efficiency": self.integration_efficiency,
            "integration_scalability": self.integration_scalability,
            "is_integration_enabled": self.is_integration_enabled
        }
        
        frappe.get_doc({
            "doctype": "Integration Profile",
            "integration": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_integration_workflow(self):
        """Setup integration workflow"""
        workflow_data = {
            "integration": self.name,
            "workflow_type": "Integration Management",
            "steps": [
                {"step": "Integration Configuration", "status": "Completed"},
                {"step": "Integration Testing", "status": "Pending"},
                {"step": "Integration Deployment", "status": "Pending"},
                {"step": "Integration Monitoring", "status": "Pending"},
                {"step": "Integration Optimization", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Integration Workflow",
            "integration": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_integration_analytics(self):
        """Create integration analytics"""
        analytics_data = {
            "integration": self.name,
            "analytics_type": "Integration Analytics",
            "metrics": {
                "integration_performance": self.integration_performance,
                "integration_reliability": self.integration_reliability,
                "integration_efficiency": self.integration_efficiency,
                "integration_scalability": self.integration_scalability
            },
            "insights": self.generate_integration_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Integration Analytics",
            "integration": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_integration_tracking(self):
        """Initialize integration tracking"""
        tracking_data = {
            "integration": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "sync_count": 0,
            "error_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Integration Tracking",
            "integration": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_integration_analytics(self):
        """Update integration analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "integration_performance": self.calculate_integration_performance(),
            "integration_reliability": self.calculate_integration_reliability(),
            "integration_efficiency": self.calculate_integration_efficiency(),
            "integration_scalability": self.calculate_integration_scalability()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Integration Analytics", {"integration": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "integration": self.name,
                "analytics_type": "Integration Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_integration_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_integration_data(self):
        """Sync integration data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_integration_status(self):
        """Update integration status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Integration Tracking", {"integration": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_integration_changes(self):
        """Process integration changes"""
        # Log integration changes
        self.log_integration_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Integration Status Change",
            "integration": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.integration_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabIntegration Status Change`
            WHERE integration = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Integration Status Change", {"integration": self.name}) else "New"
        
        return previous_status

    def log_integration_changes(self):
        """Log integration changes"""
        frappe.get_doc({
            "doctype": "Integration Change Log",
            "integration": self.name,
            "change_type": "Update",
            "change_description": "Integration information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update integration performance
        self.update_integration_performance()
        
        # Update integration reliability
        self.update_integration_reliability()

    def update_integration_performance(self):
        """Update integration performance"""
        # Update performance status
        frappe.db.sql("""
            UPDATE `tabIntegration Performance`
            SET integration_status = %s
            WHERE integration = %s
        """, (self.integration_status, self.name))

    def update_integration_reliability(self):
        """Update integration reliability"""
        # Update reliability status
        frappe.db.sql("""
            UPDATE `tabIntegration Reliability`
            SET integration_status = %s
            WHERE integration = %s
        """, (self.integration_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify integration users
        self.notify_integration_users()
        
        # Notify integration administrators
        self.notify_integration_administrators()

    def notify_integration_users(self):
        """Notify integration users"""
        frappe.get_doc({
            "doctype": "Integration Notification",
            "integration": self.name,
            "notification_type": "Integration Update",
            "message": f"Integration {self.integration_name} has been updated",
            "recipients": "Integration Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_integration_administrators(self):
        """Notify integration administrators"""
        frappe.get_doc({
            "doctype": "Integration Notification",
            "integration": self.name,
            "notification_type": "Integration Update",
            "message": f"Integration {self.integration_name} has been updated",
            "recipients": "Integration Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync integration data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_integration_dashboard_data(self):
        """Get integration dashboard data"""
        return {
            "integration_id": self.integration_id,
            "integration_name": self.integration_name,
            "integration_type": self.integration_type,
            "integration_category": self.integration_category,
            "integration_status": self.integration_status,
            "integration_priority": self.integration_priority,
            "integration_performance": self.integration_performance,
            "integration_reliability": self.integration_reliability,
            "integration_efficiency": self.integration_efficiency,
            "integration_scalability": self.integration_scalability,
            "is_integration_enabled": self.is_integration_enabled,
            "insights": self.generate_integration_insights()
        }

    @frappe.whitelist()
    def get_integration_insights(self):
        """Get integration insights"""
        return {
            "integration_performance": self.integration_performance,
            "integration_reliability": self.integration_reliability,
            "integration_efficiency": self.integration_efficiency,
            "integration_scalability": self.integration_scalability,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
