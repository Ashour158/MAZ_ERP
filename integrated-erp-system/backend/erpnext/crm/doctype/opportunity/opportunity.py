# Enhanced Opportunity DocType - Complete Sales Pipeline Management

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class Opportunity(Document):
    def autoname(self):
        """Generate unique opportunity ID"""
        if not self.opportunity_id:
            self.opportunity_id = make_autoname("OPP-.YYYY.-.MM.-.#####")
        self.name = self.opportunity_id

    def validate(self):
        """Validate opportunity data"""
        self.validate_opportunity_data()
        self.set_defaults()
        self.validate_customer_data()
        self.validate_contact_data()
        self.calculate_opportunity_metrics()
        self.determine_opportunity_stage()

    def before_save(self):
        """Process before saving"""
        self.update_opportunity_settings()
        self.setup_opportunity_permissions()
        self.generate_opportunity_insights()
        self.calculate_aging()

    def after_insert(self):
        """Process after inserting new opportunity"""
        self.create_opportunity_profile()
        self.setup_opportunity_workflow()
        self.create_opportunity_analytics()
        self.initialize_opportunity_tracking()

    def on_update(self):
        """Process on opportunity update"""
        self.update_opportunity_analytics()
        self.sync_opportunity_data()
        self.update_opportunity_stage()
        self.process_opportunity_changes()

    def validate_opportunity_data(self):
        """Validate opportunity information"""
        if not self.opportunity_name:
            frappe.throw(_("Opportunity name is required"))
        
        if not self.customer:
            frappe.throw(_("Customer is required"))
        
        if not self.opportunity_amount:
            frappe.throw(_("Opportunity amount is required"))
        
        if not self.expected_closing:
            frappe.throw(_("Expected closing date is required"))

    def validate_customer_data(self):
        """Validate customer data"""
        if self.customer and not frappe.db.exists("Customer", self.customer):
            frappe.throw(_("Customer does not exist"))

    def validate_contact_data(self):
        """Validate contact data"""
        if self.contact and not frappe.db.exists("Contact", self.contact):
            frappe.throw(_("Contact does not exist"))

    def set_defaults(self):
        """Set default values for new opportunity"""
        if not self.opportunity_status:
            self.opportunity_status = "Open"
        
        if not self.opportunity_stage:
            self.opportunity_stage = "Prospecting"
        
        if not self.probability:
            self.probability = 10
        
        if not self.priority:
            self.priority = "Medium"
        
        if not self.opportunity_type:
            self.opportunity_type = "New Business"

    def calculate_opportunity_metrics(self):
        """Calculate opportunity metrics"""
        # Calculate weighted amount
        self.weighted_amount = self.opportunity_amount * (self.probability / 100)
        
        # Calculate days to close
        if self.expected_closing:
            days_to_close = (self.expected_closing - now().date()).days
            self.days_to_close = days_to_close
        else:
            self.days_to_close = 0
        
        # Calculate opportunity age
        if self.creation:
            opportunity_age = (now().date() - self.creation.date()).days
            self.opportunity_age = opportunity_age
        else:
            self.opportunity_age = 0

    def determine_opportunity_stage(self):
        """Determine opportunity stage based on probability"""
        if self.probability >= 90:
            self.opportunity_stage = "Closed Won"
        elif self.probability >= 75:
            self.opportunity_stage = "Proposal/Price Quote"
        elif self.probability >= 50:
            self.opportunity_stage = "Negotiation/Review"
        elif self.probability >= 25:
            self.opportunity_stage = "Qualification"
        else:
            self.opportunity_stage = "Prospecting"

    def calculate_aging(self):
        """Calculate opportunity aging"""
        if self.creation:
            aging_days = (now().date() - self.creation.date()).days
            
            if aging_days <= 30:
                self.aging_category = "New"
            elif aging_days <= 60:
                self.aging_category = "Recent"
            elif aging_days <= 90:
                self.aging_category = "Aging"
            else:
                self.aging_category = "Stale"
            
            self.aging_days = aging_days
        else:
            self.aging_category = "New"
            self.aging_days = 0

    def update_opportunity_settings(self):
        """Update opportunity-specific settings"""
        # Update opportunity preferences
        if self.preferences:
            frappe.db.set_value("Opportunity", self.name, "preferences", json.dumps(self.preferences))
        
        # Update opportunity tags
        if self.tags:
            frappe.db.set_value("Opportunity", self.name, "tags", json.dumps(self.tags))

    def setup_opportunity_permissions(self):
        """Setup opportunity-specific permissions"""
        # Create opportunity-specific roles
        opportunity_roles = [
            f"Opportunity - {self.opportunity_id}",
            f"Customer - {self.customer}",
            f"Stage - {self.opportunity_stage}"
        ]
        
        for role_name in opportunity_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_opportunity_insights(self):
        """Generate opportunity insights"""
        insights = {
            "stage_analysis": self.analyze_stage(),
            "probability_analysis": self.analyze_probability(),
            "aging_analysis": self.analyze_aging(),
            "next_actions": self.recommend_next_actions(),
            "ai_recommendations": self.get_ai_recommendations(),
            "manager_recommendations": self.get_manager_recommendations()
        }
        
        self.opportunity_insights = json.dumps(insights)

    def analyze_stage(self):
        """Analyze opportunity stage"""
        stage_analysis = {
            "current_stage": self.opportunity_stage,
            "stage_duration": self.calculate_stage_duration(),
            "stage_progress": self.calculate_stage_progress(),
            "stage_risk": self.assess_stage_risk()
        }
        
        return stage_analysis

    def calculate_stage_duration(self):
        """Calculate duration in current stage"""
        # Get stage change history
        stage_changes = frappe.db.sql("""
            SELECT creation
            FROM `tabOpportunity Stage Change`
            WHERE opportunity = %s
            AND new_stage = %s
            ORDER BY creation DESC
            LIMIT 1
        """, (self.name, self.opportunity_stage))[0][0] if frappe.db.exists("Opportunity Stage Change", {"opportunity": self.name, "new_stage": self.opportunity_stage}) else self.creation
        
        if stage_changes:
            duration = (now().date() - stage_changes.date()).days
            return duration
        else:
            return 0

    def calculate_stage_progress(self):
        """Calculate progress within current stage"""
        stage_progress = {
            "Prospecting": 0.1,
            "Qualification": 0.3,
            "Negotiation/Review": 0.6,
            "Proposal/Price Quote": 0.8,
            "Closed Won": 1.0,
            "Closed Lost": 0.0
        }
        
        return stage_progress.get(self.opportunity_stage, 0.5)

    def assess_stage_risk(self):
        """Assess risk in current stage"""
        if self.opportunity_stage == "Prospecting" and self.aging_days > 30:
            return "High Risk - Stale in prospecting"
        elif self.opportunity_stage == "Qualification" and self.aging_days > 45:
            return "Medium Risk - Long qualification period"
        elif self.opportunity_stage == "Negotiation/Review" and self.aging_days > 60:
            return "High Risk - Extended negotiation"
        else:
            return "Low Risk"

    def analyze_probability(self):
        """Analyze opportunity probability"""
        probability_analysis = {
            "current_probability": self.probability,
            "probability_trend": self.calculate_probability_trend(),
            "probability_risk": self.assess_probability_risk(),
            "probability_recommendations": self.get_probability_recommendations()
        }
        
        return probability_analysis

    def calculate_probability_trend(self):
        """Calculate probability trend"""
        # Get probability history
        probability_history = frappe.db.sql("""
            SELECT probability, creation
            FROM `tabOpportunity Probability Change`
            WHERE opportunity = %s
            ORDER BY creation DESC
            LIMIT 5
        """, self.name, as_dict=True)
        
        if len(probability_history) >= 2:
            recent_probability = probability_history[0]['probability']
            previous_probability = probability_history[1]['probability']
            
            if recent_probability > previous_probability:
                return "Increasing"
            elif recent_probability < previous_probability:
                return "Decreasing"
            else:
                return "Stable"
        else:
            return "New"

    def assess_probability_risk(self):
        """Assess probability risk"""
        if self.probability < 25:
            return "High Risk - Low probability"
        elif self.probability < 50:
            return "Medium Risk - Moderate probability"
        else:
            return "Low Risk - Good probability"

    def get_probability_recommendations(self):
        """Get probability recommendations"""
        recommendations = []
        
        if self.probability < 25:
            recommendations.append("Focus on qualification and needs analysis")
            recommendations.append("Schedule discovery calls")
            recommendations.append("Identify decision makers")
        elif self.probability < 50:
            recommendations.append("Move to proposal stage")
            recommendations.append("Address objections")
            recommendations.append("Build relationship with stakeholders")
        else:
            recommendations.append("Focus on closing activities")
            recommendations.append("Address final objections")
            recommendations.append("Prepare for contract negotiation")
        
        return recommendations

    def analyze_aging(self):
        """Analyze opportunity aging"""
        aging_analysis = {
            "aging_days": self.aging_days,
            "aging_category": self.aging_category,
            "aging_risk": self.assess_aging_risk(),
            "aging_recommendations": self.get_aging_recommendations()
        }
        
        return aging_analysis

    def assess_aging_risk(self):
        """Assess aging risk"""
        if self.aging_days > 90:
            return "High Risk - Stale opportunity"
        elif self.aging_days > 60:
            return "Medium Risk - Aging opportunity"
        else:
            return "Low Risk - Recent opportunity"

    def get_aging_recommendations(self):
        """Get aging recommendations"""
        recommendations = []
        
        if self.aging_days > 90:
            recommendations.append("Review opportunity viability")
            recommendations.append("Schedule urgent follow-up")
            recommendations.append("Consider closing as lost")
        elif self.aging_days > 60:
            recommendations.append("Increase engagement frequency")
            recommendations.append("Schedule progress review")
            recommendations.append("Identify blockers")
        else:
            recommendations.append("Continue regular follow-up")
            recommendations.append("Monitor progress")
            recommendations.append("Maintain engagement")
        
        return recommendations

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.opportunity_stage == "Prospecting":
            actions.append("Schedule initial discovery call")
            actions.append("Research customer needs")
            actions.append("Identify key stakeholders")
        elif self.opportunity_stage == "Qualification":
            actions.append("Conduct needs analysis")
            actions.append("Identify decision makers")
            actions.append("Assess budget and timeline")
        elif self.opportunity_stage == "Negotiation/Review":
            actions.append("Address objections")
            actions.append("Prepare proposal")
            actions.append("Schedule decision meeting")
        elif self.opportunity_stage == "Proposal/Price Quote":
            actions.append("Follow up on proposal")
            actions.append("Address final objections")
            actions.append("Prepare contract")
        else:
            actions.append("Monitor progress")
            actions.append("Maintain relationship")
            actions.append("Look for upsell opportunities")
        
        return actions

    def get_ai_recommendations(self):
        """Get AI recommendations"""
        ai_recommendations = []
        
        # Analyze customer behavior
        customer_behavior = self.analyze_customer_behavior()
        if customer_behavior['engagement_level'] < 0.5:
            ai_recommendations.append("Increase customer engagement")
            ai_recommendations.append("Schedule relationship building activities")
        
        # Analyze opportunity patterns
        opportunity_patterns = self.analyze_opportunity_patterns()
        if opportunity_patterns['similar_opportunities']:
            ai_recommendations.append("Review similar successful opportunities")
            ai_recommendations.append("Apply successful strategies")
        
        # Analyze timing
        timing_analysis = self.analyze_timing()
        if timing_analysis['optimal_timing']:
            ai_recommendations.append("Leverage optimal timing for closing")
            ai_recommendations.append("Schedule key activities during peak times")
        
        return ai_recommendations

    def get_manager_recommendations(self):
        """Get manager recommendations"""
        manager_recommendations = []
        
        # Get manager insights
        manager_insights = self.get_manager_insights()
        
        if manager_insights['team_performance']:
            manager_recommendations.append("Review team performance on similar opportunities")
            manager_recommendations.append("Apply best practices from top performers")
        
        if manager_insights['market_conditions']:
            manager_recommendations.append("Consider current market conditions")
            manager_recommendations.append("Adjust strategy based on market trends")
        
        if manager_insights['competitive_landscape']:
            manager_recommendations.append("Analyze competitive positioning")
            manager_recommendations.append("Develop competitive advantages")
        
        return manager_recommendations

    def analyze_customer_behavior(self):
        """Analyze customer behavior"""
        # Get customer engagement data
        engagement_data = frappe.db.sql("""
            SELECT COUNT(*) as interaction_count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Customer'
            AND reference_name = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.customer)[0][0]
        
        engagement_level = min(engagement_data / 10, 1.0)  # Normalize to 0-1
        
        return {
            "engagement_level": engagement_level,
            "interaction_count": engagement_data
        }

    def analyze_opportunity_patterns(self):
        """Analyze opportunity patterns"""
        # Get similar opportunities
        similar_opportunities = frappe.db.sql("""
            SELECT COUNT(*) as similar_count
            FROM `tabOpportunity`
            WHERE customer = %s
            AND opportunity_type = %s
            AND opportunity_amount BETWEEN %s AND %s
        """, (self.customer, self.opportunity_type, self.opportunity_amount * 0.8, self.opportunity_amount * 1.2))[0][0]
        
        return {
            "similar_opportunities": similar_opportunities > 0,
            "similar_count": similar_opportunities
        }

    def analyze_timing(self):
        """Analyze timing"""
        # Get optimal timing data
        optimal_timing = frappe.db.sql("""
            SELECT COUNT(*) as optimal_count
            FROM `tabOpportunity`
            WHERE customer = %s
            AND MONTH(expected_closing) = MONTH(%s)
            AND YEAR(expected_closing) = YEAR(%s)
        """, (self.customer, self.expected_closing, self.expected_closing))[0][0]
        
        return {
            "optimal_timing": optimal_timing > 0,
            "timing_count": optimal_timing
        }

    def get_manager_insights(self):
        """Get manager insights"""
        return {
            "team_performance": True,
            "market_conditions": True,
            "competitive_landscape": True
        }

    def create_opportunity_profile(self):
        """Create comprehensive opportunity profile"""
        profile_data = {
            "opportunity_id": self.opportunity_id,
            "opportunity_name": self.opportunity_name,
            "customer": self.customer,
            "contact": self.contact,
            "opportunity_amount": self.opportunity_amount,
            "probability": self.probability,
            "weighted_amount": self.weighted_amount,
            "opportunity_stage": self.opportunity_stage,
            "opportunity_status": self.opportunity_status,
            "expected_closing": self.expected_closing,
            "opportunity_type": self.opportunity_type,
            "priority": self.priority,
            "aging_days": self.aging_days,
            "aging_category": self.aging_category
        }
        
        frappe.get_doc({
            "doctype": "Opportunity Profile",
            "opportunity": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_opportunity_workflow(self):
        """Setup opportunity workflow"""
        workflow_data = {
            "opportunity": self.name,
            "workflow_type": "Opportunity Management",
            "steps": [
                {"step": "Initial Contact", "status": "Completed"},
                {"step": "Qualification", "status": "Pending"},
                {"step": "Needs Analysis", "status": "Pending"},
                {"step": "Proposal", "status": "Pending"},
                {"step": "Negotiation", "status": "Pending"},
                {"step": "Closing", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Opportunity Workflow",
            "opportunity": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_opportunity_analytics(self):
        """Create opportunity analytics"""
        analytics_data = {
            "opportunity": self.name,
            "analytics_type": "Opportunity Analytics",
            "metrics": {
                "opportunity_amount": self.opportunity_amount,
                "probability": self.probability,
                "weighted_amount": self.weighted_amount,
                "aging_days": self.aging_days,
                "days_to_close": self.days_to_close
            },
            "insights": self.generate_opportunity_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Opportunity Analytics",
            "opportunity": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_opportunity_tracking(self):
        """Initialize opportunity tracking"""
        tracking_data = {
            "opportunity": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "stage_changes": 0,
            "probability_changes": 0
        }
        
        frappe.get_doc({
            "doctype": "Opportunity Tracking",
            "opportunity": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_opportunity_analytics(self):
        """Update opportunity analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "opportunity_amount": self.opportunity_amount,
            "probability": self.probability,
            "weighted_amount": self.weighted_amount,
            "aging_days": self.aging_days,
            "days_to_close": self.days_to_close
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Opportunity Analytics", {"opportunity": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "opportunity": self.name,
                "analytics_type": "Opportunity Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_opportunity_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_opportunity_data(self):
        """Sync opportunity data across systems"""
        # Sync with external CRM systems if configured
        if self.external_crm_id:
            self.sync_with_external_crm()

    def update_opportunity_stage(self):
        """Update opportunity stage"""
        # Log stage change
        self.log_stage_change()
        
        # Update tracking
        tracking = frappe.get_doc("Opportunity Tracking", {"opportunity": self.name})
        if tracking:
            tracking.stage_changes += 1
            tracking.last_activity = now()
            tracking.save()

    def process_opportunity_changes(self):
        """Process opportunity changes"""
        # Log opportunity changes
        self.log_opportunity_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_stage_change(self):
        """Log stage change"""
        frappe.get_doc({
            "doctype": "Opportunity Stage Change",
            "opportunity": self.name,
            "old_stage": self.get_previous_stage(),
            "new_stage": self.opportunity_stage,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_stage(self):
        """Get previous stage"""
        previous_stage = frappe.db.sql("""
            SELECT new_stage
            FROM `tabOpportunity Stage Change`
            WHERE opportunity = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Opportunity Stage Change", {"opportunity": self.name}) else "New"
        
        return previous_stage

    def log_opportunity_changes(self):
        """Log opportunity changes"""
        frappe.get_doc({
            "doctype": "Opportunity Change Log",
            "opportunity": self.name,
            "change_type": "Update",
            "change_description": "Opportunity information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update customer records
        self.update_customer_records()
        
        # Update contact records
        self.update_contact_records()

    def update_customer_records(self):
        """Update customer records"""
        # Update customer opportunity count
        frappe.db.sql("""
            UPDATE `tabCustomer`
            SET opportunity_count = (
                SELECT COUNT(*) FROM `tabOpportunity`
                WHERE customer = %s AND status = 'Open'
            )
            WHERE name = %s
        """, (self.customer, self.customer))

    def update_contact_records(self):
        """Update contact records"""
        # Update contact opportunity count
        if self.contact:
            frappe.db.sql("""
                UPDATE `tabContact`
                SET opportunity_count = (
                    SELECT COUNT(*) FROM `tabOpportunity`
                    WHERE contact = %s AND status = 'Open'
                )
                WHERE name = %s
            """, (self.contact, self.contact))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify sales team
        self.notify_sales_team()
        
        # Notify account owner
        self.notify_account_owner()

    def notify_sales_team(self):
        """Notify sales team"""
        frappe.get_doc({
            "doctype": "Opportunity Notification",
            "opportunity": self.name,
            "notification_type": "Opportunity Update",
            "message": f"Opportunity {self.opportunity_name} has been updated",
            "recipients": "Sales Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_account_owner(self):
        """Notify account owner"""
        if self.account_owner:
            frappe.get_doc({
                "doctype": "Opportunity Notification",
                "opportunity": self.name,
                "notification_type": "Opportunity Update",
                "message": f"Opportunity {self.opportunity_name} has been updated",
                "recipients": self.account_owner,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_crm(self):
        """Sync opportunity data with external CRM"""
        # Implementation for external CRM sync
        pass

    @frappe.whitelist()
    def get_opportunity_dashboard_data(self):
        """Get opportunity dashboard data"""
        return {
            "opportunity_id": self.opportunity_id,
            "opportunity_name": self.opportunity_name,
            "customer": self.customer,
            "contact": self.contact,
            "opportunity_amount": self.opportunity_amount,
            "probability": self.probability,
            "weighted_amount": self.weighted_amount,
            "opportunity_stage": self.opportunity_stage,
            "opportunity_status": self.opportunity_status,
            "expected_closing": self.expected_closing,
            "aging_days": self.aging_days,
            "aging_category": self.aging_category,
            "days_to_close": self.days_to_close,
            "insights": self.generate_opportunity_insights()
        }

    @frappe.whitelist()
    def update_opportunity_stage(self, new_stage, probability=None):
        """Update opportunity stage"""
        old_stage = self.opportunity_stage
        self.opportunity_stage = new_stage
        
        if probability:
            self.probability = probability
        
        # Log stage change
        self.log_stage_change()
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "old_stage": old_stage,
            "new_stage": new_stage,
            "probability": self.probability
        }

    @frappe.whitelist()
    def update_probability(self, new_probability):
        """Update opportunity probability"""
        old_probability = self.probability
        self.probability = new_probability
        
        # Recalculate weighted amount
        self.weighted_amount = self.opportunity_amount * (self.probability / 100)
        
        # Log probability change
        frappe.get_doc({
            "doctype": "Opportunity Probability Change",
            "opportunity": self.name,
            "old_probability": old_probability,
            "new_probability": new_probability,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "old_probability": old_probability,
            "new_probability": new_probability,
            "weighted_amount": self.weighted_amount
        }

    @frappe.whitelist()
    def get_opportunity_insights(self):
        """Get opportunity insights"""
        return {
            "stage_analysis": self.analyze_stage(),
            "probability_analysis": self.analyze_probability(),
            "aging_analysis": self.analyze_aging(),
            "next_actions": self.recommend_next_actions(),
            "ai_recommendations": self.get_ai_recommendations(),
            "manager_recommendations": self.get_manager_recommendations()
        }
