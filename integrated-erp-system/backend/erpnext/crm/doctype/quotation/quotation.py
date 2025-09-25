# Enhanced Quotation DocType - Complete Quotation Management System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class Quotation(Document):
    def autoname(self):
        """Generate unique quotation ID"""
        if not self.quotation_id:
            self.quotation_id = make_autoname("QUO-.YYYY.-.MM.-.#####")
        self.name = self.quotation_id

    def validate(self):
        """Validate quotation data"""
        self.validate_quotation_data()
        self.set_defaults()
        self.validate_customer_data()
        self.validate_contact_data()
        self.calculate_quotation_totals()
        self.determine_quotation_status()

    def before_save(self):
        """Process before saving"""
        self.update_quotation_settings()
        self.setup_quotation_permissions()
        self.generate_quotation_insights()

    def after_insert(self):
        """Process after inserting new quotation"""
        self.create_quotation_profile()
        self.setup_quotation_workflow()
        self.create_quotation_analytics()
        self.initialize_quotation_tracking()

    def on_update(self):
        """Process on quotation update"""
        self.update_quotation_analytics()
        self.sync_quotation_data()
        self.update_quotation_status()
        self.process_quotation_changes()

    def validate_quotation_data(self):
        """Validate quotation information"""
        if not self.quotation_name:
            frappe.throw(_("Quotation name is required"))
        
        if not self.customer:
            frappe.throw(_("Customer is required"))
        
        if not self.quotation_date:
            frappe.throw(_("Quotation date is required"))
        
        if not self.valid_until:
            frappe.throw(_("Valid until date is required"))

    def validate_customer_data(self):
        """Validate customer data"""
        if self.customer and not frappe.db.exists("Customer", self.customer):
            frappe.throw(_("Customer does not exist"))

    def validate_contact_data(self):
        """Validate contact data"""
        if self.contact and not frappe.db.exists("Contact", self.contact):
            frappe.throw(_("Contact does not exist"))

    def set_defaults(self):
        """Set default values for new quotation"""
        if not self.quotation_status:
            self.quotation_status = "Draft"
        
        if not self.quotation_type:
            self.quotation_type = "Standard"
        
        if not self.quotation_priority:
            self.quotation_priority = "Medium"
        
        if not self.quotation_date:
            self.quotation_date = now().date()
        
        if not self.valid_until:
            self.valid_until = add_days(now().date(), 30)

    def calculate_quotation_totals(self):
        """Calculate quotation totals"""
        # Calculate item totals
        self.calculate_item_totals()
        
        # Calculate tax totals
        self.calculate_tax_totals()
        
        # Calculate discount totals
        self.calculate_discount_totals()
        
        # Calculate final totals
        self.calculate_final_totals()

    def calculate_item_totals(self):
        """Calculate item totals"""
        total_amount = 0
        total_quantity = 0
        
        for item in self.items:
            item.amount = item.rate * item.qty
            total_amount += item.amount
            total_quantity += item.qty
        
        self.total_amount = total_amount
        self.total_quantity = total_quantity

    def calculate_tax_totals(self):
        """Calculate tax totals"""
        total_tax = 0
        
        for tax in self.taxes:
            if tax.rate > 0:
                tax.amount = (self.total_amount * tax.rate) / 100
                total_tax += tax.amount
        
        self.total_tax = total_tax

    def calculate_discount_totals(self):
        """Calculate discount totals"""
        total_discount = 0
        
        # Item level discounts
        for item in self.items:
            if item.discount_percentage > 0:
                item.discount_amount = (item.amount * item.discount_percentage) / 100
                total_discount += item.discount_amount
        
        # Quotation level discount
        if self.discount_percentage > 0:
            self.discount_amount = (self.total_amount * self.discount_percentage) / 100
            total_discount += self.discount_amount
        
        self.total_discount = total_discount

    def calculate_final_totals(self):
        """Calculate final totals"""
        self.grand_total = self.total_amount + self.total_tax - self.total_discount

    def determine_quotation_status(self):
        """Determine quotation status"""
        if self.quotation_status == "Draft":
            self.status = "Draft"
        elif self.quotation_status == "Sent":
            self.status = "Sent"
        elif self.quotation_status == "Approved":
            self.status = "Approved"
        elif self.quotation_status == "Rejected":
            self.status = "Rejected"
        elif self.quotation_status == "Expired":
            self.status = "Expired"
        else:
            self.status = "Draft"

    def update_quotation_settings(self):
        """Update quotation-specific settings"""
        # Update quotation preferences
        if self.preferences:
            frappe.db.set_value("Quotation", self.name, "preferences", json.dumps(self.preferences))
        
        # Update quotation tags
        if self.tags:
            frappe.db.set_value("Quotation", self.name, "tags", json.dumps(self.tags))

    def setup_quotation_permissions(self):
        """Setup quotation-specific permissions"""
        # Create quotation-specific roles
        quotation_roles = [
            f"Quotation - {self.quotation_id}",
            f"Customer - {self.customer}",
            f"Status - {self.quotation_status}"
        ]
        
        for role_name in quotation_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_quotation_insights(self):
        """Generate quotation insights"""
        insights = {
            "quotation_status": self.quotation_status,
            "approval_status": self.determine_approval_status(),
            "pricing_analysis": self.analyze_pricing(),
            "competitiveness": self.assess_competitiveness(),
            "next_actions": self.recommend_next_actions(),
            "risk_assessment": self.assess_risk()
        }
        
        self.quotation_insights = json.dumps(insights)

    def determine_approval_status(self):
        """Determine approval status"""
        if self.quotation_status == "Draft":
            return "Pending Approval"
        elif self.quotation_status == "Sent":
            return "Awaiting Customer Response"
        elif self.quotation_status == "Approved":
            return "Approved"
        elif self.quotation_status == "Rejected":
            return "Rejected"
        else:
            return "Unknown"

    def analyze_pricing(self):
        """Analyze pricing"""
        pricing_analysis = {
            "total_amount": self.total_amount,
            "grand_total": self.grand_total,
            "discount_percentage": self.discount_percentage,
            "discount_amount": self.discount_amount,
            "tax_percentage": self.calculate_tax_percentage(),
            "tax_amount": self.total_tax,
            "profit_margin": self.calculate_profit_margin()
        }
        
        return pricing_analysis

    def calculate_tax_percentage(self):
        """Calculate tax percentage"""
        if self.total_amount > 0:
            return (self.total_tax / self.total_amount) * 100
        else:
            return 0

    def calculate_profit_margin(self):
        """Calculate profit margin"""
        # Get cost of goods sold
        cogs = self.calculate_cost_of_goods_sold()
        
        if self.total_amount > 0:
            profit_margin = ((self.total_amount - cogs) / self.total_amount) * 100
            return profit_margin
        else:
            return 0

    def calculate_cost_of_goods_sold(self):
        """Calculate cost of goods sold"""
        cogs = 0
        
        for item in self.items:
            # Get item cost from supply chain
            item_cost = frappe.db.get_value("Item", item.item_code, "standard_rate") or 0
            cogs += item_cost * item.qty
        
        return cogs

    def assess_competitiveness(self):
        """Assess competitiveness"""
        competitiveness = {
            "price_competitiveness": self.assess_price_competitiveness(),
            "value_proposition": self.assess_value_proposition(),
            "market_position": self.assess_market_position()
        }
        
        return competitiveness

    def assess_price_competitiveness(self):
        """Assess price competitiveness"""
        # Get market prices for similar items
        market_prices = self.get_market_prices()
        
        if market_prices:
            avg_market_price = sum(market_prices) / len(market_prices)
            if self.total_amount < avg_market_price * 0.9:
                return "Highly Competitive"
            elif self.total_amount < avg_market_price * 1.1:
                return "Competitive"
            else:
                return "Premium Pricing"
        else:
            return "Unknown"

    def get_market_prices(self):
        """Get market prices for similar items"""
        # Implementation for market price analysis
        return []

    def assess_value_proposition(self):
        """Assess value proposition"""
        # Analyze value proposition based on items and services
        value_score = 0
        
        for item in self.items:
            # Get item value score
            item_value = frappe.db.get_value("Item", item.item_code, "value_score") or 0
            value_score += item_value * item.qty
        
        if value_score > 80:
            return "High Value"
        elif value_score > 60:
            return "Medium Value"
        else:
            return "Low Value"

    def assess_market_position(self):
        """Assess market position"""
        # Analyze market position based on customer and competition
        if self.customer_tier == "Premium":
            return "Premium Market"
        elif self.customer_tier == "Standard":
            return "Standard Market"
        else:
            return "Value Market"

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.quotation_status == "Draft":
            actions.append("Review quotation details")
            actions.append("Submit for approval")
            actions.append("Send to customer")
        elif self.quotation_status == "Sent":
            actions.append("Follow up with customer")
            actions.append("Address customer questions")
            actions.append("Negotiate terms if needed")
        elif self.quotation_status == "Approved":
            actions.append("Convert to sales order")
            actions.append("Process payment")
            actions.append("Schedule delivery")
        elif self.quotation_status == "Rejected":
            actions.append("Analyze rejection reasons")
            actions.append("Revise quotation")
            actions.append("Resubmit if appropriate")
        else:
            actions.append("Review quotation status")
            actions.append("Take appropriate action")
        
        return actions

    def assess_risk(self):
        """Assess quotation risk"""
        risk_factors = {
            "customer_risk": self.assess_customer_risk(),
            "pricing_risk": self.assess_pricing_risk(),
            "delivery_risk": self.assess_delivery_risk(),
            "payment_risk": self.assess_payment_risk()
        }
        
        return risk_factors

    def assess_customer_risk(self):
        """Assess customer risk"""
        # Get customer credit score
        credit_score = frappe.db.get_value("Customer", self.customer, "credit_score") or 0
        
        if credit_score >= 80:
            return "Low Risk"
        elif credit_score >= 60:
            return "Medium Risk"
        else:
            return "High Risk"

    def assess_pricing_risk(self):
        """Assess pricing risk"""
        if self.grand_total > 100000:
            return "High Risk - Large Amount"
        elif self.grand_total > 50000:
            return "Medium Risk - Moderate Amount"
        else:
            return "Low Risk - Small Amount"

    def assess_delivery_risk(self):
        """Assess delivery risk"""
        # Check delivery timeline
        if self.valid_until and (self.valid_until - now().date()).days < 7:
            return "High Risk - Short Timeline"
        elif self.valid_until and (self.valid_until - now().date()).days < 30:
            return "Medium Risk - Moderate Timeline"
        else:
            return "Low Risk - Adequate Timeline"

    def assess_payment_risk(self):
        """Assess payment risk"""
        # Check payment terms
        if self.payment_terms == "Net 30":
            return "Low Risk"
        elif self.payment_terms == "Net 60":
            return "Medium Risk"
        else:
            return "High Risk"

    def create_quotation_profile(self):
        """Create comprehensive quotation profile"""
        profile_data = {
            "quotation_id": self.quotation_id,
            "quotation_name": self.quotation_name,
            "customer": self.customer,
            "contact": self.contact,
            "quotation_date": self.quotation_date,
            "valid_until": self.valid_until,
            "quotation_status": self.quotation_status,
            "quotation_type": self.quotation_type,
            "quotation_priority": self.quotation_priority,
            "total_amount": self.total_amount,
            "grand_total": self.grand_total,
            "discount_percentage": self.discount_percentage,
            "discount_amount": self.discount_amount,
            "tax_percentage": self.calculate_tax_percentage(),
            "tax_amount": self.total_tax,
            "profit_margin": self.calculate_profit_margin()
        }
        
        frappe.get_doc({
            "doctype": "Quotation Profile",
            "quotation": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_quotation_workflow(self):
        """Setup quotation workflow"""
        workflow_data = {
            "quotation": self.name,
            "workflow_type": "Quotation Management",
            "steps": [
                {"step": "Quotation Creation", "status": "Completed"},
                {"step": "Internal Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Customer Delivery", "status": "Pending"},
                {"step": "Customer Response", "status": "Pending"},
                {"step": "Follow-up", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Quotation Workflow",
            "quotation": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_quotation_analytics(self):
        """Create quotation analytics"""
        analytics_data = {
            "quotation": self.name,
            "analytics_type": "Quotation Analytics",
            "metrics": {
                "total_amount": self.total_amount,
                "grand_total": self.grand_total,
                "discount_percentage": self.discount_percentage,
                "tax_percentage": self.calculate_tax_percentage(),
                "profit_margin": self.calculate_profit_margin()
            },
            "insights": self.generate_quotation_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Quotation Analytics",
            "quotation": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_quotation_tracking(self):
        """Initialize quotation tracking"""
        tracking_data = {
            "quotation": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "status_changes": 0,
            "approval_changes": 0
        }
        
        frappe.get_doc({
            "doctype": "Quotation Tracking",
            "quotation": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_quotation_analytics(self):
        """Update quotation analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "total_amount": self.total_amount,
            "grand_total": self.grand_total,
            "discount_percentage": self.discount_percentage,
            "tax_percentage": self.calculate_tax_percentage(),
            "profit_margin": self.calculate_profit_margin()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Quotation Analytics", {"quotation": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "quotation": self.name,
                "analytics_type": "Quotation Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_quotation_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_quotation_data(self):
        """Sync quotation data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_quotation_status(self):
        """Update quotation status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Quotation Tracking", {"quotation": self.name})
        if tracking:
            tracking.status_changes += 1
            tracking.last_activity = now()
            tracking.save()

    def process_quotation_changes(self):
        """Process quotation changes"""
        # Log quotation changes
        self.log_quotation_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Quotation Status Change",
            "quotation": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.quotation_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabQuotation Status Change`
            WHERE quotation = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Quotation Status Change", {"quotation": self.name}) else "New"
        
        return previous_status

    def log_quotation_changes(self):
        """Log quotation changes"""
        frappe.get_doc({
            "doctype": "Quotation Change Log",
            "quotation": self.name,
            "change_type": "Update",
            "change_description": "Quotation information updated",
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
        # Update customer quotation count
        frappe.db.sql("""
            UPDATE `tabCustomer`
            SET quotation_count = (
                SELECT COUNT(*) FROM `tabQuotation`
                WHERE customer = %s AND status = 'Active'
            )
            WHERE name = %s
        """, (self.customer, self.customer))

    def update_opportunity_records(self):
        """Update opportunity records"""
        # Update opportunity quotation count
        if self.opportunity:
            frappe.db.sql("""
                UPDATE `tabOpportunity`
                SET quotation_count = (
                    SELECT COUNT(*) FROM `tabQuotation`
                    WHERE opportunity = %s AND status = 'Active'
                )
                WHERE name = %s
            """, (self.opportunity, self.opportunity))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify sales team
        self.notify_sales_team()
        
        # Notify approvers
        self.notify_approvers()

    def notify_sales_team(self):
        """Notify sales team"""
        frappe.get_doc({
            "doctype": "Quotation Notification",
            "quotation": self.name,
            "notification_type": "Quotation Update",
            "message": f"Quotation {self.quotation_name} has been updated",
            "recipients": "Sales Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_approvers(self):
        """Notify approvers"""
        if self.approver:
            frappe.get_doc({
                "doctype": "Quotation Notification",
                "quotation": self.name,
                "notification_type": "Quotation Update",
                "message": f"Quotation {self.quotation_name} has been updated",
                "recipients": self.approver,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync quotation data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_quotation_dashboard_data(self):
        """Get quotation dashboard data"""
        return {
            "quotation_id": self.quotation_id,
            "quotation_name": self.quotation_name,
            "customer": self.customer,
            "contact": self.contact,
            "quotation_date": self.quotation_date,
            "valid_until": self.valid_until,
            "quotation_status": self.quotation_status,
            "quotation_type": self.quotation_type,
            "quotation_priority": self.quotation_priority,
            "total_amount": self.total_amount,
            "grand_total": self.grand_total,
            "discount_percentage": self.discount_percentage,
            "discount_amount": self.discount_amount,
            "tax_percentage": self.calculate_tax_percentage(),
            "tax_amount": self.total_tax,
            "profit_margin": self.calculate_profit_margin(),
            "insights": self.generate_quotation_insights()
        }

    @frappe.whitelist()
    def approve_quotation(self, approver_notes=None):
        """Approve quotation"""
        if self.quotation_status != "Draft":
            return {
                "status": "error",
                "message": "Only draft quotations can be approved"
            }
        
        self.quotation_status = "Approved"
        self.approver = frappe.session.user
        self.approval_date = now()
        self.approver_notes = approver_notes
        
        # Log approval
        frappe.get_doc({
            "doctype": "Quotation Approval",
            "quotation": self.name,
            "approver": frappe.session.user,
            "approval_date": now(),
            "approver_notes": approver_notes
        }).insert(ignore_permissions=True)
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Quotation approved successfully"
        }

    @frappe.whitelist()
    def reject_quotation(self, rejection_reason=None):
        """Reject quotation"""
        if self.quotation_status != "Draft":
            return {
                "status": "error",
                "message": "Only draft quotations can be rejected"
            }
        
        self.quotation_status = "Rejected"
        self.rejector = frappe.session.user
        self.rejection_date = now()
        self.rejection_reason = rejection_reason
        
        # Log rejection
        frappe.get_doc({
            "doctype": "Quotation Rejection",
            "quotation": self.name,
            "rejector": frappe.session.user,
            "rejection_date": now(),
            "rejection_reason": rejection_reason
        }).insert(ignore_permissions=True)
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Quotation rejected successfully"
        }

    @frappe.whitelist()
    def send_to_customer(self, email_template=None):
        """Send quotation to customer"""
        if self.quotation_status != "Approved":
            return {
                "status": "error",
                "message": "Only approved quotations can be sent to customer"
            }
        
        self.quotation_status = "Sent"
        self.sent_date = now()
        self.sent_by = frappe.session.user
        
        # Log sending
        frappe.get_doc({
            "doctype": "Quotation Send",
            "quotation": self.name,
            "sent_by": frappe.session.user,
            "sent_date": now(),
            "email_template": email_template
        }).insert(ignore_permissions=True)
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Quotation sent to customer successfully"
        }

    @frappe.whitelist()
    def convert_to_sales_order(self):
        """Convert quotation to sales order"""
        if self.quotation_status != "Approved":
            return {
                "status": "error",
                "message": "Only approved quotations can be converted to sales order"
            }
        
        # Create sales order
        sales_order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": self.customer,
            "contact": self.contact,
            "quotation": self.name,
            "order_date": now().date(),
            "delivery_date": self.valid_until,
            "items": []
        })
        
        # Copy items
        for item in self.items:
            sales_order.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": item.rate,
                "amount": item.amount
            })
        
        sales_order.insert(ignore_permissions=True)
        
        # Update quotation status
        self.quotation_status = "Converted"
        self.conversion_date = now()
        self.sales_order = sales_order.name
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "sales_order": sales_order.name,
            "message": "Quotation converted to sales order successfully"
        }

    @frappe.whitelist()
    def get_quotation_insights(self):
        """Get quotation insights"""
        return {
            "quotation_status": self.quotation_status,
            "approval_status": self.determine_approval_status(),
            "pricing_analysis": self.analyze_pricing(),
            "competitiveness": self.assess_competitiveness(),
            "next_actions": self.recommend_next_actions(),
            "risk_assessment": self.assess_risk()
        }
