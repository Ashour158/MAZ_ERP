# Enhanced Customer DocType - Complete Customer Management

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class Customer(Document):
    def autoname(self):
        """Generate unique customer code"""
        if not self.customer_code:
            self.customer_code = make_autoname("CUST-.YYYY.-.MM.-.#####")
        self.name = self.customer_code

    def validate(self):
        """Validate customer data"""
        self.validate_customer_data()
        self.set_defaults()
        self.validate_contact_info()
        self.validate_business_info()
        self.calculate_customer_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_customer_settings()
        self.setup_customer_permissions()
        self.generate_customer_insights()

    def after_insert(self):
        """Process after inserting new customer"""
        self.create_customer_profile()
        self.setup_customer_workflow()
        self.create_customer_analytics()
        self.initialize_customer_health()

    def on_update(self):
        """Process on customer update"""
        self.update_customer_analytics()
        self.sync_customer_data()
        self.update_customer_health()
        self.process_customer_changes()

    def validate_customer_data(self):
        """Validate customer information"""
        if not self.customer_name:
            frappe.throw(_("Customer name is required"))
        
        if not self.customer_type:
            frappe.throw(_("Customer type is required"))
        
        if not self.customer_group:
            frappe.throw(_("Customer group is required"))

    def validate_contact_info(self):
        """Validate contact information"""
        if self.email and not self.validate_email():
            frappe.throw(_("Invalid email format"))
        
        if self.mobile_no and not self.validate_mobile():
            frappe.throw(_("Invalid mobile number format"))

    def validate_business_info(self):
        """Validate business information"""
        if self.tax_id and len(self.tax_id) < 5:
            frappe.throw(_("Tax ID must be at least 5 characters"))
        
        if self.website and not self.validate_website():
            frappe.throw(_("Invalid website format"))

    def set_defaults(self):
        """Set default values for new customer"""
        if not self.customer_type:
            self.customer_type = "Individual"
        
        if not self.customer_group:
            self.customer_group = "All Customer Groups"
        
        if not self.territory:
            self.territory = "All Territories"
        
        if not self.customer_status:
            self.customer_status = "Active"
        
        if not self.customer_tier:
            self.customer_tier = "Standard"

    def calculate_customer_metrics(self):
        """Calculate customer metrics"""
        # Calculate customer lifetime value
        self.customer_lifetime_value = self.calculate_lifetime_value()
        
        # Calculate customer health score
        self.customer_health_score = self.calculate_health_score()
        
        # Calculate customer engagement score
        self.customer_engagement_score = self.calculate_engagement_score()
        
        # Calculate customer satisfaction score
        self.customer_satisfaction_score = self.calculate_satisfaction_score()

    def calculate_lifetime_value(self):
        """Calculate customer lifetime value"""
        # Get total sales
        total_sales = frappe.db.sql("""
            SELECT SUM(grand_total)
            FROM `tabSales Invoice`
            WHERE customer = %s
            AND docstatus = 1
        """, self.name)[0][0] or 0
        
        # Get total costs
        total_costs = frappe.db.sql("""
            SELECT SUM(grand_total)
            FROM `tabPurchase Invoice`
            WHERE customer = %s
            AND docstatus = 1
        """, self.name)[0][0] or 0
        
        # Calculate lifetime value
        lifetime_value = total_sales - total_costs
        
        return lifetime_value

    def calculate_health_score(self):
        """Calculate customer health score"""
        health_factors = {
            'revenue_trend': self.get_revenue_trend_score(),
            'payment_behavior': self.get_payment_behavior_score(),
            'engagement_level': self.get_engagement_level_score(),
            'satisfaction_rating': self.get_satisfaction_rating_score(),
            'support_tickets': self.get_support_tickets_score()
        }
        
        # Calculate weighted health score
        weights = {
            'revenue_trend': 0.25,
            'payment_behavior': 0.20,
            'engagement_level': 0.20,
            'satisfaction_rating': 0.20,
            'support_tickets': 0.15
        }
        
        health_score = sum(health_factors[factor] * weights[factor] for factor in health_factors)
        
        return round(health_score, 2)

    def calculate_engagement_score(self):
        """Calculate customer engagement score"""
        # Get recent activity
        recent_activity = self.get_recent_activity_score()
        
        # Get communication frequency
        communication_frequency = self.get_communication_frequency_score()
        
        # Get feature usage
        feature_usage = self.get_feature_usage_score()
        
        # Calculate engagement score
        engagement_score = (recent_activity * 0.4 + 
                           communication_frequency * 0.3 + 
                           feature_usage * 0.3)
        
        return round(engagement_score, 2)

    def calculate_satisfaction_score(self):
        """Calculate customer satisfaction score"""
        # Get feedback scores
        feedback_scores = self.get_feedback_scores()
        
        # Get support ticket satisfaction
        support_satisfaction = self.get_support_satisfaction_score()
        
        # Get product/service ratings
        product_ratings = self.get_product_ratings()
        
        # Calculate satisfaction score
        satisfaction_score = (feedback_scores * 0.4 + 
                            support_satisfaction * 0.3 + 
                            product_ratings * 0.3)
        
        return round(satisfaction_score, 2)

    def get_revenue_trend_score(self):
        """Get revenue trend score"""
        # Get revenue data for last 6 months
        revenue_data = frappe.db.sql("""
            SELECT MONTH(posting_date) as month, SUM(grand_total) as revenue
            FROM `tabSales Invoice`
            WHERE customer = %s
            AND docstatus = 1
            AND posting_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY MONTH(posting_date)
            ORDER BY month
        """, self.name, as_dict=True)
        
        if len(revenue_data) < 2:
            return 0.5
        
        # Calculate trend
        recent_revenue = revenue_data[-1]['revenue']
        previous_revenue = revenue_data[-2]['revenue']
        
        if previous_revenue > 0:
            trend = (recent_revenue - previous_revenue) / previous_revenue
            if trend > 0.1:
                return 1.0
            elif trend > 0:
                return 0.7
            elif trend > -0.1:
                return 0.5
            else:
                return 0.2
        else:
            return 0.5

    def get_payment_behavior_score(self):
        """Get payment behavior score"""
        # Get payment history
        payment_data = frappe.db.sql("""
            SELECT AVG(DATEDIFF(outstanding_amount_date, posting_date)) as avg_payment_days
            FROM `tabSales Invoice`
            WHERE customer = %s
            AND docstatus = 1
            AND outstanding_amount = 0
        """, self.name)[0][0]
        
        if payment_data:
            if payment_data <= 30:
                return 1.0
            elif payment_data <= 45:
                return 0.8
            elif payment_data <= 60:
                return 0.6
            else:
                return 0.3
        else:
            return 0.5

    def get_engagement_level_score(self):
        """Get engagement level score"""
        # Get recent interactions
        recent_interactions = frappe.db.sql("""
            SELECT COUNT(*) as interaction_count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Customer'
            AND reference_name = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        if recent_interactions >= 10:
            return 1.0
        elif recent_interactions >= 5:
            return 0.7
        elif recent_interactions >= 2:
            return 0.5
        else:
            return 0.2

    def get_satisfaction_rating_score(self):
        """Get satisfaction rating score"""
        # Get customer feedback
        feedback_data = frappe.db.sql("""
            SELECT AVG(rating) as avg_rating
            FROM `tabCustomer Feedback`
            WHERE customer = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, self.name)[0][0]
        
        if feedback_data:
            return feedback_data / 5.0
        else:
            return 0.5

    def get_support_tickets_score(self):
        """Get support tickets score"""
        # Get support ticket data
        ticket_data = frappe.db.sql("""
            SELECT COUNT(*) as ticket_count,
                   AVG(DATEDIFF(resolution_date, creation)) as avg_resolution_days
            FROM `tabIssue`
            WHERE customer = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, self.name, as_dict=True)[0]
        
        if ticket_data['ticket_count'] == 0:
            return 1.0
        elif ticket_data['avg_resolution_days'] <= 2:
            return 0.8
        elif ticket_data['avg_resolution_days'] <= 5:
            return 0.6
        else:
            return 0.3

    def get_recent_activity_score(self):
        """Get recent activity score"""
        # Get recent activity count
        activity_count = frappe.db.sql("""
            SELECT COUNT(*) as activity_count
            FROM `tabCustomer Activity`
            WHERE customer = %s
            AND activity_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        if activity_count >= 20:
            return 1.0
        elif activity_count >= 10:
            return 0.7
        elif activity_count >= 5:
            return 0.5
        else:
            return 0.2

    def get_communication_frequency_score(self):
        """Get communication frequency score"""
        # Get communication frequency
        communication_count = frappe.db.sql("""
            SELECT COUNT(*) as communication_count
            FROM `tabCommunication`
            WHERE reference_doctype = 'Customer'
            AND reference_name = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        if communication_count >= 15:
            return 1.0
        elif communication_count >= 8:
            return 0.7
        elif communication_count >= 4:
            return 0.5
        else:
            return 0.2

    def get_feature_usage_score(self):
        """Get feature usage score"""
        # Get feature usage data
        feature_usage = frappe.db.sql("""
            SELECT COUNT(DISTINCT feature_name) as unique_features
            FROM `tabCustomer Feature Usage`
            WHERE customer = %s
            AND usage_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        if feature_usage >= 5:
            return 1.0
        elif feature_usage >= 3:
            return 0.7
        elif feature_usage >= 1:
            return 0.5
        else:
            return 0.2

    def get_feedback_scores(self):
        """Get feedback scores"""
        # Get average feedback score
        avg_feedback = frappe.db.sql("""
            SELECT AVG(rating) as avg_rating
            FROM `tabCustomer Feedback`
            WHERE customer = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, self.name)[0][0]
        
        if avg_feedback:
            return avg_feedback / 5.0
        else:
            return 0.5

    def get_support_satisfaction_score(self):
        """Get support satisfaction score"""
        # Get support satisfaction
        support_satisfaction = frappe.db.sql("""
            SELECT AVG(satisfaction_rating) as avg_satisfaction
            FROM `tabSupport Ticket`
            WHERE customer = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, self.name)[0][0]
        
        if support_satisfaction:
            return support_satisfaction / 5.0
        else:
            return 0.5

    def get_product_ratings(self):
        """Get product ratings"""
        # Get product ratings
        product_ratings = frappe.db.sql("""
            SELECT AVG(rating) as avg_rating
            FROM `tabProduct Review`
            WHERE customer = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, self.name)[0][0]
        
        if product_ratings:
            return product_ratings / 5.0
        else:
            return 0.5

    def update_customer_settings(self):
        """Update customer-specific settings"""
        # Update customer preferences
        if self.preferences:
            frappe.db.set_value("Customer", self.name, "preferences", json.dumps(self.preferences))
        
        # Update customer tags
        if self.tags:
            frappe.db.set_value("Customer", self.name, "tags", json.dumps(self.tags))

    def setup_customer_permissions(self):
        """Setup customer-specific permissions"""
        # Create customer-specific roles
        customer_roles = [
            f"Customer - {self.customer_code}",
            f"Customer Group - {self.customer_group}",
            f"Territory - {self.territory}"
        ]
        
        for role_name in customer_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_customer_insights(self):
        """Generate customer insights"""
        insights = {
            "customer_segment": self.determine_customer_segment(),
            "churn_risk": self.calculate_churn_risk(),
            "upsell_opportunities": self.identify_upsell_opportunities(),
            "retention_strategy": self.recommend_retention_strategy()
        }
        
        self.customer_insights = json.dumps(insights)

    def determine_customer_segment(self):
        """Determine customer segment"""
        if self.customer_lifetime_value > 100000:
            return "High Value"
        elif self.customer_lifetime_value > 50000:
            return "Medium Value"
        else:
            return "Standard"

    def calculate_churn_risk(self):
        """Calculate churn risk"""
        risk_factors = {
            'health_score': self.customer_health_score,
            'engagement_score': self.customer_engagement_score,
            'satisfaction_score': self.customer_satisfaction_score,
            'recent_activity': self.get_recent_activity_score(),
            'payment_behavior': self.get_payment_behavior_score()
        }
        
        # Calculate weighted risk score
        weights = {
            'health_score': 0.3,
            'engagement_score': 0.25,
            'satisfaction_score': 0.25,
            'recent_activity': 0.1,
            'payment_behavior': 0.1
        }
        
        risk_score = sum(risk_factors[factor] * weights[factor] for factor in risk_factors)
        
        if risk_score < 0.3:
            return "High Risk"
        elif risk_score < 0.6:
            return "Medium Risk"
        else:
            return "Low Risk"

    def identify_upsell_opportunities(self):
        """Identify upsell opportunities"""
        opportunities = []
        
        # Check for product upgrades
        if self.customer_tier == "Standard":
            opportunities.append("Upgrade to Premium tier")
        
        # Check for additional services
        if not self.has_premium_support:
            opportunities.append("Add premium support")
        
        # Check for additional features
        if not self.has_advanced_features:
            opportunities.append("Add advanced features")
        
        return opportunities

    def recommend_retention_strategy(self):
        """Recommend retention strategy"""
        if self.calculate_churn_risk() == "High Risk":
            return "Implement immediate retention campaign"
        elif self.calculate_churn_risk() == "Medium Risk":
            return "Schedule customer success call"
        else:
            return "Continue current engagement strategy"

    def create_customer_profile(self):
        """Create comprehensive customer profile"""
        profile_data = {
            "customer_code": self.customer_code,
            "customer_name": self.customer_name,
            "customer_type": self.customer_type,
            "customer_group": self.customer_group,
            "territory": self.territory,
            "customer_tier": self.customer_tier,
            "contact_info": {
                "email": self.email,
                "mobile_no": self.mobile_no,
                "phone": self.phone,
                "website": self.website
            },
            "business_info": {
                "tax_id": self.tax_id,
                "industry": self.industry,
                "customer_status": self.customer_status
            },
            "metrics": {
                "lifetime_value": self.customer_lifetime_value,
                "health_score": self.customer_health_score,
                "engagement_score": self.customer_engagement_score,
                "satisfaction_score": self.customer_satisfaction_score
            }
        }
        
        frappe.get_doc({
            "doctype": "Customer Profile",
            "customer": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_customer_workflow(self):
        """Setup customer workflow"""
        workflow_data = {
            "customer": self.name,
            "workflow_type": "Customer Onboarding",
            "steps": [
                {"step": "Initial Contact", "status": "Completed"},
                {"step": "Qualification", "status": "Pending"},
                {"step": "Proposal", "status": "Pending"},
                {"step": "Negotiation", "status": "Pending"},
                {"step": "Contract", "status": "Pending"},
                {"step": "Implementation", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Customer Workflow",
            "customer": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_customer_analytics(self):
        """Create customer analytics"""
        analytics_data = {
            "customer": self.name,
            "analytics_type": "Customer Analytics",
            "metrics": {
                "revenue_trend": self.get_revenue_trend_score(),
                "payment_behavior": self.get_payment_behavior_score(),
                "engagement_level": self.get_engagement_level_score(),
                "satisfaction_rating": self.get_satisfaction_rating_score(),
                "support_tickets": self.get_support_tickets_score()
            },
            "insights": self.generate_customer_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Customer Analytics",
            "customer": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_customer_health(self):
        """Initialize customer health tracking"""
        health_data = {
            "customer": self.name,
            "health_score": self.customer_health_score,
            "health_factors": {
                "revenue_trend": self.get_revenue_trend_score(),
                "payment_behavior": self.get_payment_behavior_score(),
                "engagement_level": self.get_engagement_level_score(),
                "satisfaction_rating": self.get_satisfaction_rating_score(),
                "support_tickets": self.get_support_tickets_score()
            },
            "health_status": self.determine_health_status(),
            "last_updated": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Customer Health",
            "customer": self.name,
            "health_data": json.dumps(health_data)
        }).insert(ignore_permissions=True)

    def determine_health_status(self):
        """Determine customer health status"""
        if self.customer_health_score >= 0.8:
            return "Excellent"
        elif self.customer_health_score >= 0.6:
            return "Good"
        elif self.customer_health_score >= 0.4:
            return "Fair"
        else:
            return "Poor"

    def update_customer_analytics(self):
        """Update customer analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "revenue_trend": self.get_revenue_trend_score(),
            "payment_behavior": self.get_payment_behavior_score(),
            "engagement_level": self.get_engagement_level_score(),
            "satisfaction_rating": self.get_satisfaction_rating_score(),
            "support_tickets": self.get_support_tickets_score()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Customer Analytics", {"customer": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "customer": self.name,
                "analytics_type": "Customer Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_customer_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_customer_data(self):
        """Sync customer data across systems"""
        # Sync with external CRM systems if configured
        if self.external_crm_id:
            self.sync_with_external_crm()

    def update_customer_health(self):
        """Update customer health"""
        # Update health record
        health = frappe.get_doc("Customer Health", {"customer": self.name})
        if health:
            health.health_score = self.customer_health_score
            health.health_status = self.determine_health_status()
            health.last_updated = now()
            health.save()

    def process_customer_changes(self):
        """Process customer changes"""
        # Log customer changes
        self.log_customer_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_customer_changes(self):
        """Log customer changes"""
        frappe.get_doc({
            "doctype": "Customer Change Log",
            "customer": self.name,
            "change_type": "Update",
            "change_description": "Customer information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update contact records
        self.update_contact_records()
        
        # Update address records
        self.update_address_records()
        
        # Update opportunity records
        self.update_opportunity_records()

    def update_contact_records(self):
        """Update contact records"""
        # Update contact information
        frappe.db.sql("""
            UPDATE `tabContact`
            SET customer_name = %s
            WHERE customer = %s
        """, (self.customer_name, self.name))

    def update_address_records(self):
        """Update address records"""
        # Update address information
        frappe.db.sql("""
            UPDATE `tabAddress`
            SET customer_name = %s
            WHERE customer = %s
        """, (self.customer_name, self.name))

    def update_opportunity_records(self):
        """Update opportunity records"""
        # Update opportunity information
        frappe.db.sql("""
            UPDATE `tabOpportunity`
            SET customer_name = %s
            WHERE customer = %s
        """, (self.customer_name, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify sales team
        self.notify_sales_team()
        
        # Notify customer success team
        self.notify_customer_success_team()
        
        # Notify marketing team
        self.notify_marketing_team()

    def notify_sales_team(self):
        """Notify sales team"""
        frappe.get_doc({
            "doctype": "Customer Notification",
            "customer": self.name,
            "notification_type": "Customer Update",
            "message": f"Customer {self.customer_name} information has been updated",
            "recipients": "Sales Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_customer_success_team(self):
        """Notify customer success team"""
        frappe.get_doc({
            "doctype": "Customer Notification",
            "customer": self.name,
            "notification_type": "Customer Update",
            "message": f"Customer {self.customer_name} information has been updated",
            "recipients": "Customer Success Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_marketing_team(self):
        """Notify marketing team"""
        frappe.get_doc({
            "doctype": "Customer Notification",
            "customer": self.name,
            "notification_type": "Customer Update",
            "message": f"Customer {self.customer_name} information has been updated",
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

    def validate_website(self):
        """Validate website format"""
        import re
        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.website) is not None

    def sync_with_external_crm(self):
        """Sync customer data with external CRM"""
        # Implementation for external CRM sync
        pass

    @frappe.whitelist()
    def get_customer_dashboard_data(self):
        """Get customer dashboard data"""
        return {
            "customer_code": self.customer_code,
            "customer_name": self.customer_name,
            "customer_tier": self.customer_tier,
            "health_score": self.customer_health_score,
            "engagement_score": self.customer_engagement_score,
            "satisfaction_score": self.customer_satisfaction_score,
            "lifetime_value": self.customer_lifetime_value,
            "churn_risk": self.calculate_churn_risk(),
            "upsell_opportunities": self.identify_upsell_opportunities(),
            "retention_strategy": self.recommend_retention_strategy()
        }

    @frappe.whitelist()
    def update_customer_health(self, health_factors):
        """Update customer health with new factors"""
        # Update health factors
        for factor, value in health_factors.items():
            if hasattr(self, factor):
                setattr(self, factor, value)
        
        # Recalculate health score
        self.customer_health_score = self.calculate_health_score()
        
        # Update health status
        self.health_status = self.determine_health_status()
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "health_score": self.customer_health_score,
            "health_status": self.health_status
        }

    @frappe.whitelist()
    def get_customer_insights(self):
        """Get customer insights"""
        return {
            "customer_segment": self.determine_customer_segment(),
            "churn_risk": self.calculate_churn_risk(),
            "upsell_opportunities": self.identify_upsell_opportunities(),
            "retention_strategy": self.recommend_retention_strategy(),
            "health_factors": {
                "revenue_trend": self.get_revenue_trend_score(),
                "payment_behavior": self.get_payment_behavior_score(),
                "engagement_level": self.get_engagement_level_score(),
                "satisfaction_rating": self.get_satisfaction_rating_score(),
                "support_tickets": self.get_support_tickets_score()
            }
        }
