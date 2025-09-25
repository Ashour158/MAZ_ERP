# Approval System - Advanced Approval Management

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class ApprovalSystem(Document):
    def autoname(self):
        """Generate unique approval ID"""
        if not self.approval_id:
            self.approval_id = make_autoname("APR-.YYYY.-.MM.-.#####")
        self.name = self.approval_id

    def validate(self):
        """Validate approval data"""
        self.validate_approval_data()
        self.set_defaults()
        self.validate_approval_chain()
        self.calculate_approval_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_approval_settings()
        self.setup_approval_permissions()
        self.generate_approval_insights()

    def after_insert(self):
        """Process after inserting new approval"""
        self.create_approval_profile()
        self.setup_approval_workflow()
        self.create_approval_analytics()
        self.initialize_approval_tracking()

    def on_update(self):
        """Process on approval update"""
        self.update_approval_analytics()
        self.sync_approval_data()
        self.update_approval_status()
        self.process_approval_changes()

    def validate_approval_data(self):
        """Validate approval information"""
        if not self.approval_name:
            frappe.throw(_("Approval name is required"))
        
        if not self.approval_type:
            frappe.throw(_("Approval type is required"))
        
        if not self.approval_chain:
            frappe.throw(_("Approval chain is required"))

    def validate_approval_chain(self):
        """Validate approval chain"""
        for approver in self.approval_chain:
            if not approver.approver:
                frappe.throw(_("Approver is required"))
            
            if not approver.approval_level:
                frappe.throw(_("Approval level is required"))
            
            if not approver.approval_order:
                frappe.throw(_("Approval order is required"))

    def set_defaults(self):
        """Set default values for new approval"""
        if not self.approval_status:
            self.approval_status = "Pending"
        
        if not self.approval_priority:
            self.approval_priority = "Medium"
        
        if not self.approval_category:
            self.approval_category = "General"
        
        if not self.is_urgent:
            self.is_urgent = 0

    def calculate_approval_metrics(self):
        """Calculate approval metrics"""
        # Calculate approval complexity
        self.approval_complexity = self.calculate_complexity()
        
        # Calculate estimated duration
        self.estimated_duration = self.calculate_estimated_duration()
        
        # Calculate approval risk
        self.approval_risk = self.calculate_approval_risk()
        
        # Calculate approval efficiency
        self.approval_efficiency = self.calculate_approval_efficiency()

    def calculate_complexity(self):
        """Calculate approval complexity"""
        complexity_factors = {
            'approver_count': len(self.approval_chain),
            'approval_levels': len(set([a.approval_level for a in self.approval_chain])),
            'approval_type': self.get_approval_type_complexity(),
            'approval_amount': self.get_approval_amount_complexity()
        }
        
        # Calculate complexity score
        complexity_score = (
            complexity_factors['approver_count'] * 0.3 +
            complexity_factors['approval_levels'] * 0.3 +
            complexity_factors['approval_type'] * 0.2 +
            complexity_factors['approval_amount'] * 0.2
        )
        
        if complexity_score <= 3:
            return "Simple"
        elif complexity_score <= 6:
            return "Medium"
        else:
            return "Complex"

    def get_approval_type_complexity(self):
        """Get approval type complexity"""
        type_complexity = {
            "Financial": 3,
            "Contract": 4,
            "Policy": 2,
            "Operational": 1,
            "Strategic": 5
        }
        
        return type_complexity.get(self.approval_type, 2)

    def get_approval_amount_complexity(self):
        """Get approval amount complexity"""
        if self.approval_amount:
            if self.approval_amount > 1000000:
                return 5
            elif self.approval_amount > 100000:
                return 4
            elif self.approval_amount > 10000:
                return 3
            elif self.approval_amount > 1000:
                return 2
            else:
                return 1
        else:
            return 1

    def calculate_estimated_duration(self):
        """Calculate estimated approval duration"""
        total_duration = 0
        
        for approver in self.approval_chain:
            if approver.estimated_duration:
                total_duration += approver.estimated_duration
            else:
                # Default duration based on approval level
                level_duration = {
                    "Level 1": 1,  # 1 hour
                    "Level 2": 4,  # 4 hours
                    "Level 3": 8,  # 8 hours
                    "Level 4": 24, # 24 hours
                    "Level 5": 48  # 48 hours
                }
                total_duration += level_duration.get(approver.approval_level, 4)
        
        return total_duration

    def calculate_approval_risk(self):
        """Calculate approval risk"""
        risk_factors = {
            'approval_amount': self.get_amount_risk(),
            'approval_type': self.get_type_risk(),
            'approver_availability': self.get_approver_availability_risk(),
            'approval_urgency': self.get_urgency_risk()
        }
        
        # Calculate risk score
        risk_score = (
            risk_factors['approval_amount'] * 0.3 +
            risk_factors['approval_type'] * 0.3 +
            risk_factors['approver_availability'] * 0.2 +
            risk_factors['approval_urgency'] * 0.2
        )
        
        if risk_score >= 0.8:
            return "High Risk"
        elif risk_score >= 0.6:
            return "Medium Risk"
        else:
            return "Low Risk"

    def get_amount_risk(self):
        """Get amount-based risk"""
        if self.approval_amount:
            if self.approval_amount > 1000000:
                return 1.0
            elif self.approval_amount > 100000:
                return 0.8
            elif self.approval_amount > 10000:
                return 0.6
            elif self.approval_amount > 1000:
                return 0.4
            else:
                return 0.2
        else:
            return 0.2

    def get_type_risk(self):
        """Get type-based risk"""
        type_risk = {
            "Financial": 1.0,
            "Contract": 0.9,
            "Policy": 0.8,
            "Operational": 0.6,
            "Strategic": 0.9
        }
        
        return type_risk.get(self.approval_type, 0.5)

    def get_approver_availability_risk(self):
        """Get approver availability risk"""
        # Check approver availability
        unavailable_approvers = frappe.db.sql("""
            SELECT COUNT(*) as unavailable_count
            FROM `tabApproval Chain`
            WHERE approval = %s
            AND approver IN (
                SELECT name FROM `tabUser`
                WHERE status = 'Disabled'
                OR last_active < DATE_SUB(NOW(), INTERVAL 7 DAY)
            )
        """, self.name)[0][0]
        
        if unavailable_approvers > 0:
            return 1.0
        else:
            return 0.2

    def get_urgency_risk(self):
        """Get urgency-based risk"""
        if self.is_urgent:
            return 0.8
        else:
            return 0.2

    def calculate_approval_efficiency(self):
        """Calculate approval efficiency"""
        # Get approval history
        approval_history = frappe.db.sql("""
            SELECT AVG(approval_time) as avg_approval_time,
                   COUNT(*) as approval_count
            FROM `tabApproval History`
            WHERE approval = %s
            AND approval_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        if approval_history['approval_count'] > 0:
            # Calculate efficiency based on approval time
            if approval_history['avg_approval_time'] <= 1:  # 1 hour
                return 100
            elif approval_history['avg_approval_time'] <= 4:  # 4 hours
                return 80
            elif approval_history['avg_approval_time'] <= 8:  # 8 hours
                return 60
            elif approval_history['avg_approval_time'] <= 24:  # 24 hours
                return 40
            else:
                return 20
        else:
            return 0

    def update_approval_settings(self):
        """Update approval-specific settings"""
        # Update approval preferences
        if self.preferences:
            frappe.db.set_value("Approval System", self.name, "preferences", json.dumps(self.preferences))
        
        # Update approval tags
        if self.tags:
            frappe.db.set_value("Approval System", self.name, "tags", json.dumps(self.tags))

    def setup_approval_permissions(self):
        """Setup approval-specific permissions"""
        # Create approval-specific roles
        approval_roles = [
            f"Approval - {self.approval_id}",
            f"Type - {self.approval_type}",
            f"Category - {self.approval_category}"
        ]
        
        for role_name in approval_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_approval_insights(self):
        """Generate approval insights"""
        insights = {
            "approval_complexity": self.approval_complexity,
            "estimated_duration": self.estimated_duration,
            "approval_risk": self.approval_risk,
            "approval_efficiency": self.approval_efficiency,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.approval_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify approval optimization opportunities"""
        opportunities = []
        
        # Check for approval bottlenecks
        bottlenecks = self.identify_approval_bottlenecks()
        if bottlenecks:
            opportunities.append("Address approval bottlenecks")
        
        # Check for automation opportunities
        automation_opportunities = self.identify_automation_opportunities()
        if automation_opportunities:
            opportunities.append("Implement approval automation")
        
        # Check for approval routing optimization
        routing_optimization = self.identify_routing_optimization()
        if routing_optimization:
            opportunities.append("Optimize approval routing")
        
        return opportunities

    def identify_approval_bottlenecks(self):
        """Identify approval bottlenecks"""
        bottlenecks = []
        
        # Check for slow approvers
        slow_approvers = frappe.db.sql("""
            SELECT approver, AVG(approval_time) as avg_approval_time
            FROM `tabApproval History`
            WHERE approval = %s
            AND approval_time > %s
            GROUP BY approver
        """, (self.name, 4), as_dict=True)  # Approvals taking more than 4 hours
        
        if slow_approvers:
            bottlenecks.append("Slow approvers identified")
        
        # Check for approval delays
        approval_delays = frappe.db.sql("""
            SELECT COUNT(*) as delay_count
            FROM `tabApproval History`
            WHERE approval = %s
            AND approval_time > estimated_duration
        """, self.name)[0][0]
        
        if approval_delays > 0:
            bottlenecks.append("Approval delays identified")
        
        return bottlenecks

    def identify_automation_opportunities(self):
        """Identify automation opportunities"""
        opportunities = []
        
        # Check for repetitive approvals
        repetitive_approvals = frappe.db.sql("""
            SELECT approval_type, COUNT(*) as approval_count
            FROM `tabApproval System`
            WHERE approval_type = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY approval_type
            HAVING approval_count > 10
        """, self.approval_type)[0][0]
        
        if repetitive_approvals > 0:
            opportunities.append("High-frequency approvals can be automated")
        
        # Check for low-value approvals
        if self.approval_amount and self.approval_amount < 1000:
            opportunities.append("Low-value approvals can be automated")
        
        return opportunities

    def identify_routing_optimization(self):
        """Identify routing optimization opportunities"""
        opportunities = []
        
        # Check for sequential routing
        sequential_routing = frappe.db.sql("""
            SELECT COUNT(*) as sequential_count
            FROM `tabApproval Chain`
            WHERE approval = %s
            AND routing_type = 'Sequential'
        """, self.name)[0][0]
        
        if sequential_routing > 2:
            opportunities.append("Consider parallel approval routing")
        
        # Check for approval levels
        approval_levels = frappe.db.sql("""
            SELECT COUNT(DISTINCT approval_level) as level_count
            FROM `tabApproval Chain`
            WHERE approval = %s
        """, self.name)[0][0]
        
        if approval_levels > 4:
            opportunities.append("Consider reducing approval levels")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.approval_status == "Pending":
            actions.append("Review approval requirements")
            actions.append("Submit for approval")
            actions.append("Monitor approval progress")
        elif self.approval_status == "In Progress":
            actions.append("Follow up with approvers")
            actions.append("Address any issues")
            actions.append("Monitor approval timeline")
        elif self.approval_status == "Approved":
            actions.append("Execute approved action")
            actions.append("Update related records")
            actions.append("Notify stakeholders")
        elif self.approval_status == "Rejected":
            actions.append("Review rejection reasons")
            actions.append("Revise approval request")
            actions.append("Resubmit if appropriate")
        else:
            actions.append("Review approval status")
            actions.append("Take appropriate action")
        
        return actions

    def create_approval_profile(self):
        """Create comprehensive approval profile"""
        profile_data = {
            "approval_id": self.approval_id,
            "approval_name": self.approval_name,
            "approval_type": self.approval_type,
            "approval_category": self.approval_category,
            "approval_status": self.approval_status,
            "approval_priority": self.approval_priority,
            "is_urgent": self.is_urgent,
            "approval_amount": self.approval_amount,
            "approval_complexity": self.approval_complexity,
            "estimated_duration": self.estimated_duration,
            "approval_risk": self.approval_risk,
            "approval_efficiency": self.approval_efficiency,
            "approver_count": len(self.approval_chain)
        }
        
        frappe.get_doc({
            "doctype": "Approval Profile",
            "approval": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_approval_workflow(self):
        """Setup approval workflow"""
        workflow_data = {
            "approval": self.name,
            "workflow_type": "Approval Management",
            "steps": [
                {"step": "Approval Request", "status": "Completed"},
                {"step": "Approval Review", "status": "Pending"},
                {"step": "Approval Decision", "status": "Pending"},
                {"step": "Approval Execution", "status": "Pending"},
                {"step": "Approval Completion", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Approval Workflow",
            "approval": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_approval_analytics(self):
        """Create approval analytics"""
        analytics_data = {
            "approval": self.name,
            "analytics_type": "Approval Analytics",
            "metrics": {
                "approval_complexity": self.approval_complexity,
                "estimated_duration": self.estimated_duration,
                "approval_risk": self.approval_risk,
                "approval_efficiency": self.approval_efficiency
            },
            "insights": self.generate_approval_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Approval Analytics",
            "approval": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_approval_tracking(self):
        """Initialize approval tracking"""
        tracking_data = {
            "approval": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "approval_count": 0,
            "success_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Approval Tracking",
            "approval": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_approval_analytics(self):
        """Update approval analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "approval_complexity": self.approval_complexity,
            "estimated_duration": self.estimated_duration,
            "approval_risk": self.approval_risk,
            "approval_efficiency": self.calculate_approval_efficiency()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Approval Analytics", {"approval": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "approval": self.name,
                "analytics_type": "Approval Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_approval_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_approval_data(self):
        """Sync approval data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_approval_status(self):
        """Update approval status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Approval Tracking", {"approval": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_approval_changes(self):
        """Process approval changes"""
        # Log approval changes
        self.log_approval_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Approval Status Change",
            "approval": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.approval_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabApproval Status Change`
            WHERE approval = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Approval Status Change", {"approval": self.name}) else "New"
        
        return previous_status

    def log_approval_changes(self):
        """Log approval changes"""
        frappe.get_doc({
            "doctype": "Approval Change Log",
            "approval": self.name,
            "change_type": "Update",
            "change_description": "Approval information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update approval chain
        self.update_approval_chain()
        
        # Update approval history
        self.update_approval_history()

    def update_approval_chain(self):
        """Update approval chain"""
        # Update chain status
        frappe.db.sql("""
            UPDATE `tabApproval Chain`
            SET approval_status = %s
            WHERE approval = %s
        """, (self.approval_status, self.name))

    def update_approval_history(self):
        """Update approval history"""
        # Update history status
        frappe.db.sql("""
            UPDATE `tabApproval History`
            SET approval_status = %s
            WHERE approval = %s
        """, (self.approval_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify approvers
        self.notify_approvers()
        
        # Notify requesters
        self.notify_requesters()

    def notify_approvers(self):
        """Notify approvers"""
        for approver in self.approval_chain:
            frappe.get_doc({
                "doctype": "Approval Notification",
                "approval": self.name,
                "notification_type": "Approval Update",
                "message": f"Approval {self.approval_name} has been updated",
                "recipients": approver.approver,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def notify_requesters(self):
        """Notify requesters"""
        frappe.get_doc({
            "doctype": "Approval Notification",
            "approval": self.name,
            "notification_type": "Approval Update",
            "message": f"Approval {self.approval_name} has been updated",
            "recipients": self.requested_by,
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync approval data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_approval_dashboard_data(self):
        """Get approval dashboard data"""
        return {
            "approval_id": self.approval_id,
            "approval_name": self.approval_name,
            "approval_type": self.approval_type,
            "approval_category": self.approval_category,
            "approval_status": self.approval_status,
            "approval_priority": self.approval_priority,
            "is_urgent": self.is_urgent,
            "approval_amount": self.approval_amount,
            "approval_complexity": self.approval_complexity,
            "estimated_duration": self.estimated_duration,
            "approval_risk": self.approval_risk,
            "approval_efficiency": self.approval_efficiency,
            "approver_count": len(self.approval_chain),
            "insights": self.generate_approval_insights()
        }

    @frappe.whitelist()
    def approve_request(self, approver_notes=None):
        """Approve request"""
        if self.approval_status != "Pending":
            return {
                "status": "error",
                "message": "Only pending approvals can be approved"
            }
        
        self.approval_status = "Approved"
        self.approval_date = now()
        self.approved_by = frappe.session.user
        self.approver_notes = approver_notes
        
        # Log approval
        frappe.get_doc({
            "doctype": "Approval History",
            "approval": self.name,
            "approver": frappe.session.user,
            "approval_date": now(),
            "approval_action": "Approved",
            "approver_notes": approver_notes
        }).insert(ignore_permissions=True)
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Approval request approved successfully"
        }

    @frappe.whitelist()
    def reject_request(self, rejection_reason=None):
        """Reject request"""
        if self.approval_status != "Pending":
            return {
                "status": "error",
                "message": "Only pending approvals can be rejected"
            }
        
        self.approval_status = "Rejected"
        self.rejection_date = now()
        self.rejected_by = frappe.session.user
        self.rejection_reason = rejection_reason
        
        # Log rejection
        frappe.get_doc({
            "doctype": "Approval History",
            "approval": self.name,
            "approver": frappe.session.user,
            "approval_date": now(),
            "approval_action": "Rejected",
            "approver_notes": rejection_reason
        }).insert(ignore_permissions=True)
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Approval request rejected successfully"
        }

    @frappe.whitelist()
    def get_approval_insights(self):
        """Get approval insights"""
        return {
            "approval_complexity": self.approval_complexity,
            "estimated_duration": self.estimated_duration,
            "approval_risk": self.approval_risk,
            "approval_efficiency": self.approval_efficiency,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
