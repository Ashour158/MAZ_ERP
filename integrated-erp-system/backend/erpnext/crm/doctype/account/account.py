# Enhanced Account - With Advanced Coding System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta

class Account(Document):
    def validate(self):
        """Validate account data"""
        self.validate_account_data()
        self.set_defaults()
        self.generate_account_code()
        self.calculate_account_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_account_settings()
        self.setup_account_permissions()
        self.generate_account_insights()

    def after_insert(self):
        """Process after inserting new account"""
        self.create_account_profile()
        self.setup_account_workflow()
        self.create_account_analytics()
        self.initialize_account_tracking()

    def on_update(self):
        """Process on account update"""
        self.update_account_analytics()
        self.sync_account_data()
        self.update_account_status()
        self.process_account_changes()

    def validate_account_data(self):
        """Validate account information"""
        if not self.account_name:
            frappe.throw(_("Account name is required"))
        
        if not self.account_type:
            frappe.throw(_("Account type is required"))

    def set_defaults(self):
        """Set default values for new account"""
        if not self.account_status:
            self.account_status = "Active"
        
        if not self.account_priority:
            self.account_priority = "Medium"
        
        if not self.account_category:
            self.account_category = "General"
        
        if not self.is_primary:
            self.is_primary = 0

    def generate_account_code(self):
        """Generate account code based on coding system"""
        if not self.code and self.account_status == "Active":
            # Get coding system for accounts
            coding_system = frappe.get_doc("Coding System", {"coding_type": "Account", "coding_status": "Active"})
            
            if coding_system and coding_system.is_auto_generation_enabled:
                # Generate code
                code_result = coding_system.generate_code(
                    record_data=self.as_dict(),
                    territory=self.territory
                )
                
                if code_result.get('status') == 'success':
                    self.code = code_result.get('code')
                    self.coding_system = coding_system.name
                    self.code_generated_date = now()
                    self.code_generated_by = frappe.session.user

    def calculate_account_metrics(self):
        """Calculate account metrics"""
        # Calculate account score
        self.account_score = self.calculate_account_score()
        
        # Calculate account value
        self.account_value = self.calculate_account_value()
        
        # Calculate account health
        self.account_health = self.calculate_account_health()
        
        # Calculate account potential
        self.account_potential = self.calculate_account_potential()

    def calculate_account_score(self):
        """Calculate account score"""
        score = 0
        
        # Basic information score
        if self.account_name:
            score += 15
        
        if self.account_type:
            score += 10
        
        if self.industry:
            score += 10
        
        if self.territory:
            score += 10
        
        # Contact information score
        if self.primary_contact:
            score += 15
        
        if self.email:
            score += 10
        
        if self.phone:
            score += 10
        
        # Address information score
        if self.billing_address:
            score += 10
        
        if self.shipping_address:
            score += 10
        
        return min(score, 100)

    def calculate_account_value(self):
        """Calculate account value"""
        # Get account value from opportunities and sales
        value_data = frappe.db.sql("""
            SELECT SUM(deal_value) as total_value,
                   COUNT(*) as opportunity_count
            FROM `tabOpportunity`
            WHERE account = %s
            AND status IN ('Open', 'Qualified', 'Proposal/Price Quote')
        """, self.name, as_dict=True)[0]
        
        if value_data['total_value']:
            return round(value_data['total_value'], 2)
        else:
            return 0

    def calculate_account_health(self):
        """Calculate account health"""
        # Get account health from various factors
        health_score = 0
        
        # Opportunity health
        opportunity_health = self.get_opportunity_health()
        health_score += opportunity_health * 0.4
        
        # Communication health
        communication_health = self.get_communication_health()
        health_score += communication_health * 0.3
        
        # Activity health
        activity_health = self.get_activity_health()
        health_score += activity_health * 0.3
        
        if health_score >= 80:
            return "Excellent"
        elif health_score >= 60:
            return "Good"
        elif health_score >= 40:
            return "Fair"
        else:
            return "Poor"

    def calculate_account_potential(self):
        """Calculate account potential"""
        # Get account potential from various factors
        potential_score = 0
        
        # Industry potential
        industry_potential = self.get_industry_potential()
        potential_score += industry_potential * 0.3
        
        # Size potential
        size_potential = self.get_size_potential()
        potential_score += size_potential * 0.3
        
        # Relationship potential
        relationship_potential = self.get_relationship_potential()
        potential_score += relationship_potential * 0.4
        
        if potential_score >= 80:
            return "High"
        elif potential_score >= 60:
            return "Medium"
        elif potential_score >= 40:
            return "Low"
        else:
            return "Very Low"

    def get_opportunity_health(self):
        """Get opportunity health score"""
        # Get opportunity data
        opportunity_data = frappe.db.sql("""
            SELECT COUNT(*) as total_opportunities,
                   SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_opportunities,
                   AVG(deal_value) as avg_deal_value
            FROM `tabOpportunity`
            WHERE account = %s
        """, self.name, as_dict=True)[0]
        
        if opportunity_data['total_opportunities'] > 0:
            open_ratio = opportunity_data['open_opportunities'] / opportunity_data['total_opportunities']
            value_score = min(100, (opportunity_data['avg_deal_value'] or 0) / 1000)
            return (open_ratio * 50) + (value_score * 0.5)
        else:
            return 0

    def get_communication_health(self):
        """Get communication health score"""
        # Get communication data
        communication_data = frappe.db.sql("""
            SELECT COUNT(*) as total_communications,
                   AVG(DATEDIFF(NOW(), communication_date)) as avg_days_since
            FROM `tabCommunication`
            WHERE reference_doctype = 'Account'
            AND reference_name = %s
            AND communication_date >= DATE_SUB(NOW(), INTERVAL 90 DAYS)
        """, self.name, as_dict=True)[0]
        
        if communication_data['total_communications'] > 0:
            frequency_score = min(100, communication_data['total_communications'] * 10)
            recency_score = max(0, 100 - (communication_data['avg_days_since'] or 0))
            return (frequency_score + recency_score) / 2
        else:
            return 0

    def get_activity_health(self):
        """Get activity health score"""
        # Get activity data
        activity_data = frappe.db.sql("""
            SELECT COUNT(*) as total_activities,
                   AVG(DATEDIFF(NOW(), activity_date)) as avg_days_since
            FROM `tabActivity`
            WHERE account = %s
            AND activity_date >= DATE_SUB(NOW(), INTERVAL 90 DAYS)
        """, self.name, as_dict=True)[0]
        
        if activity_data['total_activities'] > 0:
            frequency_score = min(100, activity_data['total_activities'] * 10)
            recency_score = max(0, 100 - (activity_data['avg_days_since'] or 0))
            return (frequency_score + recency_score) / 2
        else:
            return 0

    def get_industry_potential(self):
        """Get industry potential score"""
        # Industry potential mapping
        industry_potential = {
            "Technology": 90,
            "Healthcare": 85,
            "Finance": 80,
            "Manufacturing": 75,
            "Retail": 70,
            "Education": 65,
            "Government": 60,
            "Non-profit": 55,
            "Other": 50
        }
        
        return industry_potential.get(self.industry, 50)

    def get_size_potential(self):
        """Get size potential score"""
        # Size potential mapping
        size_potential = {
            "Enterprise": 90,
            "Large": 80,
            "Medium": 70,
            "Small": 60,
            "Startup": 50
        }
        
        return size_potential.get(self.account_size, 50)

    def get_relationship_potential(self):
        """Get relationship potential score"""
        # Get relationship data
        relationship_data = frappe.db.sql("""
            SELECT COUNT(*) as total_contacts,
                   COUNT(CASE WHEN is_primary = 1 THEN 1 END) as primary_contacts,
                   AVG(contact_score) as avg_contact_score
            FROM `tabContact`
            WHERE account = %s
        """, self.name, as_dict=True)[0]
        
        if relationship_data['total_contacts'] > 0:
            contact_score = min(100, relationship_data['total_contacts'] * 20)
            primary_score = min(100, relationship_data['primary_contacts'] * 30)
            quality_score = relationship_data['avg_contact_score'] or 0
            return (contact_score + primary_score + quality_score) / 3
        else:
            return 0

    def update_account_settings(self):
        """Update account-specific settings"""
        # Update account preferences
        if self.preferences:
            frappe.db.set_value("Account", self.name, "preferences", json.dumps(self.preferences))
        
        # Update account tags
        if self.tags:
            frappe.db.set_value("Account", self.name, "tags", json.dumps(self.tags))

    def setup_account_permissions(self):
        """Setup account-specific permissions"""
        # Create account-specific roles
        account_roles = [
            f"Account - {self.name}",
            f"Territory - {self.territory}",
            f"Category - {self.account_category}"
        ]
        
        for role_name in account_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_account_insights(self):
        """Generate account insights"""
        insights = {
            "account_score": self.account_score,
            "account_value": self.account_value,
            "account_health": self.account_health,
            "account_potential": self.account_potential,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.account_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify account optimization opportunities"""
        opportunities = []
        
        # Check for missing information
        if not self.primary_contact:
            opportunities.append("Add primary contact")
        
        if not self.email:
            opportunities.append("Add email address")
        
        if not self.phone:
            opportunities.append("Add phone number")
        
        if not self.territory:
            opportunities.append("Assign territory")
        
        # Check for health improvements
        if self.account_health == "Poor":
            opportunities.append("Improve account health")
        
        # Check for potential improvements
        if self.account_potential == "Very Low":
            opportunities.append("Increase account potential")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.account_status == "Active":
            actions.append("Monitor account health")
            actions.append("Update account information")
            actions.append("Schedule follow-up")
        elif self.account_status == "Inactive":
            actions.append("Re-engage account")
            actions.append("Update account status")
            actions.append("Review account information")
        else:
            actions.append("Review account status")
            actions.append("Take appropriate action")
        
        return actions

    def create_account_profile(self):
        """Create comprehensive account profile"""
        profile_data = {
            "account_id": self.name,
            "account_name": self.account_name,
            "account_type": self.account_type,
            "industry": self.industry,
            "territory": self.territory,
            "account_status": self.account_status,
            "account_priority": self.account_priority,
            "account_category": self.account_category,
            "account_score": self.account_score,
            "account_value": self.account_value,
            "account_health": self.account_health,
            "account_potential": self.account_potential,
            "code": self.code,
            "coding_system": self.coding_system
        }
        
        frappe.get_doc({
            "doctype": "Account Profile",
            "account": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_account_workflow(self):
        """Setup account workflow"""
        workflow_data = {
            "account": self.name,
            "workflow_type": "Account Management",
            "steps": [
                {"step": "Account Creation", "status": "Completed"},
                {"step": "Account Validation", "status": "Pending"},
                {"step": "Account Activation", "status": "Pending"},
                {"step": "Account Engagement", "status": "Pending"},
                {"step": "Account Maintenance", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Account Workflow",
            "account": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_account_analytics(self):
        """Create account analytics"""
        analytics_data = {
            "account": self.name,
            "analytics_type": "Account Analytics",
            "metrics": {
                "account_score": self.account_score,
                "account_value": self.account_value,
                "account_health": self.account_health,
                "account_potential": self.account_potential
            },
            "insights": self.generate_account_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Account Analytics",
            "account": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_account_tracking(self):
        """Initialize account tracking"""
        tracking_data = {
            "account": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "opportunity_count": 0,
            "value_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Account Tracking",
            "account": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_account_analytics(self):
        """Update account analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "account_score": self.calculate_account_score(),
            "account_value": self.calculate_account_value(),
            "account_health": self.calculate_account_health(),
            "account_potential": self.calculate_account_potential()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Account Analytics", {"account": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "account": self.name,
                "analytics_type": "Account Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_account_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_account_data(self):
        """Sync account data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_account_status(self):
        """Update account status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Account Tracking", {"account": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_account_changes(self):
        """Process account changes"""
        # Log account changes
        self.log_account_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Account Status Change",
            "account": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.account_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabAccount Status Change`
            WHERE account = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Account Status Change", {"account": self.name}) else "New"
        
        return previous_status

    def log_account_changes(self):
        """Log account changes"""
        frappe.get_doc({
            "doctype": "Account Change Log",
            "account": self.name,
            "change_type": "Update",
            "change_description": "Account information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update account opportunities
        self.update_account_opportunities()
        
        # Update account contacts
        self.update_account_contacts()

    def update_account_opportunities(self):
        """Update account opportunities"""
        # Update opportunity status
        frappe.db.sql("""
            UPDATE `tabOpportunity`
            SET account_status = %s
            WHERE account = %s
        """, (self.account_status, self.name))

    def update_account_contacts(self):
        """Update account contacts"""
        # Update contact status
        frappe.db.sql("""
            UPDATE `tabContact`
            SET account_status = %s
            WHERE account = %s
        """, (self.account_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify account users
        self.notify_account_users()
        
        # Notify account administrators
        self.notify_account_administrators()

    def notify_account_users(self):
        """Notify account users"""
        frappe.get_doc({
            "doctype": "Account Notification",
            "account": self.name,
            "notification_type": "Account Update",
            "message": f"Account {self.account_name} has been updated",
            "recipients": "Account Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_account_administrators(self):
        """Notify account administrators"""
        frappe.get_doc({
            "doctype": "Account Notification",
            "account": self.name,
            "notification_type": "Account Update",
            "message": f"Account {self.account_name} has been updated",
            "recipients": "Account Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync account data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_account_dashboard_data(self):
        """Get account dashboard data"""
        return {
            "account_id": self.name,
            "account_name": self.account_name,
            "account_type": self.account_type,
            "industry": self.industry,
            "territory": self.territory,
            "account_status": self.account_status,
            "account_priority": self.account_priority,
            "account_category": self.account_category,
            "account_score": self.account_score,
            "account_value": self.account_value,
            "account_health": self.account_health,
            "account_potential": self.account_potential,
            "code": self.code,
            "coding_system": self.coding_system,
            "insights": self.generate_account_insights()
        }

    @frappe.whitelist()
    def get_account_insights(self):
        """Get account insights"""
        return {
            "account_score": self.account_score,
            "account_value": self.account_value,
            "account_health": self.account_health,
            "account_potential": self.account_potential,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }

    @frappe.whitelist()
    def export_account_data(self):
        """Export account data with code"""
        try:
            # Get account data with code
            account_data = {
                "id": self.name,
                "code": self.code,
                "name": self.account_name,
                "type": self.account_type,
                "industry": self.industry,
                "territory": self.territory,
                "status": self.account_status,
                "priority": self.account_priority,
                "category": self.account_category,
                "score": self.account_score,
                "value": self.account_value,
                "health": self.account_health,
                "potential": self.account_potential,
                "created_date": self.creation,
                "modified_date": self.modified
            }
            
            # Log export
            frappe.get_doc({
                "doctype": "Account Export",
                "account": self.name,
                "export_data": json.dumps(account_data),
                "export_date": now(),
                "exported_by": frappe.session.user
            }).insert(ignore_permissions=True)
            
            return {
                "status": "success",
                "data": account_data,
                "message": "Account data exported successfully with code"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Export failed: {str(e)}"
            }
