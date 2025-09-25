# Enhanced Maintenance Ticket with AI Features

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta

class MaintenanceTicket(Document):
    def autoname(self):
        """Generate unique ticket number"""
        if not self.ticket_number:
            self.ticket_number = make_autoname("TKT-.YYYY.-.MM.-.#####")
        self.name = self.ticket_number

    def validate(self):
        """Validate ticket data"""
        self.validate_priority()
        self.validate_sla()
        self.calculate_ai_sentiment()
        self.set_defaults()

    def before_save(self):
        """Process before saving"""
        self.update_sla_status()
        self.check_escalation()
        self.generate_ai_insights()

    def after_insert(self):
        """Process after inserting new ticket"""
        self.send_notifications()
        self.create_communication_log()
        self.update_customer_analytics()

    def on_update(self):
        """Process on ticket update"""
        self.log_status_change()
        self.update_ai_analytics()
        self.check_sla_breach()

    def validate_priority(self):
        """Validate priority based on business rules"""
        if self.priority == "Critical" and not self.assigned_to:
            frappe.throw(_("Critical tickets must be assigned immediately"))
        
        if self.priority == "High" and self.expected_resolution:
            expected = get_datetime(self.expected_resolution)
            if expected < get_datetime(now()) + timedelta(hours=4):
                frappe.msgprint(_("High priority tickets should be resolved within 4 hours"))

    def validate_sla(self):
        """Validate SLA compliance"""
        if self.sla_status == "Breached":
            frappe.msgprint(_("SLA has been breached for this ticket"), alert=True)

    def calculate_ai_sentiment(self):
        """Calculate AI sentiment score for ticket content"""
        if self.description:
            # This would integrate with AI service
            sentiment_score = self.analyze_sentiment(self.description)
            self.ai_sentiment_score = sentiment_score
            
            if sentiment_score < 0.3:
                self.priority = "High" if self.priority != "Critical" else "Critical"
                frappe.msgprint(_("Negative sentiment detected - Priority escalated"))

    def analyze_sentiment(self, text):
        """Analyze sentiment of text using AI"""
        # Placeholder for AI sentiment analysis
        # In production, this would call an AI service
        import random
        return round(random.uniform(0.1, 0.9), 2)

    def set_defaults(self):
        """Set default values"""
        if not self.status:
            self.status = "Open"
        
        if not self.ticket_type:
            self.ticket_type = "Support"
        
        if not self.source:
            self.source = "Web Portal"

    def update_sla_status(self):
        """Update SLA status based on current time"""
        if self.sla and self.expected_resolution:
            current_time = get_datetime(now())
            expected_time = get_datetime(self.expected_resolution)
            
            if current_time > expected_time:
                self.sla_status = "Breached"
            elif current_time > expected_time - timedelta(hours=1):
                self.sla_status = "At Risk"
            else:
                self.sla_status = "On Track"

    def check_escalation(self):
        """Check if ticket needs escalation"""
        if self.sla_status == "Breached" and self.priority != "Critical":
            self.priority = "High"
            self.escalated = 1
            self.escalated_at = now()
            frappe.msgprint(_("Ticket escalated due to SLA breach"))

    def generate_ai_insights(self):
        """Generate AI insights for the ticket"""
        insights = []
        
        # Analyze ticket content for patterns
        if "urgent" in self.description.lower():
            insights.append("Urgency keywords detected")
        
        if "bug" in self.description.lower():
            insights.append("Potential bug report")
        
        if "feature" in self.description.lower():
            insights.append("Feature request identified")
        
        self.ai_insights = json.dumps(insights)

    def send_notifications(self):
        """Send notifications for ticket events"""
        # Send email to assigned user
        if self.assigned_to:
            self.send_assignment_notification()
        
        # Send notification to customer
        if self.customer:
            self.send_customer_notification()

    def send_assignment_notification(self):
        """Send notification to assigned user"""
        frappe.sendmail(
            recipients=[self.assigned_to],
            subject=f"New Ticket Assigned: {self.ticket_number}",
            message=f"You have been assigned a new ticket: {self.subject}",
            reference_doctype=self.doctype,
            reference_name=self.name
        )

    def send_customer_notification(self):
        """Send notification to customer"""
        if self.customer_email:
            frappe.sendmail(
                recipients=[self.customer_email],
                subject=f"Ticket Created: {self.ticket_number}",
                message=f"Your ticket has been created and will be processed shortly.",
                reference_doctype=self.doctype,
                reference_name=self.name
            )

    def create_communication_log(self):
        """Create communication log entry"""
        frappe.get_doc({
            "doctype": "Maintenance Communication",
            "ticket_id": self.name,
            "communication_type": "Ticket Created",
            "content": f"Ticket {self.ticket_number} created with priority {self.priority}",
            "sentiment_score": self.ai_sentiment_score,
            "created_by": frappe.session.user
        }).insert()

    def update_customer_analytics(self):
        """Update customer analytics"""
        if self.customer:
            # Update customer ticket count
            customer_doc = frappe.get_doc("Customer", self.customer)
            if not hasattr(customer_doc, 'total_tickets'):
                customer_doc.total_tickets = 0
            customer_doc.total_tickets += 1
            customer_doc.save()

    def log_status_change(self):
        """Log status changes"""
        if self.has_value_changed('status'):
            frappe.get_doc({
                "doctype": "Maintenance Communication",
                "ticket_id": self.name,
                "communication_type": "Status Change",
                "content": f"Status changed to {self.status}",
                "created_by": frappe.session.user
            }).insert()

    def update_ai_analytics(self):
        """Update AI analytics for the ticket"""
        # This would update AI models with ticket data
        pass

    def check_sla_breach(self):
        """Check for SLA breach and take action"""
        if self.sla_status == "Breached":
            # Send escalation notification
            self.send_escalation_notification()
            
            # Update escalation metrics
            self.escalated = 1
            self.escalated_at = now()

    def send_escalation_notification(self):
        """Send escalation notification"""
        managers = frappe.get_all("User", 
            filters={"role_profile_name": "Maintenance Manager"},
            fields=["email"]
        )
        
        for manager in managers:
            frappe.sendmail(
                recipients=[manager.email],
                subject=f"SLA Breach Alert: {self.ticket_number}",
                message=f"Ticket {self.ticket_number} has breached SLA and requires immediate attention.",
                reference_doctype=self.doctype,
                reference_name=self.name
            )

    def get_ai_recommendations(self):
        """Get AI recommendations for ticket resolution"""
        recommendations = []
        
        # Analyze similar resolved tickets
        similar_tickets = frappe.get_all("Maintenance Ticket",
            filters={
                "status": "Closed",
                "subject": ["like", f"%{self.subject[:20]}%"]
            },
            fields=["resolution", "time_to_resolution"]
        )
        
        if similar_tickets:
            recommendations.append("Similar tickets found - check resolution patterns")
        
        # Analyze customer history
        if self.customer:
            customer_tickets = frappe.get_all("Maintenance Ticket",
                filters={"customer": self.customer, "status": "Closed"},
                fields=["resolution"]
            )
            
            if customer_tickets:
                recommendations.append("Customer has similar resolved tickets")
        
        return recommendations

    def get_performance_metrics(self):
        """Get performance metrics for the ticket"""
        metrics = {
            "time_to_first_response": None,
            "time_to_resolution": None,
            "customer_satisfaction": None,
            "ai_sentiment_trend": None
        }
        
        # Calculate time to first response
        if self.first_response_time:
            created_time = get_datetime(self.creation)
            first_response = get_datetime(self.first_response_time)
            metrics["time_to_first_response"] = (first_response - created_time).total_seconds() / 3600
        
        # Calculate time to resolution
        if self.status == "Closed" and self.resolution_time:
            created_time = get_datetime(self.creation)
            resolution_time = get_datetime(self.resolution_time)
            metrics["time_to_resolution"] = (resolution_time - created_time).total_seconds() / 3600
        
        return metrics

