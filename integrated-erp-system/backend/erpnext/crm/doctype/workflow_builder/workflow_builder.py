# Workflow Builder - Visual Workflow Management System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class WorkflowBuilder(Document):
    def autoname(self):
        """Generate unique workflow ID"""
        if not self.workflow_id:
            self.workflow_id = make_autoname("WF-.YYYY.-.MM.-.#####")
        self.name = self.workflow_id

    def validate(self):
        """Validate workflow data"""
        self.validate_workflow_data()
        self.set_defaults()
        self.validate_workflow_steps()
        self.calculate_workflow_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_workflow_settings()
        self.setup_workflow_permissions()
        self.generate_workflow_insights()

    def after_insert(self):
        """Process after inserting new workflow"""
        self.create_workflow_profile()
        self.setup_workflow_automation()
        self.create_workflow_analytics()
        self.initialize_workflow_tracking()

    def on_update(self):
        """Process on workflow update"""
        self.update_workflow_analytics()
        self.sync_workflow_data()
        self.update_workflow_status()
        self.process_workflow_changes()

    def validate_workflow_data(self):
        """Validate workflow information"""
        if not self.workflow_name:
            frappe.throw(_("Workflow name is required"))
        
        if not self.workflow_type:
            frappe.throw(_("Workflow type is required"))
        
        if not self.workflow_steps:
            frappe.throw(_("Workflow steps are required"))

    def validate_workflow_steps(self):
        """Validate workflow steps"""
        for step in self.workflow_steps:
            if not step.step_name:
                frappe.throw(_("Step name is required"))
            
            if not step.step_type:
                frappe.throw(_("Step type is required"))
            
            if not step.step_order:
                frappe.throw(_("Step order is required"))

    def set_defaults(self):
        """Set default values for new workflow"""
        if not self.workflow_status:
            self.workflow_status = "Draft"
        
        if not self.workflow_priority:
            self.workflow_priority = "Medium"
        
        if not self.workflow_category:
            self.workflow_category = "General"
        
        if not self.is_active:
            self.is_active = 1

    def calculate_workflow_metrics(self):
        """Calculate workflow metrics"""
        # Calculate workflow complexity
        self.workflow_complexity = self.calculate_complexity()
        
        # Calculate estimated duration
        self.estimated_duration = self.calculate_estimated_duration()
        
        # Calculate success rate
        self.success_rate = self.calculate_success_rate()
        
        # Calculate efficiency score
        self.efficiency_score = self.calculate_efficiency_score()

    def calculate_complexity(self):
        """Calculate workflow complexity"""
        complexity_factors = {
            'step_count': len(self.workflow_steps),
            'approval_count': len([s for s in self.workflow_steps if s.step_type == 'Approval']),
            'automation_count': len([s for s in self.workflow_steps if s.step_type == 'Automation']),
            'condition_count': len([s for s in self.workflow_steps if s.has_conditions])
        }
        
        # Calculate complexity score
        complexity_score = (
            complexity_factors['step_count'] * 0.3 +
            complexity_factors['approval_count'] * 0.4 +
            complexity_factors['automation_count'] * 0.2 +
            complexity_factors['condition_count'] * 0.1
        )
        
        if complexity_score <= 3:
            return "Simple"
        elif complexity_score <= 6:
            return "Medium"
        else:
            return "Complex"

    def calculate_estimated_duration(self):
        """Calculate estimated workflow duration"""
        total_duration = 0
        
        for step in self.workflow_steps:
            if step.estimated_duration:
                total_duration += step.estimated_duration
        
        return total_duration

    def calculate_success_rate(self):
        """Calculate workflow success rate"""
        # Get workflow execution history
        executions = frappe.db.sql("""
            SELECT COUNT(*) as total_executions,
                   SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as successful_executions
            FROM `tabWorkflow Execution`
            WHERE workflow = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, self.name, as_dict=True)[0]
        
        if executions['total_executions'] > 0:
            success_rate = (executions['successful_executions'] / executions['total_executions']) * 100
            return round(success_rate, 2)
        else:
            return 0

    def calculate_efficiency_score(self):
        """Calculate workflow efficiency score"""
        # Get workflow performance data
        performance_data = frappe.db.sql("""
            SELECT AVG(execution_time) as avg_execution_time,
                   AVG(step_count) as avg_step_count,
                   AVG(approval_time) as avg_approval_time
            FROM `tabWorkflow Execution`
            WHERE workflow = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        # Calculate efficiency based on execution time and step count
        if performance_data['avg_execution_time'] and performance_data['avg_step_count']:
            efficiency = (performance_data['avg_step_count'] / performance_data['avg_execution_time']) * 100
            return min(efficiency, 100)
        else:
            return 0

    def update_workflow_settings(self):
        """Update workflow-specific settings"""
        # Update workflow preferences
        if self.preferences:
            frappe.db.set_value("Workflow Builder", self.name, "preferences", json.dumps(self.preferences))
        
        # Update workflow tags
        if self.tags:
            frappe.db.set_value("Workflow Builder", self.name, "tags", json.dumps(self.tags))

    def setup_workflow_permissions(self):
        """Setup workflow-specific permissions"""
        # Create workflow-specific roles
        workflow_roles = [
            f"Workflow - {self.workflow_id}",
            f"Type - {self.workflow_type}",
            f"Category - {self.workflow_category}"
        ]
        
        for role_name in workflow_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_workflow_insights(self):
        """Generate workflow insights"""
        insights = {
            "workflow_complexity": self.workflow_complexity,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.workflow_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify workflow optimization opportunities"""
        opportunities = []
        
        # Check for bottlenecks
        bottlenecks = self.identify_bottlenecks()
        if bottlenecks:
            opportunities.append("Address workflow bottlenecks")
        
        # Check for automation opportunities
        automation_opportunities = self.identify_automation_opportunities()
        if automation_opportunities:
            opportunities.append("Implement workflow automation")
        
        # Check for approval optimization
        approval_optimization = self.identify_approval_optimization()
        if approval_optimization:
            opportunities.append("Optimize approval processes")
        
        return opportunities

    def identify_bottlenecks(self):
        """Identify workflow bottlenecks"""
        bottlenecks = []
        
        # Check for steps with high execution time
        slow_steps = frappe.db.sql("""
            SELECT step_name, AVG(execution_time) as avg_time
            FROM `tabWorkflow Step Execution`
            WHERE workflow = %s
            AND execution_time > %s
            GROUP BY step_name
        """, (self.name, 3600), as_dict=True)  # Steps taking more than 1 hour
        
        if slow_steps:
            bottlenecks.append("Slow execution steps identified")
        
        # Check for approval delays
        approval_delays = frappe.db.sql("""
            SELECT step_name, AVG(approval_time) as avg_approval_time
            FROM `tabWorkflow Step Execution`
            WHERE workflow = %s
            AND step_type = 'Approval'
            AND approval_time > %s
            GROUP BY step_name
        """, (self.name, 1800), as_dict=True)  # Approvals taking more than 30 minutes
        
        if approval_delays:
            bottlenecks.append("Approval delays identified")
        
        return bottlenecks

    def identify_automation_opportunities(self):
        """Identify automation opportunities"""
        opportunities = []
        
        # Check for repetitive manual steps
        manual_steps = frappe.db.sql("""
            SELECT step_name, COUNT(*) as execution_count
            FROM `tabWorkflow Step Execution`
            WHERE workflow = %s
            AND step_type = 'Manual'
            AND execution_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY step_name
            HAVING execution_count > 10
        """, self.name, as_dict=True)
        
        if manual_steps:
            opportunities.append("High-frequency manual steps can be automated")
        
        # Check for data entry steps
        data_entry_steps = frappe.db.sql("""
            SELECT step_name
            FROM `tabWorkflow Step`
            WHERE workflow = %s
            AND step_type = 'Data Entry'
        """, self.name, as_dict=True)
        
        if data_entry_steps:
            opportunities.append("Data entry steps can be automated")
        
        return opportunities

    def identify_approval_optimization(self):
        """Identify approval optimization opportunities"""
        opportunities = []
        
        # Check for multiple approval levels
        approval_levels = frappe.db.sql("""
            SELECT COUNT(*) as approval_count
            FROM `tabWorkflow Step`
            WHERE workflow = %s
            AND step_type = 'Approval'
        """, self.name)[0][0]
        
        if approval_levels > 3:
            opportunities.append("Consider reducing approval levels")
        
        # Check for approval routing
        approval_routing = frappe.db.sql("""
            SELECT step_name
            FROM `tabWorkflow Step`
            WHERE workflow = %s
            AND step_type = 'Approval'
            AND approval_routing = 'Sequential'
        """, self.name, as_dict=True)
        
        if approval_routing:
            opportunities.append("Consider parallel approval routing")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.workflow_status == "Draft":
            actions.append("Review workflow design")
            actions.append("Test workflow execution")
            actions.append("Activate workflow")
        elif self.workflow_status == "Active":
            actions.append("Monitor workflow performance")
            actions.append("Optimize workflow steps")
            actions.append("Update workflow as needed")
        else:
            actions.append("Review workflow status")
            actions.append("Take appropriate action")
        
        return actions

    def create_workflow_profile(self):
        """Create comprehensive workflow profile"""
        profile_data = {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "workflow_type": self.workflow_type,
            "workflow_category": self.workflow_category,
            "workflow_status": self.workflow_status,
            "workflow_priority": self.workflow_priority,
            "is_active": self.is_active,
            "workflow_complexity": self.workflow_complexity,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "step_count": len(self.workflow_steps)
        }
        
        frappe.get_doc({
            "doctype": "Workflow Profile",
            "workflow": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_workflow_automation(self):
        """Setup workflow automation"""
        automation_data = {
            "workflow": self.name,
            "automation_type": "Workflow Automation",
            "triggers": self.get_workflow_triggers(),
            "actions": self.get_workflow_actions(),
            "conditions": self.get_workflow_conditions()
        }
        
        frappe.get_doc({
            "doctype": "Workflow Automation",
            "workflow": self.name,
            "automation_data": json.dumps(automation_data)
        }).insert(ignore_permissions=True)

    def get_workflow_triggers(self):
        """Get workflow triggers"""
        triggers = []
        
        for step in self.workflow_steps:
            if step.trigger_conditions:
                triggers.append({
                    "step": step.step_name,
                    "trigger": step.trigger_conditions,
                    "action": step.trigger_action
                })
        
        return triggers

    def get_workflow_actions(self):
        """Get workflow actions"""
        actions = []
        
        for step in self.workflow_steps:
            if step.step_type == "Automation":
                actions.append({
                    "step": step.step_name,
                    "action_type": step.automation_type,
                    "action_config": step.automation_config
                })
        
        return actions

    def get_workflow_conditions(self):
        """Get workflow conditions"""
        conditions = []
        
        for step in self.workflow_steps:
            if step.has_conditions:
                conditions.append({
                    "step": step.step_name,
                    "condition": step.condition_logic,
                    "action": step.condition_action
                })
        
        return conditions

    def create_workflow_analytics(self):
        """Create workflow analytics"""
        analytics_data = {
            "workflow": self.name,
            "analytics_type": "Workflow Analytics",
            "metrics": {
                "workflow_complexity": self.workflow_complexity,
                "estimated_duration": self.estimated_duration,
                "success_rate": self.success_rate,
                "efficiency_score": self.efficiency_score
            },
            "insights": self.generate_workflow_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Workflow Analytics",
            "workflow": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_workflow_tracking(self):
        """Initialize workflow tracking"""
        tracking_data = {
            "workflow": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "execution_count": 0,
            "success_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Workflow Tracking",
            "workflow": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_workflow_analytics(self):
        """Update workflow analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "workflow_complexity": self.workflow_complexity,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.calculate_success_rate(),
            "efficiency_score": self.calculate_efficiency_score()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Workflow Analytics", {"workflow": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "workflow": self.name,
                "analytics_type": "Workflow Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_workflow_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_workflow_data(self):
        """Sync workflow data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_workflow_status(self):
        """Update workflow status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Workflow Tracking", {"workflow": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_workflow_changes(self):
        """Process workflow changes"""
        # Log workflow changes
        self.log_workflow_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Workflow Status Change",
            "workflow": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.workflow_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabWorkflow Status Change`
            WHERE workflow = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Workflow Status Change", {"workflow": self.name}) else "New"
        
        return previous_status

    def log_workflow_changes(self):
        """Log workflow changes"""
        frappe.get_doc({
            "doctype": "Workflow Change Log",
            "workflow": self.name,
            "change_type": "Update",
            "change_description": "Workflow information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update workflow executions
        self.update_workflow_executions()
        
        # Update workflow steps
        self.update_workflow_steps()

    def update_workflow_executions(self):
        """Update workflow executions"""
        # Update execution status
        frappe.db.sql("""
            UPDATE `tabWorkflow Execution`
            SET workflow_status = %s
            WHERE workflow = %s
        """, (self.workflow_status, self.name))

    def update_workflow_steps(self):
        """Update workflow steps"""
        # Update step status
        frappe.db.sql("""
            UPDATE `tabWorkflow Step`
            SET workflow_status = %s
            WHERE workflow = %s
        """, (self.workflow_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify workflow users
        self.notify_workflow_users()
        
        # Notify workflow administrators
        self.notify_workflow_administrators()

    def notify_workflow_users(self):
        """Notify workflow users"""
        frappe.get_doc({
            "doctype": "Workflow Notification",
            "workflow": self.name,
            "notification_type": "Workflow Update",
            "message": f"Workflow {self.workflow_name} has been updated",
            "recipients": "Workflow Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_workflow_administrators(self):
        """Notify workflow administrators"""
        frappe.get_doc({
            "doctype": "Workflow Notification",
            "workflow": self.name,
            "notification_type": "Workflow Update",
            "message": f"Workflow {self.workflow_name} has been updated",
            "recipients": "Workflow Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync workflow data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_workflow_dashboard_data(self):
        """Get workflow dashboard data"""
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "workflow_type": self.workflow_type,
            "workflow_category": self.workflow_category,
            "workflow_status": self.workflow_status,
            "workflow_priority": self.workflow_priority,
            "is_active": self.is_active,
            "workflow_complexity": self.workflow_complexity,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "step_count": len(self.workflow_steps),
            "insights": self.generate_workflow_insights()
        }

    @frappe.whitelist()
    def activate_workflow(self):
        """Activate workflow"""
        if self.workflow_status != "Draft":
            return {
                "status": "error",
                "message": "Only draft workflows can be activated"
            }
        
        self.workflow_status = "Active"
        self.activation_date = now()
        self.activated_by = frappe.session.user
        
        # Log activation
        frappe.get_doc({
            "doctype": "Workflow Activation",
            "workflow": self.name,
            "activated_by": frappe.session.user,
            "activation_date": now()
        }).insert(ignore_permissions=True)
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Workflow activated successfully"
        }

    @frappe.whitelist()
    def deactivate_workflow(self):
        """Deactivate workflow"""
        if self.workflow_status != "Active":
            return {
                "status": "error",
                "message": "Only active workflows can be deactivated"
            }
        
        self.workflow_status = "Inactive"
        self.deactivation_date = now()
        self.deactivated_by = frappe.session.user
        
        # Log deactivation
        frappe.get_doc({
            "doctype": "Workflow Deactivation",
            "workflow": self.name,
            "deactivated_by": frappe.session.user,
            "deactivation_date": now()
        }).insert(ignore_permissions=True)
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Workflow deactivated successfully"
        }

    @frappe.whitelist()
    def get_workflow_insights(self):
        """Get workflow insights"""
        return {
            "workflow_complexity": self.workflow_complexity,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
