# Customer 360° View - Complete Customer Profile with Full Page View

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class Customer360View(Document):
    def autoname(self):
        """Generate unique view ID"""
        if not self.view_id:
            self.view_id = make_autoname("C360-.YYYY.-.MM.-.#####")
        self.name = self.view_id

    def validate(self):
        """Validate customer 360 view data"""
        self.validate_customer_data()
        self.set_defaults()
        self.load_customer_data()
        self.load_historical_data()
        self.load_communication_data()
        self.load_activity_logs()
        self.load_financial_data()
        self.load_opportunities()
        self.load_contacts()
        self.load_addresses()

    def before_save(self):
        """Process before saving"""
        self.update_customer_insights()
        self.generate_customer_summary()
        self.calculate_customer_metrics()

    def after_insert(self):
        """Process after inserting new view"""
        self.create_customer_timeline()
        self.setup_customer_workflow()
        self.initialize_customer_tracking()

    def on_update(self):
        """Process on view update"""
        self.update_customer_analytics()
        self.sync_customer_data()
        self.update_customer_health()

    def validate_customer_data(self):
        """Validate customer information"""
        if not self.customer:
            frappe.throw(_("Customer is required"))
        
        if not self.account_owner:
            frappe.throw(_("Account owner is required"))

    def set_defaults(self):
        """Set default values for new view"""
        if not self.view_type:
            self.view_type = "Customer 360° View"
        
        if not self.view_status:
            self.view_status = "Active"
        
        if not self.last_updated:
            self.last_updated = now()

    def load_customer_data(self):
        """Load complete customer data"""
        customer = frappe.get_doc("Customer", self.customer)
        
        self.customer_name = customer.customer_name
        self.customer_type = customer.customer_type
        self.customer_group = customer.customer_group
        self.territory = customer.territory
        self.customer_tier = customer.customer_tier
        self.customer_status = customer.customer_status
        self.industry = customer.industry
        self.website = customer.website
        self.email = customer.email
        self.phone = customer.phone
        self.mobile_no = customer.mobile_no
        self.tax_id = customer.tax_id
        self.customer_lifetime_value = customer.customer_lifetime_value
        self.customer_health_score = customer.customer_health_score
        self.customer_engagement_score = customer.customer_engagement_score
        self.customer_satisfaction_score = customer.customer_satisfaction_score

    def load_historical_data(self):
        """Load historical customer data"""
        # Get customer creation date
        self.customer_since = frappe.db.get_value("Customer", self.customer, "creation")
        
        # Get customer history
        self.customer_history = self.get_customer_history()
        
        # Get customer milestones
        self.customer_milestones = self.get_customer_milestones()
        
        # Get customer achievements
        self.customer_achievements = self.get_customer_achievements()

    def get_customer_history(self):
        """Get customer history"""
        history = []
        
        # Get customer creation
        history.append({
            "date": frappe.db.get_value("Customer", self.customer, "creation"),
            "event": "Customer Created",
            "description": "Customer account was created",
            "type": "creation"
        })
        
        # Get sales history
        sales_history = frappe.db.sql("""
            SELECT 
                name,
                posting_date,
                grand_total,
                status
            FROM `tabSales Invoice`
            WHERE customer = %s
            ORDER BY posting_date DESC
            LIMIT 10
        """, self.customer, as_dict=True)
        
        for sale in sales_history:
            history.append({
                "date": sale.posting_date,
                "event": "Sales Invoice",
                "description": f"Invoice {sale.name} - {sale.grand_total}",
                "type": "sales",
                "amount": sale.grand_total,
                "status": sale.status
            })
        
        # Get opportunity history
        opportunity_history = frappe.db.sql("""
            SELECT 
                name,
                creation,
                opportunity_amount,
                stage
            FROM `tabOpportunity`
            WHERE customer = %s
            ORDER BY creation DESC
            LIMIT 10
        """, self.customer, as_dict=True)
        
        for opp in opportunity_history:
            history.append({
                "date": opp.creation,
                "event": "Opportunity",
                "description": f"Opportunity {opp.name} - {opp.opportunity_amount}",
                "type": "opportunity",
                "amount": opp.opportunity_amount,
                "stage": opp.stage
            })
        
        return history

    def get_customer_milestones(self):
        """Get customer milestones"""
        milestones = []
        
        # First sale milestone
        first_sale = frappe.db.sql("""
            SELECT MIN(posting_date) as first_sale_date
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus = 1
        """, self.customer)[0][0]
        
        if first_sale:
            milestones.append({
                "date": first_sale,
                "milestone": "First Sale",
                "description": "Customer's first purchase",
                "type": "sales"
            })
        
        # Revenue milestones
        revenue_milestones = [10000, 50000, 100000, 250000, 500000, 1000000]
        
        for milestone in revenue_milestones:
            milestone_date = frappe.db.sql("""
                SELECT MIN(posting_date) as milestone_date
                FROM `tabSales Invoice`
                WHERE customer = %s 
                AND docstatus = 1
                AND grand_total >= %s
            """, (self.customer, milestone))[0][0]
            
            if milestone_date:
                milestones.append({
                    "date": milestone_date,
                    "milestone": f"${milestone:,} Revenue",
                    "description": f"Reached ${milestone:,} in total revenue",
                    "type": "revenue"
                })
        
        return milestones

    def get_customer_achievements(self):
        """Get customer achievements"""
        achievements = []
        
        # Total revenue achievement
        total_revenue = frappe.db.sql("""
            SELECT SUM(grand_total) as total_revenue
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus = 1
        """, self.customer)[0][0] or 0
        
        if total_revenue > 0:
            achievements.append({
                "achievement": "Total Revenue",
                "value": f"${total_revenue:,.2f}",
                "description": "Total revenue generated from customer"
            })
        
        # Number of orders achievement
        order_count = frappe.db.sql("""
            SELECT COUNT(*) as order_count
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus = 1
        """, self.customer)[0][0]
        
        if order_count > 0:
            achievements.append({
                "achievement": "Total Orders",
                "value": f"{order_count}",
                "description": "Total number of orders placed"
            })
        
        # Customer loyalty achievement
        customer_since = frappe.db.get_value("Customer", self.customer, "creation")
        if customer_since:
            days_since = (now().date() - customer_since.date()).days
            if days_since > 365:
                achievements.append({
                    "achievement": "Loyal Customer",
                    "value": f"{days_since} days",
                    "description": "Customer for over 1 year"
                })
        
        return achievements

    def load_communication_data(self):
        """Load communication data"""
        # Get all communications
        communications = frappe.db.sql("""
            SELECT 
                name,
                creation,
                communication_type,
                content,
                sender,
                recipient
            FROM `tabCommunication`
            WHERE reference_doctype = 'Customer'
            AND reference_name = %s
            ORDER BY creation DESC
            LIMIT 50
        """, self.customer, as_dict=True)
        
        self.communications = communications
        
        # Get email communications
        email_communications = frappe.db.sql("""
            SELECT 
                name,
                creation,
                subject,
                content,
                sender,
                recipient
            FROM `tabCommunication`
            WHERE reference_doctype = 'Customer'
            AND reference_name = %s
            AND communication_type = 'Communication'
            ORDER BY creation DESC
            LIMIT 20
        """, self.customer, as_dict=True)
        
        self.email_communications = email_communications

    def load_activity_logs(self):
        """Load activity logs"""
        # Get all activities
        activities = frappe.db.sql("""
            SELECT 
                name,
                activity_date,
                activity_type,
                description,
                assigned_to,
                status
            FROM `tabCustomer Activity`
            WHERE customer = %s
            ORDER BY activity_date DESC
            LIMIT 50
        """, self.customer, as_dict=True)
        
        self.activities = activities
        
        # Get upcoming activities
        upcoming_activities = frappe.db.sql("""
            SELECT 
                name,
                activity_date,
                activity_type,
                description,
                assigned_to,
                status
            FROM `tabCustomer Activity`
            WHERE customer = %s
            AND activity_date >= %s
            ORDER BY activity_date ASC
            LIMIT 10
        """, (self.customer, now().date()), as_dict=True)
        
        self.upcoming_activities = upcoming_activities

    def load_financial_data(self):
        """Load financial data"""
        # Get open invoices
        open_invoices = frappe.db.sql("""
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
        """, self.customer, as_dict=True)
        
        self.open_invoices = open_invoices
        
        # Get recent orders
        recent_orders = frappe.db.sql("""
            SELECT 
                name,
                posting_date,
                grand_total,
                status
            FROM `tabSales Order`
            WHERE customer = %s
            ORDER BY posting_date DESC
            LIMIT 10
        """, self.customer, as_dict=True)
        
        self.recent_orders = recent_orders
        
        # Get payment history
        payment_history = frappe.db.sql("""
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
        
        self.payment_history = payment_history

    def load_opportunities(self):
        """Load opportunities"""
        # Get all opportunities
        opportunities = frappe.db.sql("""
            SELECT 
                name,
                creation,
                opportunity_amount,
                stage,
                probability,
                expected_closing,
                status
            FROM `tabOpportunity`
            WHERE customer = %s
            ORDER BY creation DESC
        """, self.customer, as_dict=True)
        
        self.opportunities = opportunities
        
        # Get active opportunities
        active_opportunities = frappe.db.sql("""
            SELECT 
                name,
                creation,
                opportunity_amount,
                stage,
                probability,
                expected_closing,
                status
            FROM `tabOpportunity`
            WHERE customer = %s
            AND status = 'Open'
            ORDER BY expected_closing ASC
        """, self.customer, as_dict=True)
        
        self.active_opportunities = active_opportunities

    def load_contacts(self):
        """Load contacts"""
        # Get all contacts
        contacts = frappe.db.sql("""
            SELECT 
                name,
                first_name,
                last_name,
                email_id,
                mobile_no,
                phone,
                designation,
                department
            FROM `tabContact`
            WHERE customer = %s
            ORDER BY creation DESC
        """, self.customer, as_dict=True)
        
        self.contacts = contacts

    def load_addresses(self):
        """Load addresses"""
        # Get all addresses
        addresses = frappe.db.sql("""
            SELECT 
                name,
                address_type,
                address_line1,
                address_line2,
                city,
                state,
                country,
                pincode,
                is_primary_address,
                is_shipping_address
            FROM `tabAddress`
            WHERE customer = %s
            ORDER BY creation DESC
        """, self.customer, as_dict=True)
        
        self.addresses = addresses

    def update_customer_insights(self):
        """Update customer insights"""
        insights = {
            "customer_segment": self.determine_customer_segment(),
            "churn_risk": self.calculate_churn_risk(),
            "upsell_opportunities": self.identify_upsell_opportunities(),
            "retention_strategy": self.recommend_retention_strategy(),
            "next_best_actions": self.recommend_next_actions()
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
        if self.customer_health_score >= 0.8:
            return "Low Risk"
        elif self.customer_health_score >= 0.6:
            return "Medium Risk"
        else:
            return "High Risk"

    def identify_upsell_opportunities(self):
        """Identify upsell opportunities"""
        opportunities = []
        
        if self.customer_tier == "Standard":
            opportunities.append("Upgrade to Premium tier")
        
        if not self.has_premium_support:
            opportunities.append("Add premium support")
        
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

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.calculate_churn_risk() == "High Risk":
            actions.append("Schedule immediate customer success call")
            actions.append("Review customer satisfaction")
            actions.append("Implement retention campaign")
        elif self.calculate_churn_risk() == "Medium Risk":
            actions.append("Schedule regular check-in call")
            actions.append("Send customer satisfaction survey")
            actions.append("Review customer usage patterns")
        else:
            actions.append("Continue regular communication")
            actions.append("Monitor customer health")
            actions.append("Look for upsell opportunities")
        
        return actions

    def generate_customer_summary(self):
        """Generate customer summary"""
        summary = {
            "customer_name": self.customer_name,
            "customer_tier": self.customer_tier,
            "customer_since": self.customer_since,
            "total_revenue": self.calculate_total_revenue(),
            "total_orders": self.calculate_total_orders(),
            "health_score": self.customer_health_score,
            "engagement_score": self.customer_engagement_score,
            "satisfaction_score": self.customer_satisfaction_score,
            "churn_risk": self.calculate_churn_risk(),
            "upsell_opportunities": self.identify_upsell_opportunities()
        }
        
        self.customer_summary = json.dumps(summary)

    def calculate_total_revenue(self):
        """Calculate total revenue"""
        total_revenue = frappe.db.sql("""
            SELECT SUM(grand_total) as total_revenue
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus = 1
        """, self.customer)[0][0] or 0
        
        return total_revenue

    def calculate_total_orders(self):
        """Calculate total orders"""
        total_orders = frappe.db.sql("""
            SELECT COUNT(*) as total_orders
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus = 1
        """, self.customer)[0][0] or 0
        
        return total_orders

    def calculate_customer_metrics(self):
        """Calculate customer metrics"""
        metrics = {
            "total_revenue": self.calculate_total_revenue(),
            "total_orders": self.calculate_total_orders(),
            "average_order_value": self.calculate_average_order_value(),
            "customer_lifetime_value": self.customer_lifetime_value,
            "health_score": self.customer_health_score,
            "engagement_score": self.customer_engagement_score,
            "satisfaction_score": self.customer_satisfaction_score
        }
        
        self.customer_metrics = json.dumps(metrics)

    def calculate_average_order_value(self):
        """Calculate average order value"""
        total_revenue = self.calculate_total_revenue()
        total_orders = self.calculate_total_orders()
        
        if total_orders > 0:
            return total_revenue / total_orders
        else:
            return 0

    def create_customer_timeline(self):
        """Create customer timeline"""
        timeline_data = {
            "customer": self.customer,
            "timeline_events": self.customer_history,
            "milestones": self.customer_milestones,
            "achievements": self.customer_achievements,
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Customer Timeline",
            "customer": self.customer,
            "timeline_data": json.dumps(timeline_data)
        }).insert(ignore_permissions=True)

    def setup_customer_workflow(self):
        """Setup customer workflow"""
        workflow_data = {
            "customer": self.customer,
            "workflow_type": "Customer Management",
            "steps": [
                {"step": "Customer Onboarding", "status": "Completed"},
                {"step": "Initial Engagement", "status": "Pending"},
                {"step": "Relationship Building", "status": "Pending"},
                {"step": "Value Delivery", "status": "Pending"},
                {"step": "Growth Planning", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Customer Workflow",
            "customer": self.customer,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def initialize_customer_tracking(self):
        """Initialize customer tracking"""
        tracking_data = {
            "customer": self.customer,
            "account_owner": self.account_owner,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "engagement_score": self.customer_engagement_score
        }
        
        frappe.get_doc({
            "doctype": "Customer Tracking",
            "customer": self.customer,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_customer_analytics(self):
        """Update customer analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "total_revenue": self.calculate_total_revenue(),
            "total_orders": self.calculate_total_orders(),
            "average_order_value": self.calculate_average_order_value(),
            "customer_lifetime_value": self.customer_lifetime_value,
            "health_score": self.customer_health_score,
            "engagement_score": self.customer_engagement_score,
            "satisfaction_score": self.customer_satisfaction_score
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Customer Analytics", {"customer": self.customer})
        if analytics:
            analytics.analytics_data = json.dumps({
                "customer": self.customer,
                "analytics_type": "Customer 360° Analytics",
                "metrics": updated_metrics,
                "insights": self.update_customer_insights(),
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
        health = frappe.get_doc("Customer Health", {"customer": self.customer})
        if health:
            health.health_score = self.customer_health_score
            health.health_status = self.determine_health_status()
            health.last_updated = now()
            health.save()

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

    def sync_with_external_crm(self):
        """Sync customer data with external CRM"""
        # Implementation for external CRM sync
        pass

    @frappe.whitelist()
    def get_customer_360_data(self):
        """Get complete customer 360 data"""
        return {
            "customer_info": {
                "customer_name": self.customer_name,
                "customer_type": self.customer_type,
                "customer_group": self.customer_group,
                "territory": self.territory,
                "customer_tier": self.customer_tier,
                "customer_status": self.customer_status,
                "industry": self.industry,
                "website": self.website,
                "email": self.email,
                "phone": self.phone,
                "mobile_no": self.mobile_no,
                "tax_id": self.tax_id
            },
            "metrics": {
                "customer_lifetime_value": self.customer_lifetime_value,
                "customer_health_score": self.customer_health_score,
                "customer_engagement_score": self.customer_engagement_score,
                "customer_satisfaction_score": self.customer_satisfaction_score,
                "total_revenue": self.calculate_total_revenue(),
                "total_orders": self.calculate_total_orders(),
                "average_order_value": self.calculate_average_order_value()
            },
            "historical_data": {
                "customer_history": self.customer_history,
                "customer_milestones": self.customer_milestones,
                "customer_achievements": self.customer_achievements
            },
            "communication_data": {
                "communications": self.communications,
                "email_communications": self.email_communications
            },
            "activity_data": {
                "activities": self.activities,
                "upcoming_activities": self.upcoming_activities
            },
            "financial_data": {
                "open_invoices": self.open_invoices,
                "recent_orders": self.recent_orders,
                "payment_history": self.payment_history
            },
            "opportunity_data": {
                "opportunities": self.opportunities,
                "active_opportunities": self.active_opportunities
            },
            "contact_data": {
                "contacts": self.contacts
            },
            "address_data": {
                "addresses": self.addresses
            },
            "insights": {
                "customer_segment": self.determine_customer_segment(),
                "churn_risk": self.calculate_churn_risk(),
                "upsell_opportunities": self.identify_upsell_opportunities(),
                "retention_strategy": self.recommend_retention_strategy(),
                "next_best_actions": self.recommend_next_actions()
            }
        }

    @frappe.whitelist()
    def add_activity_log(self, activity_data):
        """Add activity log"""
        activity = frappe.get_doc({
            "doctype": "Customer Activity",
            "customer": self.customer,
            "activity_date": activity_data.get('activity_date', now().date()),
            "activity_type": activity_data.get('activity_type'),
            "description": activity_data.get('description'),
            "summary": activity_data.get('summary'),
            "next_step": activity_data.get('next_step'),
            "assigned_to": activity_data.get('assigned_to', frappe.session.user),
            "status": activity_data.get('status', 'Completed'),
            "created_by": frappe.session.user
        })
        activity.insert(ignore_permissions=True)
        
        # Update customer tracking
        tracking = frappe.get_doc("Customer Tracking", {"customer": self.customer})
        if tracking:
            tracking.activity_count += 1
            tracking.last_activity = now()
            tracking.save()
        
        return {
            "status": "success",
            "activity_id": activity.name,
            "message": "Activity log added successfully"
        }

    @frappe.whitelist()
    def update_customer_insights(self):
        """Update customer insights"""
        insights = {
            "customer_segment": self.determine_customer_segment(),
            "churn_risk": self.calculate_churn_risk(),
            "upsell_opportunities": self.identify_upsell_opportunities(),
            "retention_strategy": self.recommend_retention_strategy(),
            "next_best_actions": self.recommend_next_actions()
        }
        
        self.customer_insights = json.dumps(insights)
        self.save()
        
        return {
            "status": "success",
            "insights": insights
        }