@frappe.whitelist()
def get_ticket_analytics(filters=None):
    """Get ticket analytics data"""
    if not filters:
        filters = {}
    
    # Get ticket statistics
    stats = frappe.db.sql("""
        SELECT 
            COUNT(*) as total_tickets,
            SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_tickets,
            SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) as closed_tickets,
            SUM(CASE WHEN sla_status = 'Breached' THEN 1 ELSE 0 END) as breached_tickets,
            AVG(ai_sentiment_score) as avg_sentiment
        FROM `tabMaintenance Ticket`
        WHERE creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    """, as_dict=True)
    
    return stats[0] if stats else {}

@frappe.whitelist()
def get_ai_insights(ticket_id):
    """Get AI insights for a specific ticket"""
    ticket = frappe.get_doc("Maintenance Ticket", ticket_id)
    
    insights = {
        "sentiment_score": ticket.ai_sentiment_score,
        "recommendations": ticket.get_ai_recommendations(),
        "performance_metrics": ticket.get_performance_metrics(),
        "similar_tickets": frappe.get_all("Maintenance Ticket",
            filters={
                "name": ["!=", ticket_id],
                "subject": ["like", f"%{ticket.subject[:20]}%"]
            },
            fields=["name", "subject", "status", "resolution"]
        )
    }
    
    return insights

@frappe.whitelist()
def escalate_ticket(ticket_id, reason):
    """Manually escalate a ticket"""
    ticket = frappe.get_doc("Maintenance Ticket", ticket_id)
    
    if ticket.priority == "Critical":
        frappe.throw(_("Ticket is already at highest priority"))
    
    ticket.priority = "High" if ticket.priority == "Medium" else "Critical"
    ticket.escalated = 1
    ticket.escalated_at = now()
    ticket.escalation_reason = reason
    ticket.save()
    
    frappe.msgprint(_("Ticket escalated successfully"))
    return ticket
