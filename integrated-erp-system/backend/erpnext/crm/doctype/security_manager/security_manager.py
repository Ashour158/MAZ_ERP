# Security Manager - Advanced Security Management

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET
import hashlib
import secrets
import string

class SecurityManager(Document):
    def autoname(self):
        """Generate unique security manager ID"""
        if not self.security_manager_id:
            self.security_manager_id = make_autoname("SEC-.YYYY.-.MM.-.#####")
        self.name = self.security_manager_id

    def validate(self):
        """Validate security manager data"""
        self.validate_security_data()
        self.set_defaults()
        self.validate_security_configuration()
        self.calculate_security_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_security_settings()
        self.setup_security_permissions()
        self.generate_security_insights()

    def after_insert(self):
        """Process after inserting new security manager"""
        self.create_security_profile()
        self.setup_security_workflow()
        self.create_security_analytics()
        self.initialize_security_tracking()

    def on_update(self):
        """Process on security manager update"""
        self.update_security_analytics()
        self.sync_security_data()
        self.update_security_status()
        self.process_security_changes()

    def validate_security_data(self):
        """Validate security manager information"""
        if not self.security_manager_name:
            frappe.throw(_("Security manager name is required"))
        
        if not self.security_type:
            frappe.throw(_("Security type is required"))
        
        if not self.security_configuration:
            frappe.throw(_("Security configuration is required"))

    def validate_security_configuration(self):
        """Validate security configuration"""
        if not self.security_configuration:
            frappe.throw(_("Security configuration is required"))
        
        # Validate security configuration format
        try:
            config = json.loads(self.security_configuration)
            if not isinstance(config, dict):
                frappe.throw(_("Security configuration must be a valid JSON object"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format in security configuration"))

    def set_defaults(self):
        """Set default values for new security manager"""
        if not self.security_status:
            self.security_status = "Active"
        
        if not self.security_priority:
            self.security_priority = "High"
        
        if not self.security_category:
            self.security_category = "General"
        
        if not self.is_security_enabled:
            self.is_security_enabled = 1

    def calculate_security_metrics(self):
        """Calculate security metrics"""
        # Calculate security score
        self.security_score = self.calculate_security_score()
        
        # Calculate threat level
        self.threat_level = self.calculate_threat_level()
        
        # Calculate compliance score
        self.compliance_score = self.calculate_compliance_score()
        
        # Calculate risk score
        self.risk_score = self.calculate_risk_score()

    def calculate_security_score(self):
        """Calculate security score"""
        # Get security data
        security_data = frappe.db.sql("""
            SELECT AVG(security_score) as avg_security_score,
                   COUNT(*) as total_checks
            FROM `tabSecurity Check`
            WHERE security_manager = %s
            AND check_date >= DATE_SUB(NOW(), INTERVAL 24 HOURS)
        """, self.name, as_dict=True)[0]
        
        if security_data['total_checks'] > 0:
            return round(security_data['avg_security_score'], 2)
        else:
            return 0

    def calculate_threat_level(self):
        """Calculate threat level"""
        # Get threat data
        threat_data = frappe.db.sql("""
            SELECT COUNT(*) as threat_count,
                   AVG(threat_severity) as avg_threat_severity
            FROM `tabSecurity Threat`
            WHERE security_manager = %s
            AND threat_date >= DATE_SUB(NOW(), INTERVAL 24 HOURS)
        """, self.name, as_dict=True)[0]
        
        if threat_data['threat_count'] > 0:
            if threat_data['avg_threat_severity'] >= 8:
                return "Critical"
            elif threat_data['avg_threat_severity'] >= 6:
                return "High"
            elif threat_data['avg_threat_severity'] >= 4:
                return "Medium"
            else:
                return "Low"
        else:
            return "Low"

    def calculate_compliance_score(self):
        """Calculate compliance score"""
        # Get compliance data
        compliance_data = frappe.db.sql("""
            SELECT AVG(compliance_score) as avg_compliance_score,
                   COUNT(*) as total_checks
            FROM `tabCompliance Check`
            WHERE security_manager = %s
            AND check_date >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
        """, self.name, as_dict=True)[0]
        
        if compliance_data['total_checks'] > 0:
            return round(compliance_data['avg_compliance_score'], 2)
        else:
            return 0

    def calculate_risk_score(self):
        """Calculate risk score"""
        # Get risk data
        risk_data = frappe.db.sql("""
            SELECT AVG(risk_score) as avg_risk_score,
                   COUNT(*) as total_risks
            FROM `tabSecurity Risk`
            WHERE security_manager = %s
            AND risk_date >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
        """, self.name, as_dict=True)[0]
        
        if risk_data['total_risks'] > 0:
            return round(risk_data['avg_risk_score'], 2)
        else:
            return 0

    def update_security_settings(self):
        """Update security-specific settings"""
        # Update security preferences
        if self.preferences:
            frappe.db.set_value("Security Manager", self.name, "preferences", json.dumps(self.preferences))
        
        # Update security tags
        if self.tags:
            frappe.db.set_value("Security Manager", self.name, "tags", json.dumps(self.tags))

    def setup_security_permissions(self):
        """Setup security-specific permissions"""
        # Create security-specific roles
        security_roles = [
            f"Security - {self.security_manager_id}",
            f"Type - {self.security_type}",
            f"Category - {self.security_category}"
        ]
        
        for role_name in security_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_security_insights(self):
        """Generate security insights"""
        insights = {
            "security_score": self.security_score,
            "threat_level": self.threat_level,
            "compliance_score": self.compliance_score,
            "risk_score": self.risk_score,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.security_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify security optimization opportunities"""
        opportunities = []
        
        # Check for security improvements
        if self.security_score < 80:
            opportunities.append("Improve security measures")
        
        # Check for threat mitigation
        if self.threat_level in ["High", "Critical"]:
            opportunities.append("Mitigate security threats")
        
        # Check for compliance improvements
        if self.compliance_score < 90:
            opportunities.append("Improve compliance measures")
        
        # Check for risk reduction
        if self.risk_score > 70:
            opportunities.append("Reduce security risks")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.security_status == "Active":
            actions.append("Monitor security status")
            actions.append("Update security measures")
            actions.append("Review security policies")
        elif self.security_status == "Testing":
            actions.append("Complete security testing")
            actions.append("Validate security measures")
            actions.append("Deploy security system")
        else:
            actions.append("Review security status")
            actions.append("Take appropriate action")
        
        return actions

    def create_security_profile(self):
        """Create comprehensive security profile"""
        profile_data = {
            "security_manager_id": self.security_manager_id,
            "security_manager_name": self.security_manager_name,
            "security_type": self.security_type,
            "security_category": self.security_category,
            "security_status": self.security_status,
            "security_priority": self.security_priority,
            "security_score": self.security_score,
            "threat_level": self.threat_level,
            "compliance_score": self.compliance_score,
            "risk_score": self.risk_score,
            "is_security_enabled": self.is_security_enabled
        }
        
        frappe.get_doc({
            "doctype": "Security Profile",
            "security_manager": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_security_workflow(self):
        """Setup security workflow"""
        workflow_data = {
            "security_manager": self.name,
            "workflow_type": "Security Management",
            "steps": [
                {"step": "Security Configuration", "status": "Completed"},
                {"step": "Security Testing", "status": "Pending"},
                {"step": "Security Deployment", "status": "Pending"},
                {"step": "Security Monitoring", "status": "Pending"},
                {"step": "Security Optimization", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Security Workflow",
            "security_manager": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_security_analytics(self):
        """Create security analytics"""
        analytics_data = {
            "security_manager": self.name,
            "analytics_type": "Security Analytics",
            "metrics": {
                "security_score": self.security_score,
                "threat_level": self.threat_level,
                "compliance_score": self.compliance_score,
                "risk_score": self.risk_score
            },
            "insights": self.generate_security_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Security Analytics",
            "security_manager": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_security_tracking(self):
        """Initialize security tracking"""
        tracking_data = {
            "security_manager": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "threat_count": 0,
            "incident_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Security Tracking",
            "security_manager": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_security_analytics(self):
        """Update security analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "security_score": self.calculate_security_score(),
            "threat_level": self.calculate_threat_level(),
            "compliance_score": self.calculate_compliance_score(),
            "risk_score": self.calculate_risk_score()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Security Analytics", {"security_manager": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "security_manager": self.name,
                "analytics_type": "Security Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_security_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_security_data(self):
        """Sync security data across systems"""
        # Sync with external security systems if configured
        if self.external_security_system_id:
            self.sync_with_external_security_system()

    def update_security_status(self):
        """Update security status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Security Tracking", {"security_manager": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_security_changes(self):
        """Process security changes"""
        # Log security changes
        self.log_security_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Security Status Change",
            "security_manager": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.security_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabSecurity Status Change`
            WHERE security_manager = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Security Status Change", {"security_manager": self.name}) else "New"
        
        return previous_status

    def log_security_changes(self):
        """Log security changes"""
        frappe.get_doc({
            "doctype": "Security Change Log",
            "security_manager": self.name,
            "change_type": "Update",
            "change_description": "Security information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update security checks
        self.update_security_checks()
        
        # Update security threats
        self.update_security_threats()

    def update_security_checks(self):
        """Update security checks"""
        # Update check status
        frappe.db.sql("""
            UPDATE `tabSecurity Check`
            SET security_manager_status = %s
            WHERE security_manager = %s
        """, (self.security_status, self.name))

    def update_security_threats(self):
        """Update security threats"""
        # Update threat status
        frappe.db.sql("""
            UPDATE `tabSecurity Threat`
            SET security_manager_status = %s
            WHERE security_manager = %s
        """, (self.security_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify security users
        self.notify_security_users()
        
        # Notify security administrators
        self.notify_security_administrators()

    def notify_security_users(self):
        """Notify security users"""
        frappe.get_doc({
            "doctype": "Security Notification",
            "security_manager": self.name,
            "notification_type": "Security Update",
            "message": f"Security {self.security_manager_name} has been updated",
            "recipients": "Security Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_security_administrators(self):
        """Notify security administrators"""
        frappe.get_doc({
            "doctype": "Security Notification",
            "security_manager": self.name,
            "notification_type": "Security Update",
            "message": f"Security {self.security_manager_name} has been updated",
            "recipients": "Security Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_security_system(self):
        """Sync security data with external security system"""
        # Implementation for external security system sync
        pass

    @frappe.whitelist()
    def get_security_dashboard_data(self):
        """Get security dashboard data"""
        return {
            "security_manager_id": self.security_manager_id,
            "security_manager_name": self.security_manager_name,
            "security_type": self.security_type,
            "security_category": self.security_category,
            "security_status": self.security_status,
            "security_priority": self.security_priority,
            "security_score": self.security_score,
            "threat_level": self.threat_level,
            "compliance_score": self.compliance_score,
            "risk_score": self.risk_score,
            "is_security_enabled": self.is_security_enabled,
            "insights": self.generate_security_insights()
        }

    @frappe.whitelist()
    def get_security_insights(self):
        """Get security insights"""
        return {
            "security_score": self.security_score,
            "threat_level": self.threat_level,
            "compliance_score": self.compliance_score,
            "risk_score": self.risk_score,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }

    @frappe.whitelist()
    def generate_security_report(self):
        """Generate security report"""
        try:
            # Generate security report
            report_data = self.get_security_report_data()
            
            # Log report generation
            frappe.get_doc({
                "doctype": "Security Report",
                "security_manager": self.name,
                "report_type": "Security Report",
                "report_data": json.dumps(report_data),
                "report_date": now(),
                "generated_by": frappe.session.user
            }).insert(ignore_permissions=True)
            
            return {
                "status": "success",
                "message": "Security report generated successfully",
                "report_data": report_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Security report generation failed: {str(e)}"
            }

    def get_security_report_data(self):
        """Get security report data"""
        return {
            "security_score": self.security_score,
            "threat_level": self.threat_level,
            "compliance_score": self.compliance_score,
            "risk_score": self.risk_score,
            "security_insights": self.generate_security_insights(),
            "report_date": now().isoformat()
        }
