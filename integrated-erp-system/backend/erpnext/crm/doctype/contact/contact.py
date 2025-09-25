# Enhanced Contact DocType - Complete Contact Management with Full Integration

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class Contact(Document):
    def autoname(self):
        """Generate unique contact ID"""
        if not self.contact_id:
            self.contact_id = make_autoname("CON-.YYYY.-.MM.-.#####")
        self.name = self.contact_id

    def validate(self):
        """Validate contact data"""
        self.validate_contact_data()
        self.set_defaults()
        self.validate_contact_info()
        self.calculate_contact_metrics()
        self.determine_contact_priority()

    def before_save(self):
        """Process before saving"""
        self.update_contact_settings()
        self.setup_contact_permissions()
        self.generate_contact_insights()

    def after_insert(self):
        """Process after inserting new contact"""
        self.create_contact_profile()
        self.setup_contact_workflow()
        self.create_contact_analytics()
        self.initialize_contact_tracking()

    def on_update(self):
        """Process on contact update"""
        self.update_contact_analytics()
        self.sync_contact_data()
        self.update_contact_priority()
        self.process_contact_changes()

    def validate_contact_data(self):
        """Validate contact information"""
        if not self.first_name:
            frappe.throw(_("First name is required"))
        
        if not self.last_name:
            frappe.throw(_("Last name is required"))
        
        if not self.customer:
            frappe.throw(_("Customer is required"))

    def validate_contact_info(self):
        """Validate contact information"""
        if self.email_id and not self.validate_email():
            frappe.throw(_("Invalid email format"))
        
        if self.mobile_no and not self.validate_mobile():
            frappe.throw(_("Invalid mobile number format"))

    def set_defaults(self):
        """Set default values for new contact"""
        if not self.contact_type:
            self.contact_type = "Individual"
        
        if not self.contact_status:
            self.contact_status = "Active"
        
        if not self.contact_priority:
            self.contact_priority = "Medium"
        
        if not self.is_primary_contact:
            self.is_primary_contact = 0

    def calculate_contact_metrics(self):
        """Calculate contact metrics"""
        # Calculate contact engagement score
        self.contact_engagement_score = self.calculate_engagement_score()
        
        # Calculate contact influence score
        self.contact_influence_score = self.calculate_influence_score()
        
        # Calculate contact communication frequency
        self.communication_frequency = self.calculate_communication_frequency()
        
        # Calculate contact response rate
        self.response_rate = self.calculate_response_rate()

    def calculate_engagement_score(self):
        """Calculate contact engagement score"""
        # Get recent interactions
        recent_interactions = frappe.db.sql("""
            SELECT COUNT(*) as interaction_count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Contact'
            AND reference_name = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        # Get email opens
        email_opens = frappe.db.sql("""
            SELECT COUNT(*) as open_count
            FROM `tabEmail Open`
            WHERE contact = %s
            AND open_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        # Get meeting attendance
        meeting_attendance = frappe.db.sql("""
            SELECT COUNT(*) as attendance_count
            FROM `tabMeeting Attendance`
            WHERE contact = %s
            AND meeting_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        # Calculate engagement score
        engagement_score = (recent_interactions * 0.4 + 
                           email_opens * 0.3 + 
                           meeting_attendance * 0.3) / 10
        
        return min(engagement_score, 1.0)

    def calculate_influence_score(self):
        """Calculate contact influence score"""
        # Get contact role and designation
        role_score = self.get_role_score()
        
        # Get contact decision making authority
        authority_score = self.get_authority_score()
        
        # Get contact network size
        network_score = self.get_network_score()
        
        # Calculate influence score
        influence_score = (role_score * 0.4 + 
                          authority_score * 0.4 + 
                          network_score * 0.2)
        
        return influence_score

    def get_role_score(self):
        """Get role score"""
        role_scores = {
            "CEO": 1.0,
            "CTO": 0.9,
            "CFO": 0.9,
            "VP": 0.8,
            "Director": 0.7,
            "Manager": 0.6,
            "Senior": 0.5,
            "Junior": 0.3,
            "Intern": 0.1
        }
        
        return role_scores.get(self.designation, 0.5)

    def get_authority_score(self):
        """Get authority score"""
        if self.is_decision_maker:
            return 1.0
        elif self.is_influencer:
            return 0.7
        elif self.is_gatekeeper:
            return 0.5
        else:
            return 0.3

    def get_network_score(self):
        """Get network score"""
        # Get contact connections
        connections = frappe.db.sql("""
            SELECT COUNT(*) as connection_count
            FROM `tabContact Connection`
            WHERE contact = %s
        """, self.name)[0][0]
        
        # Normalize network score
        network_score = min(connections / 100, 1.0)
        
        return network_score

    def calculate_communication_frequency(self):
        """Calculate communication frequency"""
        # Get communication frequency
        communication_count = frappe.db.sql("""
            SELECT COUNT(*) as communication_count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Contact'
            AND reference_name = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        return communication_count

    def calculate_response_rate(self):
        """Calculate response rate"""
        # Get sent emails
        sent_emails = frappe.db.sql("""
            SELECT COUNT(*) as sent_count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Contact'
            AND reference_name = %s
            AND communication_type = 'Communication'
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        # Get responses
        responses = frappe.db.sql("""
            SELECT COUNT(*) as response_count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Contact'
            AND reference_name = %s
            AND communication_type = 'Communication'
            AND is_incoming = 1
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        if sent_emails > 0:
            response_rate = responses / sent_emails
        else:
            response_rate = 0
        
        return response_rate

    def determine_contact_priority(self):
        """Determine contact priority"""
        if self.contact_engagement_score >= 0.8 and self.contact_influence_score >= 0.8:
            self.contact_priority = "High"
        elif self.contact_engagement_score >= 0.6 and self.contact_influence_score >= 0.6:
            self.contact_priority = "Medium"
        else:
            self.contact_priority = "Low"

    def update_contact_settings(self):
        """Update contact-specific settings"""
        # Update contact preferences
        if self.preferences:
            frappe.db.set_value("Contact", self.name, "preferences", json.dumps(self.preferences))
        
        # Update contact tags
        if self.tags:
            frappe.db.set_value("Contact", self.name, "tags", json.dumps(self.tags))

    def setup_contact_permissions(self):
        """Setup contact-specific permissions"""
        # Create contact-specific roles
        contact_roles = [
            f"Contact - {self.contact_id}",
            f"Customer - {self.customer}",
            f"Priority - {self.contact_priority}"
        ]
        
        for role_name in contact_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_contact_insights(self):
        """Generate contact insights"""
        insights = {
            "contact_priority": self.contact_priority,
            "engagement_level": self.determine_engagement_level(),
            "influence_level": self.determine_influence_level(),
            "communication_preferences": self.analyze_communication_preferences(),
            "next_actions": self.recommend_next_actions(),
            "relationship_stage": self.determine_relationship_stage()
        }
        
        self.contact_insights = json.dumps(insights)

    def determine_engagement_level(self):
        """Determine engagement level"""
        if self.contact_engagement_score >= 0.8:
            return "High Engagement"
        elif self.contact_engagement_score >= 0.6:
            return "Medium Engagement"
        else:
            return "Low Engagement"

    def determine_influence_level(self):
        """Determine influence level"""
        if self.contact_influence_score >= 0.8:
            return "High Influence"
        elif self.contact_influence_score >= 0.6:
            return "Medium Influence"
        else:
            return "Low Influence"

    def analyze_communication_preferences(self):
        """Analyze communication preferences"""
        preferences = {
            "preferred_channel": self.get_preferred_channel(),
            "best_time": self.get_best_time(),
            "frequency": self.get_communication_frequency(),
            "response_rate": self.response_rate
        }
        
        return preferences

    def get_preferred_channel(self):
        """Get preferred communication channel"""
        # Analyze communication history
        email_count = frappe.db.sql("""
            SELECT COUNT(*) as email_count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Contact'
            AND reference_name = %s
            AND communication_type = 'Communication'
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        phone_count = frappe.db.sql("""
            SELECT COUNT(*) as phone_count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Contact'
            AND reference_name = %s
            AND communication_type = 'Phone'
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        if email_count > phone_count:
            return "Email"
        elif phone_count > email_count:
            return "Phone"
        else:
            return "Mixed"

    def get_best_time(self):
        """Get best communication time"""
        # Analyze communication patterns
        communication_times = frappe.db.sql("""
            SELECT HOUR(creation) as hour, COUNT(*) as count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Contact'
            AND reference_name = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY HOUR(creation)
            ORDER BY count DESC
            LIMIT 1
        """, self.name, as_dict=True)
        
        if communication_times:
            best_hour = communication_times[0]['hour']
            if 9 <= best_hour <= 17:
                return "Business Hours"
            elif 18 <= best_hour <= 22:
                return "Evening"
            else:
                return "Flexible"
        else:
            return "Business Hours"

    def get_communication_frequency(self):
        """Get communication frequency"""
        if self.communication_frequency >= 10:
            return "High"
        elif self.communication_frequency >= 5:
            return "Medium"
        else:
            return "Low"

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.contact_priority == "High":
            actions.append("Schedule regular check-ins")
            actions.append("Provide personalized service")
            actions.append("Monitor engagement closely")
        elif self.contact_priority == "Medium":
            actions.append("Increase communication frequency")
            actions.append("Build stronger relationship")
            actions.append("Identify growth opportunities")
        else:
            actions.append("Re-engage contact")
            actions.append("Understand contact needs")
            actions.append("Improve communication")
        
        return actions

    def determine_relationship_stage(self):
        """Determine relationship stage"""
        if self.contact_engagement_score >= 0.8 and self.contact_influence_score >= 0.8:
            return "Strategic Partner"
        elif self.contact_engagement_score >= 0.6 and self.contact_influence_score >= 0.6:
            return "Key Contact"
        elif self.contact_engagement_score >= 0.4:
            return "Active Contact"
        else:
            return "Prospect"

    def create_contact_profile(self):
        """Create comprehensive contact profile"""
        profile_data = {
            "contact_id": self.contact_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": f"{self.first_name} {self.last_name}",
            "customer": self.customer,
            "contact_type": self.contact_type,
            "contact_status": self.contact_status,
            "contact_priority": self.contact_priority,
            "designation": self.designation,
            "department": self.department,
            "email_id": self.email_id,
            "mobile_no": self.mobile_no,
            "phone": self.phone,
            "is_primary_contact": self.is_primary_contact,
            "is_decision_maker": self.is_decision_maker,
            "is_influencer": self.is_influencer,
            "is_gatekeeper": self.is_gatekeeper,
            "metrics": {
                "engagement_score": self.contact_engagement_score,
                "influence_score": self.contact_influence_score,
                "communication_frequency": self.communication_frequency,
                "response_rate": self.response_rate
            }
        }
        
        frappe.get_doc({
            "doctype": "Contact Profile",
            "contact": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_contact_workflow(self):
        """Setup contact workflow"""
        workflow_data = {
            "contact": self.name,
            "workflow_type": "Contact Management",
            "steps": [
                {"step": "Initial Contact", "status": "Completed"},
                {"step": "Relationship Building", "status": "Pending"},
                {"step": "Engagement", "status": "Pending"},
                {"step": "Value Delivery", "status": "Pending"},
                {"step": "Partnership", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Contact Workflow",
            "contact": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_contact_analytics(self):
        """Create contact analytics"""
        analytics_data = {
            "contact": self.name,
            "analytics_type": "Contact Analytics",
            "metrics": {
                "engagement_score": self.contact_engagement_score,
                "influence_score": self.contact_influence_score,
                "communication_frequency": self.communication_frequency,
                "response_rate": self.response_rate
            },
            "insights": self.generate_contact_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Contact Analytics",
            "contact": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_contact_tracking(self):
        """Initialize contact tracking"""
        tracking_data = {
            "contact": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "communication_count": 0,
            "meeting_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Contact Tracking",
            "contact": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_contact_analytics(self):
        """Update contact analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "engagement_score": self.contact_engagement_score,
            "influence_score": self.contact_influence_score,
            "communication_frequency": self.communication_frequency,
            "response_rate": self.response_rate
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Contact Analytics", {"contact": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "contact": self.name,
                "analytics_type": "Contact Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_contact_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_contact_data(self):
        """Sync contact data across systems"""
        # Sync with external CRM systems if configured
        if self.external_crm_id:
            self.sync_with_external_crm()

    def update_contact_priority(self):
        """Update contact priority"""
        # Recalculate priority
        self.contact_priority = self.determine_contact_priority()
        
        # Update tracking
        tracking = frappe.get_doc("Contact Tracking", {"contact": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_contact_changes(self):
        """Process contact changes"""
        # Log contact changes
        self.log_contact_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_contact_changes(self):
        """Log contact changes"""
        frappe.get_doc({
            "doctype": "Contact Change Log",
            "contact": self.name,
            "change_type": "Update",
            "change_description": "Contact information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update customer records
        self.update_customer_records()
        
        # Update opportunity records
        self.update_opportunity_records()

    def update_customer_records(self):
        """Update customer records"""
        # Update customer contact count
        frappe.db.sql("""
            UPDATE `tabCustomer`
            SET contact_count = (
                SELECT COUNT(*) FROM `tabContact`
                WHERE customer = %s AND status = 'Active'
            )
            WHERE name = %s
        """, (self.customer, self.customer))

    def update_opportunity_records(self):
        """Update opportunity records"""
        # Update opportunity contact information
        frappe.db.sql("""
            UPDATE `tabOpportunity`
            SET contact_name = %s
            WHERE contact = %s
        """, (f"{self.first_name} {self.last_name}", self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify sales team
        self.notify_sales_team()
        
        # Notify account owner
        self.notify_account_owner()

    def notify_sales_team(self):
        """Notify sales team"""
        frappe.get_doc({
            "doctype": "Contact Notification",
            "contact": self.name,
            "notification_type": "Contact Update",
            "message": f"Contact {self.first_name} {self.last_name} has been updated",
            "recipients": "Sales Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_account_owner(self):
        """Notify account owner"""
        if self.account_owner:
            frappe.get_doc({
                "doctype": "Contact Notification",
                "contact": self.name,
                "notification_type": "Contact Update",
                "message": f"Contact {self.first_name} {self.last_name} has been updated",
                "recipients": self.account_owner,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def validate_email(self):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.email_id) is not None

    def validate_mobile(self):
        """Validate mobile number format"""
        import re
        pattern = r'^\+?[\d\s\-\(\)]+$'
        return re.match(pattern, self.mobile_no) is not None

    def sync_with_external_crm(self):
        """Sync contact data with external CRM"""
        # Implementation for external CRM sync
        pass

    @frappe.whitelist()
    def get_contact_dashboard_data(self):
        """Get contact dashboard data"""
        return {
            "contact_id": self.contact_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": f"{self.first_name} {self.last_name}",
            "customer": self.customer,
            "contact_type": self.contact_type,
            "contact_status": self.contact_status,
            "contact_priority": self.contact_priority,
            "designation": self.designation,
            "department": self.department,
            "email_id": self.email_id,
            "mobile_no": self.mobile_no,
            "phone": self.phone,
            "is_primary_contact": self.is_primary_contact,
            "is_decision_maker": self.is_decision_maker,
            "is_influencer": self.is_influencer,
            "is_gatekeeper": self.is_gatekeeper,
            "metrics": {
                "engagement_score": self.contact_engagement_score,
                "influence_score": self.contact_influence_score,
                "communication_frequency": self.communication_frequency,
                "response_rate": self.response_rate
            },
            "insights": self.generate_contact_insights()
        }

    @frappe.whitelist()
    def get_contact_opportunities(self):
        """Get contact opportunities"""
        opportunities = frappe.db.sql("""
            SELECT 
                name,
                opportunity_name,
                opportunity_amount,
                probability,
                opportunity_stage,
                expected_closing,
                status
            FROM `tabOpportunity`
            WHERE contact = %s
            ORDER BY creation DESC
        """, self.name, as_dict=True)
        
        return opportunities

    @frappe.whitelist()
    def get_contact_communications(self):
        """Get contact communications"""
        communications = frappe.db.sql("""
            SELECT 
                name,
                creation,
                communication_type,
                subject,
                content,
                sender,
                recipient
            FROM `tabCommunication`
            WHERE reference_doctype = 'Contact'
            AND reference_name = %s
            ORDER BY creation DESC
            LIMIT 50
        """, self.name, as_dict=True)
        
        return communications

    @frappe.whitelist()
    def get_contact_activities(self):
        """Get contact activities"""
        activities = frappe.db.sql("""
            SELECT 
                name,
                activity_date,
                activity_type,
                description,
                assigned_to,
                status
            FROM `tabContact Activity`
            WHERE contact = %s
            ORDER BY activity_date DESC
            LIMIT 50
        """, self.name, as_dict=True)
        
        return activities

    @frappe.whitelist()
    def get_contact_financial_data(self):
        """Get contact financial data"""
        # Get customer financial data
        customer = frappe.get_doc("Customer", self.customer)
        
        financial_data = {
            "open_invoices": frappe.db.sql("""
                SELECT 
                    name,
                    posting_date,
                    grand_total,
                    outstanding_amount,
                    due_date
                FROM `tabSales Invoice`
                WHERE customer = %s
                AND docstatus = 1
                AND outstanding_amount > 0
                ORDER BY posting_date DESC
            """, self.customer, as_dict=True),
            "recent_orders": frappe.db.sql("""
                SELECT 
                    name,
                    posting_date,
                    grand_total,
                    status
                FROM `tabSales Order`
                WHERE customer = %s
                ORDER BY posting_date DESC
                LIMIT 10
            """, self.customer, as_dict=True),
            "payment_history": frappe.db.sql("""
                SELECT 
                    name,
                    posting_date,
                    paid_amount,
                    payment_type
                FROM `tabPayment Entry`
                WHERE party = %s
                AND party_type = 'Customer'
                ORDER BY posting_date DESC
                LIMIT 10
            """, self.customer, as_dict=True)
        }
        
        return financial_data

    @frappe.whitelist()
    def update_contact_priority(self, new_priority):
        """Update contact priority"""
        old_priority = self.contact_priority
        self.contact_priority = new_priority
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "old_priority": old_priority,
            "new_priority": new_priority
        }

    @frappe.whitelist()
    def get_contact_insights(self):
        """Get contact insights"""
        return {
            "contact_priority": self.contact_priority,
            "engagement_level": self.determine_engagement_level(),
            "influence_level": self.determine_influence_level(),
            "communication_preferences": self.analyze_communication_preferences(),
            "next_actions": self.recommend_next_actions(),
            "relationship_stage": self.determine_relationship_stage()
        }
