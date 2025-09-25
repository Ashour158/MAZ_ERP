# AI Assistant - Intelligent CRM Assistant

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class AIAssistant(Document):
    def autoname(self):
        """Generate unique AI assistant ID"""
        if not self.ai_assistant_id:
            self.ai_assistant_id = make_autoname("AI-.YYYY.-.MM.-.#####")
        self.name = self.ai_assistant_id

    def validate(self):
        """Validate AI assistant data"""
        self.validate_ai_assistant_data()
        self.set_defaults()
        self.validate_ai_configuration()
        self.calculate_ai_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_ai_settings()
        self.setup_ai_permissions()
        self.generate_ai_insights()

    def after_insert(self):
        """Process after inserting new AI assistant"""
        self.create_ai_profile()
        self.setup_ai_workflow()
        self.create_ai_analytics()
        self.initialize_ai_tracking()

    def on_update(self):
        """Process on AI assistant update"""
        self.update_ai_analytics()
        self.sync_ai_data()
        self.update_ai_status()
        self.process_ai_changes()

    def validate_ai_assistant_data(self):
        """Validate AI assistant information"""
        if not self.ai_assistant_name:
            frappe.throw(_("AI assistant name is required"))
        
        if not self.ai_type:
            frappe.throw(_("AI type is required"))
        
        if not self.ai_capabilities:
            frappe.throw(_("AI capabilities are required"))

    def validate_ai_configuration(self):
        """Validate AI configuration"""
        if not self.ai_configuration:
            frappe.throw(_("AI configuration is required"))
        
        # Validate AI configuration format
        try:
            config = json.loads(self.ai_configuration)
            if not isinstance(config, dict):
                frappe.throw(_("AI configuration must be a valid JSON object"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format in AI configuration"))

    def set_defaults(self):
        """Set default values for new AI assistant"""
        if not self.ai_status:
            self.ai_status = "Active"
        
        if not self.ai_priority:
            self.ai_priority = "Medium"
        
        if not self.ai_category:
            self.ai_category = "General"
        
        if not self.is_learning_enabled:
            self.is_learning_enabled = 1

    def calculate_ai_metrics(self):
        """Calculate AI assistant metrics"""
        # Calculate AI accuracy
        self.ai_accuracy = self.calculate_accuracy()
        
        # Calculate AI performance
        self.ai_performance = self.calculate_performance()
        
        # Calculate AI learning rate
        self.ai_learning_rate = self.calculate_learning_rate()
        
        # Calculate AI efficiency
        self.ai_efficiency = self.calculate_efficiency()

    def calculate_accuracy(self):
        """Calculate AI accuracy"""
        # Get AI performance history
        performance_history = frappe.db.sql("""
            SELECT AVG(accuracy_score) as avg_accuracy,
                   COUNT(*) as total_interactions
            FROM `tabAI Interaction`
            WHERE ai_assistant = %s
            AND interaction_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        if performance_history['total_interactions'] > 0:
            return round(performance_history['avg_accuracy'], 2)
        else:
            return 0

    def calculate_performance(self):
        """Calculate AI performance"""
        # Get AI performance data
        performance_data = frappe.db.sql("""
            SELECT AVG(response_time) as avg_response_time,
                   AVG(satisfaction_score) as avg_satisfaction,
                   COUNT(*) as total_interactions
            FROM `tabAI Interaction`
            WHERE ai_assistant = %s
            AND interaction_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        if performance_data['total_interactions'] > 0:
            # Calculate performance score based on response time and satisfaction
            response_score = max(0, 100 - (performance_data['avg_response_time'] / 10))
            satisfaction_score = performance_data['avg_satisfaction'] * 20
            performance = (response_score + satisfaction_score) / 2
            return min(performance, 100)
        else:
            return 0

    def calculate_learning_rate(self):
        """Calculate AI learning rate"""
        # Get learning data
        learning_data = frappe.db.sql("""
            SELECT AVG(learning_score) as avg_learning_score,
                   COUNT(*) as total_learning_events
            FROM `tabAI Learning`
            WHERE ai_assistant = %s
            AND learning_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        if learning_data['total_learning_events'] > 0:
            return round(learning_data['avg_learning_score'], 2)
        else:
            return 0

    def calculate_efficiency(self):
        """Calculate AI efficiency"""
        # Get efficiency data
        efficiency_data = frappe.db.sql("""
            SELECT AVG(task_completion_time) as avg_completion_time,
                   AVG(task_success_rate) as avg_success_rate,
                   COUNT(*) as total_tasks
            FROM `tabAI Task`
            WHERE ai_assistant = %s
            AND task_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        if efficiency_data['total_tasks'] > 0:
            # Calculate efficiency based on completion time and success rate
            time_score = max(0, 100 - (efficiency_data['avg_completion_time'] / 60))
            success_score = efficiency_data['avg_success_rate'] * 100
            efficiency = (time_score + success_score) / 2
            return min(efficiency, 100)
        else:
            return 0

    def update_ai_settings(self):
        """Update AI-specific settings"""
        # Update AI preferences
        if self.preferences:
            frappe.db.set_value("AI Assistant", self.name, "preferences", json.dumps(self.preferences))
        
        # Update AI tags
        if self.tags:
            frappe.db.set_value("AI Assistant", self.name, "tags", json.dumps(self.tags))

    def setup_ai_permissions(self):
        """Setup AI-specific permissions"""
        # Create AI-specific roles
        ai_roles = [
            f"AI Assistant - {self.ai_assistant_id}",
            f"Type - {self.ai_type}",
            f"Category - {self.ai_category}"
        ]
        
        for role_name in ai_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_ai_insights(self):
        """Generate AI assistant insights"""
        insights = {
            "ai_accuracy": self.ai_accuracy,
            "ai_performance": self.ai_performance,
            "ai_learning_rate": self.ai_learning_rate,
            "ai_efficiency": self.ai_efficiency,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.ai_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify AI optimization opportunities"""
        opportunities = []
        
        # Check for accuracy improvements
        if self.ai_accuracy < 80:
            opportunities.append("Improve AI accuracy through training")
        
        # Check for performance improvements
        if self.ai_performance < 80:
            opportunities.append("Optimize AI performance")
        
        # Check for learning improvements
        if self.ai_learning_rate < 70:
            opportunities.append("Enhance AI learning capabilities")
        
        # Check for efficiency improvements
        if self.ai_efficiency < 80:
            opportunities.append("Improve AI efficiency")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.ai_status == "Active":
            actions.append("Monitor AI performance")
            actions.append("Update AI training data")
            actions.append("Optimize AI configuration")
        elif self.ai_status == "Training":
            actions.append("Complete AI training")
            actions.append("Validate AI performance")
            actions.append("Deploy AI assistant")
        else:
            actions.append("Review AI status")
            actions.append("Take appropriate action")
        
        return actions

    def create_ai_profile(self):
        """Create comprehensive AI assistant profile"""
        profile_data = {
            "ai_assistant_id": self.ai_assistant_id,
            "ai_assistant_name": self.ai_assistant_name,
            "ai_type": self.ai_type,
            "ai_category": self.ai_category,
            "ai_status": self.ai_status,
            "ai_priority": self.ai_priority,
            "ai_capabilities": self.ai_capabilities,
            "ai_accuracy": self.ai_accuracy,
            "ai_performance": self.ai_performance,
            "ai_learning_rate": self.ai_learning_rate,
            "ai_efficiency": self.ai_efficiency,
            "is_learning_enabled": self.is_learning_enabled
        }
        
        frappe.get_doc({
            "doctype": "AI Assistant Profile",
            "ai_assistant": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_ai_workflow(self):
        """Setup AI assistant workflow"""
        workflow_data = {
            "ai_assistant": self.name,
            "workflow_type": "AI Assistant Management",
            "steps": [
                {"step": "AI Configuration", "status": "Completed"},
                {"step": "AI Training", "status": "Pending"},
                {"step": "AI Testing", "status": "Pending"},
                {"step": "AI Deployment", "status": "Pending"},
                {"step": "AI Monitoring", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "AI Assistant Workflow",
            "ai_assistant": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_ai_analytics(self):
        """Create AI assistant analytics"""
        analytics_data = {
            "ai_assistant": self.name,
            "analytics_type": "AI Assistant Analytics",
            "metrics": {
                "ai_accuracy": self.ai_accuracy,
                "ai_performance": self.ai_performance,
                "ai_learning_rate": self.ai_learning_rate,
                "ai_efficiency": self.ai_efficiency
            },
            "insights": self.generate_ai_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "AI Assistant Analytics",
            "ai_assistant": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_ai_tracking(self):
        """Initialize AI assistant tracking"""
        tracking_data = {
            "ai_assistant": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "interaction_count": 0,
            "learning_count": 0
        }
        
        frappe.get_doc({
            "doctype": "AI Assistant Tracking",
            "ai_assistant": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_ai_analytics(self):
        """Update AI assistant analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "ai_accuracy": self.calculate_accuracy(),
            "ai_performance": self.calculate_performance(),
            "ai_learning_rate": self.calculate_learning_rate(),
            "ai_efficiency": self.calculate_efficiency()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("AI Assistant Analytics", {"ai_assistant": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "ai_assistant": self.name,
                "analytics_type": "AI Assistant Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_ai_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_ai_data(self):
        """Sync AI assistant data across systems"""
        # Sync with external AI systems if configured
        if self.external_ai_system_id:
            self.sync_with_external_ai_system()

    def update_ai_status(self):
        """Update AI assistant status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("AI Assistant Tracking", {"ai_assistant": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_ai_changes(self):
        """Process AI assistant changes"""
        # Log AI assistant changes
        self.log_ai_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "AI Assistant Status Change",
            "ai_assistant": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.ai_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabAI Assistant Status Change`
            WHERE ai_assistant = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("AI Assistant Status Change", {"ai_assistant": self.name}) else "New"
        
        return previous_status

    def log_ai_changes(self):
        """Log AI assistant changes"""
        frappe.get_doc({
            "doctype": "AI Assistant Change Log",
            "ai_assistant": self.name,
            "change_type": "Update",
            "change_description": "AI assistant information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update AI interactions
        self.update_ai_interactions()
        
        # Update AI learning
        self.update_ai_learning()

    def update_ai_interactions(self):
        """Update AI interactions"""
        # Update interaction status
        frappe.db.sql("""
            UPDATE `tabAI Interaction`
            SET ai_assistant_status = %s
            WHERE ai_assistant = %s
        """, (self.ai_status, self.name))

    def update_ai_learning(self):
        """Update AI learning"""
        # Update learning status
        frappe.db.sql("""
            UPDATE `tabAI Learning`
            SET ai_assistant_status = %s
            WHERE ai_assistant = %s
        """, (self.ai_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify AI users
        self.notify_ai_users()
        
        # Notify AI administrators
        self.notify_ai_administrators()

    def notify_ai_users(self):
        """Notify AI users"""
        frappe.get_doc({
            "doctype": "AI Assistant Notification",
            "ai_assistant": self.name,
            "notification_type": "AI Assistant Update",
            "message": f"AI assistant {self.ai_assistant_name} has been updated",
            "recipients": "AI Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_ai_administrators(self):
        """Notify AI administrators"""
        frappe.get_doc({
            "doctype": "AI Assistant Notification",
            "ai_assistant": self.name,
            "notification_type": "AI Assistant Update",
            "message": f"AI assistant {self.ai_assistant_name} has been updated",
            "recipients": "AI Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_ai_system(self):
        """Sync AI assistant data with external AI system"""
        # Implementation for external AI system sync
        pass

    @frappe.whitelist()
    def get_ai_assistant_dashboard_data(self):
        """Get AI assistant dashboard data"""
        return {
            "ai_assistant_id": self.ai_assistant_id,
            "ai_assistant_name": self.ai_assistant_name,
            "ai_type": self.ai_type,
            "ai_category": self.ai_category,
            "ai_status": self.ai_status,
            "ai_priority": self.ai_priority,
            "ai_capabilities": self.ai_capabilities,
            "ai_accuracy": self.ai_accuracy,
            "ai_performance": self.ai_performance,
            "ai_learning_rate": self.ai_learning_rate,
            "ai_efficiency": self.ai_efficiency,
            "is_learning_enabled": self.is_learning_enabled,
            "insights": self.generate_ai_insights()
        }

    @frappe.whitelist()
    def process_ai_request(self, request_data):
        """Process AI request"""
        try:
            # Process AI request
            response = self.execute_ai_request(request_data)
            
            # Log interaction
            frappe.get_doc({
                "doctype": "AI Interaction",
                "ai_assistant": self.name,
                "request_data": json.dumps(request_data),
                "response_data": json.dumps(response),
                "interaction_date": now(),
                "response_time": response.get('response_time', 0),
                "accuracy_score": response.get('accuracy_score', 0),
                "satisfaction_score": response.get('satisfaction_score', 0)
            }).insert(ignore_permissions=True)
            
            return {
                "status": "success",
                "response": response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI request processing failed: {str(e)}"
            }

    def execute_ai_request(self, request_data):
        """Execute AI request"""
        # Implementation for AI request execution
        start_time = now()
        
        # Process request
        response = self.process_request(request_data)
        
        end_time = now()
        response_time = (end_time - start_time).total_seconds()
        
        return {
            "response": response,
            "response_time": response_time,
            "accuracy_score": self.calculate_request_accuracy(request_data, response),
            "satisfaction_score": self.calculate_request_satisfaction(request_data, response)
        }

    def process_request(self, request_data):
        """Process AI request"""
        # Implementation for request processing
        pass

    def calculate_request_accuracy(self, request_data, response):
        """Calculate request accuracy"""
        # Implementation for accuracy calculation
        return 0.85

    def calculate_request_satisfaction(self, request_data, response):
        """Calculate request satisfaction"""
        # Implementation for satisfaction calculation
        return 0.90

    @frappe.whitelist()
    def train_ai_assistant(self, training_data):
        """Train AI assistant"""
        try:
            # Train AI assistant
            training_result = self.execute_training(training_data)
            
            # Log training
            frappe.get_doc({
                "doctype": "AI Learning",
                "ai_assistant": self.name,
                "training_data": json.dumps(training_data),
                "training_result": json.dumps(training_result),
                "learning_date": now(),
                "learning_score": training_result.get('learning_score', 0)
            }).insert(ignore_permissions=True)
            
            return {
                "status": "success",
                "message": "AI assistant training completed successfully",
                "result": training_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI assistant training failed: {str(e)}"
            }

    def execute_training(self, training_data):
        """Execute AI training"""
        # Implementation for AI training
        return {
            "learning_score": 0.85,
            "training_accuracy": 0.90,
            "training_time": 300
        }

    @frappe.whitelist()
    def get_ai_assistant_insights(self):
        """Get AI assistant insights"""
        return {
            "ai_accuracy": self.ai_accuracy,
            "ai_performance": self.ai_performance,
            "ai_learning_rate": self.ai_learning_rate,
            "ai_efficiency": self.ai_efficiency,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
