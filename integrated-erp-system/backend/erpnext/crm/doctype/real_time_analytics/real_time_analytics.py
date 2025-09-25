# Real-time Analytics - Live Performance Monitoring

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class RealTimeAnalytics(Document):
    def autoname(self):
        """Generate unique analytics ID"""
        if not self.analytics_id:
            self.analytics_id = make_autoname("RTA-.YYYY.-.MM.-.#####")
        self.name = self.analytics_id

    def validate(self):
        """Validate analytics data"""
        self.validate_analytics_data()
        self.set_defaults()
        self.validate_analytics_configuration()
        self.calculate_real_time_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_analytics_settings()
        self.setup_analytics_permissions()
        self.generate_analytics_insights()

    def after_insert(self):
        """Process after inserting new analytics"""
        self.create_analytics_profile()
        self.setup_analytics_workflow()
        self.create_analytics_dashboard()
        self.initialize_analytics_tracking()

    def on_update(self):
        """Process on analytics update"""
        self.update_analytics_dashboard()
        self.sync_analytics_data()
        self.update_analytics_status()
        self.process_analytics_changes()

    def validate_analytics_data(self):
        """Validate analytics information"""
        if not self.analytics_name:
            frappe.throw(_("Analytics name is required"))
        
        if not self.analytics_type:
            frappe.throw(_("Analytics type is required"))
        
        if not self.analytics_configuration:
            frappe.throw(_("Analytics configuration is required"))

    def validate_analytics_configuration(self):
        """Validate analytics configuration"""
        if not self.analytics_configuration:
            frappe.throw(_("Analytics configuration is required"))
        
        # Validate analytics configuration format
        try:
            config = json.loads(self.analytics_configuration)
            if not isinstance(config, dict):
                frappe.throw(_("Analytics configuration must be a valid JSON object"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format in analytics configuration"))

    def set_defaults(self):
        """Set default values for new analytics"""
        if not self.analytics_status:
            self.analytics_status = "Active"
        
        if not self.analytics_priority:
            self.analytics_priority = "Medium"
        
        if not self.analytics_category:
            self.analytics_category = "General"
        
        if not self.is_real_time_enabled:
            self.is_real_time_enabled = 1

    def calculate_real_time_metrics(self):
        """Calculate real-time analytics metrics"""
        # Calculate performance metrics
        self.performance_score = self.calculate_performance_score()
        
        # Calculate accuracy metrics
        self.accuracy_score = self.calculate_accuracy_score()
        
        # Calculate efficiency metrics
        self.efficiency_score = self.calculate_efficiency_score()
        
        # Calculate reliability metrics
        self.reliability_score = self.calculate_reliability_score()

    def calculate_performance_score(self):
        """Calculate performance score"""
        # Get performance data
        performance_data = frappe.db.sql("""
            SELECT AVG(response_time) as avg_response_time,
                   AVG(throughput) as avg_throughput,
                   AVG(cpu_usage) as avg_cpu_usage,
                   AVG(memory_usage) as avg_memory_usage
            FROM `tabAnalytics Performance`
            WHERE analytics = %s
            AND performance_date >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """, self.name, as_dict=True)[0]
        
        if performance_data['avg_response_time']:
            # Calculate performance score based on response time and resource usage
            response_score = max(0, 100 - (performance_data['avg_response_time'] / 10))
            throughput_score = min(100, performance_data['avg_throughput'] * 10)
            resource_score = max(0, 100 - (performance_data['avg_cpu_usage'] + performance_data['avg_memory_usage']) / 2)
            
            performance = (response_score + throughput_score + resource_score) / 3
            return min(performance, 100)
        else:
            return 0

    def calculate_accuracy_score(self):
        """Calculate accuracy score"""
        # Get accuracy data
        accuracy_data = frappe.db.sql("""
            SELECT AVG(accuracy_percentage) as avg_accuracy,
                   COUNT(*) as total_measurements
            FROM `tabAnalytics Accuracy`
            WHERE analytics = %s
            AND accuracy_date >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """, self.name, as_dict=True)[0]
        
        if accuracy_data['total_measurements'] > 0:
            return round(accuracy_data['avg_accuracy'], 2)
        else:
            return 0

    def calculate_efficiency_score(self):
        """Calculate efficiency score"""
        # Get efficiency data
        efficiency_data = frappe.db.sql("""
            SELECT AVG(efficiency_percentage) as avg_efficiency,
                   COUNT(*) as total_measurements
            FROM `tabAnalytics Efficiency`
            WHERE analytics = %s
            AND efficiency_date >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """, self.name, as_dict=True)[0]
        
        if efficiency_data['total_measurements'] > 0:
            return round(efficiency_data['avg_efficiency'], 2)
        else:
            return 0

    def calculate_reliability_score(self):
        """Calculate reliability score"""
        # Get reliability data
        reliability_data = frappe.db.sql("""
            SELECT AVG(availability_percentage) as avg_availability,
                   AVG(uptime_percentage) as avg_uptime,
                   COUNT(*) as total_measurements
            FROM `tabAnalytics Reliability`
            WHERE analytics = %s
            AND reliability_date >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """, self.name, as_dict=True)[0]
        
        if reliability_data['total_measurements'] > 0:
            reliability = (reliability_data['avg_availability'] + reliability_data['avg_uptime']) / 2
            return round(reliability, 2)
        else:
            return 0

    def update_analytics_settings(self):
        """Update analytics-specific settings"""
        # Update analytics preferences
        if self.preferences:
            frappe.db.set_value("Real Time Analytics", self.name, "preferences", json.dumps(self.preferences))
        
        # Update analytics tags
        if self.tags:
            frappe.db.set_value("Real Time Analytics", self.name, "tags", json.dumps(self.tags))

    def setup_analytics_permissions(self):
        """Setup analytics-specific permissions"""
        # Create analytics-specific roles
        analytics_roles = [
            f"Analytics - {self.analytics_id}",
            f"Type - {self.analytics_type}",
            f"Category - {self.analytics_category}"
        ]
        
        for role_name in analytics_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_analytics_insights(self):
        """Generate analytics insights"""
        insights = {
            "performance_score": self.performance_score,
            "accuracy_score": self.accuracy_score,
            "efficiency_score": self.efficiency_score,
            "reliability_score": self.reliability_score,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.analytics_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify analytics optimization opportunities"""
        opportunities = []
        
        # Check for performance improvements
        if self.performance_score < 80:
            opportunities.append("Optimize analytics performance")
        
        # Check for accuracy improvements
        if self.accuracy_score < 90:
            opportunities.append("Improve analytics accuracy")
        
        # Check for efficiency improvements
        if self.efficiency_score < 85:
            opportunities.append("Enhance analytics efficiency")
        
        # Check for reliability improvements
        if self.reliability_score < 95:
            opportunities.append("Improve analytics reliability")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.analytics_status == "Active":
            actions.append("Monitor analytics performance")
            actions.append("Update analytics configuration")
            actions.append("Optimize analytics settings")
        elif self.analytics_status == "Testing":
            actions.append("Complete analytics testing")
            actions.append("Validate analytics performance")
            actions.append("Deploy analytics system")
        else:
            actions.append("Review analytics status")
            actions.append("Take appropriate action")
        
        return actions

    def create_analytics_profile(self):
        """Create comprehensive analytics profile"""
        profile_data = {
            "analytics_id": self.analytics_id,
            "analytics_name": self.analytics_name,
            "analytics_type": self.analytics_type,
            "analytics_category": self.analytics_category,
            "analytics_status": self.analytics_status,
            "analytics_priority": self.analytics_priority,
            "performance_score": self.performance_score,
            "accuracy_score": self.accuracy_score,
            "efficiency_score": self.efficiency_score,
            "reliability_score": self.reliability_score,
            "is_real_time_enabled": self.is_real_time_enabled
        }
        
        frappe.get_doc({
            "doctype": "Analytics Profile",
            "analytics": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_analytics_workflow(self):
        """Setup analytics workflow"""
        workflow_data = {
            "analytics": self.name,
            "workflow_type": "Analytics Management",
            "steps": [
                {"step": "Analytics Configuration", "status": "Completed"},
                {"step": "Analytics Testing", "status": "Pending"},
                {"step": "Analytics Deployment", "status": "Pending"},
                {"step": "Analytics Monitoring", "status": "Pending"},
                {"step": "Analytics Optimization", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Analytics Workflow",
            "analytics": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_analytics_dashboard(self):
        """Create analytics dashboard"""
        dashboard_data = {
            "analytics": self.name,
            "dashboard_type": "Real-time Analytics",
            "widgets": [
                {"widget": "Performance Metrics", "status": "Active"},
                {"widget": "Accuracy Metrics", "status": "Active"},
                {"widget": "Efficiency Metrics", "status": "Active"},
                {"widget": "Reliability Metrics", "status": "Active"},
                {"widget": "Trend Analysis", "status": "Active"},
                {"widget": "Alert System", "status": "Active"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Analytics Dashboard",
            "analytics": self.name,
            "dashboard_data": json.dumps(dashboard_data)
        }).insert(ignore_permissions=True)

    def initialize_analytics_tracking(self):
        """Initialize analytics tracking"""
        tracking_data = {
            "analytics": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "measurement_count": 0,
            "alert_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Analytics Tracking",
            "analytics": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_analytics_dashboard(self):
        """Update analytics dashboard"""
        # Calculate updated metrics
        updated_metrics = {
            "performance_score": self.calculate_performance_score(),
            "accuracy_score": self.calculate_accuracy_score(),
            "efficiency_score": self.calculate_efficiency_score(),
            "reliability_score": self.calculate_reliability_score()
        }
        
        # Update dashboard record
        dashboard = frappe.get_doc("Analytics Dashboard", {"analytics": self.name})
        if dashboard:
            dashboard.dashboard_data = json.dumps({
                "analytics": self.name,
                "dashboard_type": "Real-time Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_analytics_insights(),
                "updated_date": now().isoformat()
            })
            dashboard.save()

    def sync_analytics_data(self):
        """Sync analytics data across systems"""
        # Sync with external analytics systems if configured
        if self.external_analytics_system_id:
            self.sync_with_external_analytics_system()

    def update_analytics_status(self):
        """Update analytics status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Analytics Tracking", {"analytics": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_analytics_changes(self):
        """Process analytics changes"""
        # Log analytics changes
        self.log_analytics_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Analytics Status Change",
            "analytics": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.analytics_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabAnalytics Status Change`
            WHERE analytics = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Analytics Status Change", {"analytics": self.name}) else "New"
        
        return previous_status

    def log_analytics_changes(self):
        """Log analytics changes"""
        frappe.get_doc({
            "doctype": "Analytics Change Log",
            "analytics": self.name,
            "change_type": "Update",
            "change_description": "Analytics information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update analytics performance
        self.update_analytics_performance()
        
        # Update analytics accuracy
        self.update_analytics_accuracy()

    def update_analytics_performance(self):
        """Update analytics performance"""
        # Update performance status
        frappe.db.sql("""
            UPDATE `tabAnalytics Performance`
            SET analytics_status = %s
            WHERE analytics = %s
        """, (self.analytics_status, self.name))

    def update_analytics_accuracy(self):
        """Update analytics accuracy"""
        # Update accuracy status
        frappe.db.sql("""
            UPDATE `tabAnalytics Accuracy`
            SET analytics_status = %s
            WHERE analytics = %s
        """, (self.analytics_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify analytics users
        self.notify_analytics_users()
        
        # Notify analytics administrators
        self.notify_analytics_administrators()

    def notify_analytics_users(self):
        """Notify analytics users"""
        frappe.get_doc({
            "doctype": "Analytics Notification",
            "analytics": self.name,
            "notification_type": "Analytics Update",
            "message": f"Analytics {self.analytics_name} has been updated",
            "recipients": "Analytics Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_analytics_administrators(self):
        """Notify analytics administrators"""
        frappe.get_doc({
            "doctype": "Analytics Notification",
            "analytics": self.name,
            "notification_type": "Analytics Update",
            "message": f"Analytics {self.analytics_name} has been updated",
            "recipients": "Analytics Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_analytics_system(self):
        """Sync analytics data with external analytics system"""
        # Implementation for external analytics system sync
        pass

    @frappe.whitelist()
    def get_analytics_dashboard_data(self):
        """Get analytics dashboard data"""
        return {
            "analytics_id": self.analytics_id,
            "analytics_name": self.analytics_name,
            "analytics_type": self.analytics_type,
            "analytics_category": self.analytics_category,
            "analytics_status": self.analytics_status,
            "analytics_priority": self.analytics_priority,
            "performance_score": self.performance_score,
            "accuracy_score": self.accuracy_score,
            "efficiency_score": self.efficiency_score,
            "reliability_score": self.reliability_score,
            "is_real_time_enabled": self.is_real_time_enabled,
            "insights": self.generate_analytics_insights()
        }

    @frappe.whitelist()
    def get_real_time_metrics(self):
        """Get real-time metrics"""
        return {
            "performance_score": self.performance_score,
            "accuracy_score": self.accuracy_score,
            "efficiency_score": self.efficiency_score,
            "reliability_score": self.reliability_score,
            "timestamp": now().isoformat()
        }

    @frappe.whitelist()
    def get_analytics_insights(self):
        """Get analytics insights"""
        return {
            "performance_score": self.performance_score,
            "accuracy_score": self.accuracy_score,
            "efficiency_score": self.efficiency_score,
            "reliability_score": self.reliability_score,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
