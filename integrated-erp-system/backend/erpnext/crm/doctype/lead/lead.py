# Enhanced Lead DocType - Complete Lead Management

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class Lead(Document):
    def autoname(self):
        """Generate unique lead code"""
        if not self.lead_code:
            self.lead_code = make_autoname("LEAD-.YYYY.-.MM.-.#####")
        self.name = self.lead_code

    def validate(self):
        """Validate lead data"""
        self.validate_lead_data()
        self.set_defaults()
        self.validate_contact_info()
        self.calculate_lead_score()
        self.determine_lead_quality()

    def before_save(self):
        """Process before saving"""
        self.update_lead_settings()
        self.setup_lead_permissions()
        self.generate_lead_insights()

    def after_insert(self):
        """Process after inserting new lead"""
        self.create_lead_profile()
        self.setup_lead_workflow()
        self.create_lead_analytics()
        self.initialize_lead_tracking()

    def on_update(self):
        """Process on lead update"""
        self.update_lead_analytics()
        self.sync_lead_data()
        self.update_lead_score()
        self.process_lead_changes()

    def validate_lead_data(self):
        """Validate lead information"""
        if not self.lead_name:
            frappe.throw(_("Lead name is required"))
        
        if not self.lead_source:
            frappe.throw(_("Lead source is required"))
        
        if not self.lead_status:
            frappe.throw(_("Lead status is required"))

    def validate_contact_info(self):
        """Validate contact information"""
        if self.email and not self.validate_email():
            frappe.throw(_("Invalid email format"))
        
        if self.mobile_no and not self.validate_mobile():
            frappe.throw(_("Invalid mobile number format"))

    def set_defaults(self):
        """Set default values for new lead"""
        if not self.lead_status:
            self.lead_status = "New"
        
        if not self.lead_source:
            self.lead_source = "Website"
        
        if not self.lead_type:
            self.lead_type = "Individual"
        
        if not self.lead_priority:
            self.lead_priority = "Medium"

    def calculate_lead_score(self):
        """Calculate lead score"""
        score_factors = {
            'contact_completeness': self.get_contact_completeness_score(),
            'company_info': self.get_company_info_score(),
            'engagement_level': self.get_engagement_level_score(),
            'source_quality': self.get_source_quality_score(),
            'timing': self.get_timing_score()
        }
        
        # Calculate weighted lead score
        weights = {
            'contact_completeness': 0.25,
            'company_info': 0.20,
            'engagement_level': 0.25,
            'source_quality': 0.15,
            'timing': 0.15
        }
        
        lead_score = sum(score_factors[factor] * weights[factor] for factor in score_factors)
        
        self.lead_score = round(lead_score, 2)

    def get_contact_completeness_score(self):
        """Get contact completeness score"""
        completeness = 0
        
        if self.email:
            completeness += 0.3
        if self.mobile_no:
            completeness += 0.3
        if self.phone:
            completeness += 0.2
        if self.website:
            completeness += 0.2
        
        return completeness

    def get_company_info_score(self):
        """Get company information score"""
        company_score = 0
        
        if self.company_name:
            company_score += 0.4
        if self.industry:
            company_score += 0.3
        if self.employee_count:
            company_score += 0.3
        
        return company_score

    def get_engagement_level_score(self):
        """Get engagement level score"""
        # Get recent interactions
        interaction_count = frappe.db.sql("""
            SELECT COUNT(*) as interaction_count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Lead'
            AND reference_name = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        if interaction_count >= 10:
            return 1.0
        elif interaction_count >= 5:
            return 0.7
        elif interaction_count >= 2:
            return 0.5
        else:
            return 0.2

    def get_source_quality_score(self):
        """Get source quality score"""
        source_scores = {
            'Website': 0.8,
            'Referral': 0.9,
            'Social Media': 0.6,
            'Email Campaign': 0.7,
            'Cold Call': 0.4,
            'Trade Show': 0.8,
            'Advertisement': 0.5,
            'Other': 0.3
        }
        
        return source_scores.get(self.lead_source, 0.5)

    def get_timing_score(self):
        """Get timing score"""
        # Check if lead is recent
        days_since_creation = (now().date() - self.creation.date()).days
        
        if days_since_creation <= 1:
            return 1.0
        elif days_since_creation <= 7:
            return 0.8
        elif days_since_creation <= 30:
            return 0.6
        else:
            return 0.3

    def determine_lead_quality(self):
        """Determine lead quality"""
        if self.lead_score >= 0.8:
            self.lead_quality = "Hot"
        elif self.lead_score >= 0.6:
            self.lead_quality = "Warm"
        elif self.lead_score >= 0.4:
            self.lead_quality = "Cold"
        else:
            self.lead_quality = "Dead"

    def update_lead_settings(self):
        """Update lead-specific settings"""
        # Update lead preferences
        if self.preferences:
            frappe.db.set_value("Lead", self.name, "preferences", json.dumps(self.preferences))
        
        # Update lead tags
        if self.tags:
            frappe.db.set_value("Lead", self.name, "tags", json.dumps(self.tags))

    def setup_lead_permissions(self):
        """Setup lead-specific permissions"""
        # Create lead-specific roles
        lead_roles = [
            f"Lead - {self.lead_code}",
            f"Lead Source - {self.lead_source}",
            f"Lead Type - {self.lead_type}"
        ]
        
        for role_name in lead_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_lead_insights(self):
        """Generate lead insights"""
        insights = {
            "lead_quality": self.lead_quality,
            "conversion_probability": self.calculate_conversion_probability(),
            "next_actions": self.recommend_next_actions(),
            "follow_up_priority": self.determine_follow_up_priority()
        }
        
        self.lead_insights = json.dumps(insights)

    def calculate_conversion_probability(self):
        """Calculate conversion probability"""
        # Get similar leads conversion rate
        similar_leads = frappe.db.sql("""
            SELECT COUNT(*) as total_leads,
                   SUM(CASE WHEN lead_status = 'Converted' THEN 1 ELSE 0 END) as converted_leads
            FROM `tabLead`
            WHERE lead_source = %s
            AND lead_type = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, (self.lead_source, self.lead_type), as_dict=True)[0]
        
        if similar_leads['total_leads'] > 0:
            conversion_rate = similar_leads['converted_leads'] / similar_leads['total_leads']
            return round(conversion_rate, 2)
        else:
            return 0.5

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.lead_quality == "Hot":
            actions.append("Schedule immediate call")
            actions.append("Send personalized proposal")
        elif self.lead_quality == "Warm":
            actions.append("Send follow-up email")
            actions.append("Schedule demo")
        elif self.lead_quality == "Cold":
            actions.append("Send nurturing content")
            actions.append("Add to email campaign")
        else:
            actions.append("Archive lead")
            actions.append("Remove from active pipeline")
        
        return actions

    def determine_follow_up_priority(self):
        """Determine follow-up priority"""
        if self.lead_quality == "Hot":
            return "High"
        elif self.lead_quality == "Warm":
            return "Medium"
        elif self.lead_quality == "Cold":
            return "Low"
        else:
            return "None"

    def create_lead_profile(self):
        """Create comprehensive lead profile"""
        profile_data = {
            "lead_code": self.lead_code,
            "lead_name": self.lead_name,
            "lead_type": self.lead_type,
            "lead_source": self.lead_source,
            "lead_status": self.lead_status,
            "lead_priority": self.lead_priority,
            "contact_info": {
                "email": self.email,
                "mobile_no": self.mobile_no,
                "phone": self.phone,
                "website": self.website
            },
            "company_info": {
                "company_name": self.company_name,
                "industry": self.industry,
                "employee_count": self.employee_count
            },
            "metrics": {
                "lead_score": self.lead_score,
                "lead_quality": self.lead_quality,
                "conversion_probability": self.calculate_conversion_probability()
            }
        }
        
        frappe.get_doc({
            "doctype": "Lead Profile",
            "lead": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_lead_workflow(self):
        """Setup lead workflow"""
        workflow_data = {
            "lead": self.name,
            "workflow_type": "Lead Management",
            "steps": [
                {"step": "Initial Contact", "status": "Completed"},
                {"step": "Qualification", "status": "Pending"},
                {"step": "Needs Analysis", "status": "Pending"},
                {"step": "Proposal", "status": "Pending"},
                {"step": "Negotiation", "status": "Pending"},
                {"step": "Conversion", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Lead Workflow",
            "lead": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_lead_analytics(self):
        """Create lead analytics"""
        analytics_data = {
            "lead": self.name,
            "analytics_type": "Lead Analytics",
            "metrics": {
                "contact_completeness": self.get_contact_completeness_score(),
                "company_info": self.get_company_info_score(),
                "engagement_level": self.get_engagement_level_score(),
                "source_quality": self.get_source_quality_score(),
                "timing": self.get_timing_score()
            },
            "insights": self.generate_lead_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Lead Analytics",
            "lead": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_lead_tracking(self):
        """Initialize lead tracking"""
        tracking_data = {
            "lead": self.name,
            "lead_score": self.lead_score,
            "lead_quality": self.lead_quality,
            "conversion_probability": self.calculate_conversion_probability(),
            "follow_up_priority": self.determine_follow_up_priority(),
            "last_updated": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Lead Tracking",
            "lead": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_lead_analytics(self):
        """Update lead analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "contact_completeness": self.get_contact_completeness_score(),
            "company_info": self.get_company_info_score(),
            "engagement_level": self.get_engagement_level_score(),
            "source_quality": self.get_source_quality_score(),
            "timing": self.get_timing_score()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Lead Analytics", {"lead": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "lead": self.name,
                "analytics_type": "Lead Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_lead_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_lead_data(self):
        """Sync lead data across systems"""
        # Sync with external CRM systems if configured
        if self.external_crm_id:
            self.sync_with_external_crm()

    def update_lead_score(self):
        """Update lead score"""
        # Recalculate lead score
        self.lead_score = self.calculate_lead_score()
        
        # Update lead quality
        self.lead_quality = self.determine_lead_quality()
        
        # Update tracking record
        tracking = frappe.get_doc("Lead Tracking", {"lead": self.name})
        if tracking:
            tracking.lead_score = self.lead_score
            tracking.lead_quality = self.lead_quality
            tracking.last_updated = now()
            tracking.save()

    def process_lead_changes(self):
        """Process lead changes"""
        # Log lead changes
        self.log_lead_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_lead_changes(self):
        """Log lead changes"""
        frappe.get_doc({
            "doctype": "Lead Change Log",
            "lead": self.name,
            "change_type": "Update",
            "change_description": "Lead information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update opportunity records
        self.update_opportunity_records()
        
        # Update campaign records
        self.update_campaign_records()

    def update_opportunity_records(self):
        """Update opportunity records"""
        # Update opportunity information
        frappe.db.sql("""
            UPDATE `tabOpportunity`
            SET lead_name = %s
            WHERE lead = %s
        """, (self.lead_name, self.name))

    def update_campaign_records(self):
        """Update campaign records"""
        # Update campaign information
        frappe.db.sql("""
            UPDATE `tabCampaign Lead`
            SET lead_name = %s
            WHERE lead = %s
        """, (self.lead_name, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify sales team
        self.notify_sales_team()
        
        # Notify marketing team
        self.notify_marketing_team()

    def notify_sales_team(self):
        """Notify sales team"""
        frappe.get_doc({
            "doctype": "Lead Notification",
            "lead": self.name,
            "notification_type": "Lead Update",
            "message": f"Lead {self.lead_name} information has been updated",
            "recipients": "Sales Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_marketing_team(self):
        """Notify marketing team"""
        frappe.get_doc({
            "doctype": "Lead Notification",
            "lead": self.name,
            "notification_type": "Lead Update",
            "message": f"Lead {self.lead_name} information has been updated",
            "recipients": "Marketing Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def validate_email(self):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.email) is not None

    def validate_mobile(self):
        """Validate mobile number format"""
        import re
        pattern = r'^\+?[\d\s\-\(\)]+$'
        return re.match(pattern, self.mobile_no) is not None

    def sync_with_external_crm(self):
        """Sync lead data with external CRM"""
        # Implementation for external CRM sync
        pass

    @frappe.whitelist()
    def get_lead_dashboard_data(self):
        """Get lead dashboard data"""
        return {
            "lead_code": self.lead_code,
            "lead_name": self.lead_name,
            "lead_source": self.lead_source,
            "lead_status": self.lead_status,
            "lead_quality": self.lead_quality,
            "lead_score": self.lead_score,
            "conversion_probability": self.calculate_conversion_probability(),
            "next_actions": self.recommend_next_actions(),
            "follow_up_priority": self.determine_follow_up_priority()
        }

    @frappe.whitelist()
    def convert_to_customer(self):
        """Convert lead to customer"""
        # Create customer record
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": self.lead_name,
            "customer_type": self.lead_type,
            "email": self.email,
            "mobile_no": self.mobile_no,
            "phone": self.phone,
            "website": self.website,
            "company_name": self.company_name,
            "industry": self.industry,
            "employee_count": self.employee_count,
            "lead_source": self.lead_source
        })
        customer.insert(ignore_permissions=True)
        
        # Update lead status
        self.lead_status = "Converted"
        self.customer = customer.name
        self.save()
        
        return {
            "status": "success",
            "customer": customer.name,
            "message": "Lead converted to customer successfully"
        }

    @frappe.whitelist()
    def qualify_lead(self, qualification_data):
        """Qualify lead with additional data"""
        # Update qualification data
        for field, value in qualification_data.items():
            if hasattr(self, field):
                setattr(self, field, value)
        
        # Recalculate lead score
        self.lead_score = self.calculate_lead_score()
        self.lead_quality = self.determine_lead_quality()
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "lead_score": self.lead_score,
            "lead_quality": self.lead_quality
        }

    @frappe.whitelist()
    def get_lead_insights(self):
        """Get lead insights"""
        return {
            "lead_quality": self.lead_quality,
            "conversion_probability": self.calculate_conversion_probability(),
            "next_actions": self.recommend_next_actions(),
            "follow_up_priority": self.determine_follow_up_priority(),
            "score_factors": {
                "contact_completeness": self.get_contact_completeness_score(),
                "company_info": self.get_company_info_score(),
                "engagement_level": self.get_engagement_level_score(),
                "source_quality": self.get_source_quality_score(),
                "timing": self.get_timing_score()
            }
        }
