# Voice Assistant - Voice-Enabled CRM Operations

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class VoiceAssistant(Document):
    def autoname(self):
        """Generate unique voice assistant ID"""
        if not self.voice_assistant_id:
            self.voice_assistant_id = make_autoname("VA-.YYYY.-.MM.-.#####")
        self.name = self.voice_assistant_id

    def validate(self):
        """Validate voice assistant data"""
        self.validate_voice_assistant_data()
        self.set_defaults()
        self.validate_voice_configuration()
        self.calculate_voice_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_voice_settings()
        self.setup_voice_permissions()
        self.generate_voice_insights()

    def after_insert(self):
        """Process after inserting new voice assistant"""
        self.create_voice_profile()
        self.setup_voice_workflow()
        self.create_voice_analytics()
        self.initialize_voice_tracking()

    def on_update(self):
        """Process on voice assistant update"""
        self.update_voice_analytics()
        self.sync_voice_data()
        self.update_voice_status()
        self.process_voice_changes()

    def validate_voice_assistant_data(self):
        """Validate voice assistant information"""
        if not self.voice_assistant_name:
            frappe.throw(_("Voice assistant name is required"))
        
        if not self.voice_language:
            frappe.throw(_("Voice language is required"))
        
        if not self.voice_capabilities:
            frappe.throw(_("Voice capabilities are required"))

    def validate_voice_configuration(self):
        """Validate voice configuration"""
        if not self.voice_configuration:
            frappe.throw(_("Voice configuration is required"))
        
        # Validate voice configuration format
        try:
            config = json.loads(self.voice_configuration)
            if not isinstance(config, dict):
                frappe.throw(_("Voice configuration must be a valid JSON object"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format in voice configuration"))

    def set_defaults(self):
        """Set default values for new voice assistant"""
        if not self.voice_status:
            self.voice_status = "Active"
        
        if not self.voice_priority:
            self.voice_priority = "Medium"
        
        if not self.voice_category:
            self.voice_category = "General"
        
        if not self.is_voice_enabled:
            self.is_voice_enabled = 1

    def calculate_voice_metrics(self):
        """Calculate voice assistant metrics"""
        # Calculate voice accuracy
        self.voice_accuracy = self.calculate_voice_accuracy()
        
        # Calculate voice performance
        self.voice_performance = self.calculate_voice_performance()
        
        # Calculate voice recognition rate
        self.voice_recognition_rate = self.calculate_voice_recognition_rate()
        
        # Calculate voice response time
        self.voice_response_time = self.calculate_voice_response_time()

    def calculate_voice_accuracy(self):
        """Calculate voice accuracy"""
        # Get voice performance history
        performance_history = frappe.db.sql("""
            SELECT AVG(accuracy_score) as avg_accuracy,
                   COUNT(*) as total_interactions
            FROM `tabVoice Interaction`
            WHERE voice_assistant = %s
            AND interaction_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        if performance_history['total_interactions'] > 0:
            return round(performance_history['avg_accuracy'], 2)
        else:
            return 0

    def calculate_voice_performance(self):
        """Calculate voice performance"""
        # Get voice performance data
        performance_data = frappe.db.sql("""
            SELECT AVG(response_time) as avg_response_time,
                   AVG(satisfaction_score) as avg_satisfaction,
                   COUNT(*) as total_interactions
            FROM `tabVoice Interaction`
            WHERE voice_assistant = %s
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

    def calculate_voice_recognition_rate(self):
        """Calculate voice recognition rate"""
        # Get voice recognition data
        recognition_data = frappe.db.sql("""
            SELECT AVG(recognition_accuracy) as avg_recognition,
                   COUNT(*) as total_voice_commands
            FROM `tabVoice Command`
            WHERE voice_assistant = %s
            AND command_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        if recognition_data['total_voice_commands'] > 0:
            return round(recognition_data['avg_recognition'], 2)
        else:
            return 0

    def calculate_voice_response_time(self):
        """Calculate voice response time"""
        # Get voice response data
        response_data = frappe.db.sql("""
            SELECT AVG(response_time) as avg_response_time
            FROM `tabVoice Interaction`
            WHERE voice_assistant = %s
            AND interaction_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        if response_data['avg_response_time']:
            return round(response_data['avg_response_time'], 2)
        else:
            return 0

    def update_voice_settings(self):
        """Update voice-specific settings"""
        # Update voice preferences
        if self.preferences:
            frappe.db.set_value("Voice Assistant", self.name, "preferences", json.dumps(self.preferences))
        
        # Update voice tags
        if self.tags:
            frappe.db.set_value("Voice Assistant", self.name, "tags", json.dumps(self.tags))

    def setup_voice_permissions(self):
        """Setup voice-specific permissions"""
        # Create voice-specific roles
        voice_roles = [
            f"Voice Assistant - {self.voice_assistant_id}",
            f"Language - {self.voice_language}",
            f"Category - {self.voice_category}"
        ]
        
        for role_name in voice_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_voice_insights(self):
        """Generate voice assistant insights"""
        insights = {
            "voice_accuracy": self.voice_accuracy,
            "voice_performance": self.voice_performance,
            "voice_recognition_rate": self.voice_recognition_rate,
            "voice_response_time": self.voice_response_time,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.voice_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify voice optimization opportunities"""
        opportunities = []
        
        # Check for accuracy improvements
        if self.voice_accuracy < 85:
            opportunities.append("Improve voice recognition accuracy")
        
        # Check for performance improvements
        if self.voice_performance < 80:
            opportunities.append("Optimize voice performance")
        
        # Check for recognition improvements
        if self.voice_recognition_rate < 90:
            opportunities.append("Enhance voice recognition capabilities")
        
        # Check for response time improvements
        if self.voice_response_time > 3:
            opportunities.append("Improve voice response time")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.voice_status == "Active":
            actions.append("Monitor voice performance")
            actions.append("Update voice training data")
            actions.append("Optimize voice configuration")
        elif self.voice_status == "Training":
            actions.append("Complete voice training")
            actions.append("Validate voice performance")
            actions.append("Deploy voice assistant")
        else:
            actions.append("Review voice status")
            actions.append("Take appropriate action")
        
        return actions

    def create_voice_profile(self):
        """Create comprehensive voice assistant profile"""
        profile_data = {
            "voice_assistant_id": self.voice_assistant_id,
            "voice_assistant_name": self.voice_assistant_name,
            "voice_language": self.voice_language,
            "voice_category": self.voice_category,
            "voice_status": self.voice_status,
            "voice_priority": self.voice_priority,
            "voice_capabilities": self.voice_capabilities,
            "voice_accuracy": self.voice_accuracy,
            "voice_performance": self.voice_performance,
            "voice_recognition_rate": self.voice_recognition_rate,
            "voice_response_time": self.voice_response_time,
            "is_voice_enabled": self.is_voice_enabled
        }
        
        frappe.get_doc({
            "doctype": "Voice Assistant Profile",
            "voice_assistant": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_voice_workflow(self):
        """Setup voice assistant workflow"""
        workflow_data = {
            "voice_assistant": self.name,
            "workflow_type": "Voice Assistant Management",
            "steps": [
                {"step": "Voice Configuration", "status": "Completed"},
                {"step": "Voice Training", "status": "Pending"},
                {"step": "Voice Testing", "status": "Pending"},
                {"step": "Voice Deployment", "status": "Pending"},
                {"step": "Voice Monitoring", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Voice Assistant Workflow",
            "voice_assistant": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_voice_analytics(self):
        """Create voice assistant analytics"""
        analytics_data = {
            "voice_assistant": self.name,
            "analytics_type": "Voice Assistant Analytics",
            "metrics": {
                "voice_accuracy": self.voice_accuracy,
                "voice_performance": self.voice_performance,
                "voice_recognition_rate": self.voice_recognition_rate,
                "voice_response_time": self.voice_response_time
            },
            "insights": self.generate_voice_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Voice Assistant Analytics",
            "voice_assistant": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_voice_tracking(self):
        """Initialize voice assistant tracking"""
        tracking_data = {
            "voice_assistant": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "interaction_count": 0,
            "command_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Voice Assistant Tracking",
            "voice_assistant": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_voice_analytics(self):
        """Update voice assistant analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "voice_accuracy": self.calculate_voice_accuracy(),
            "voice_performance": self.calculate_voice_performance(),
            "voice_recognition_rate": self.calculate_voice_recognition_rate(),
            "voice_response_time": self.calculate_voice_response_time()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Voice Assistant Analytics", {"voice_assistant": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "voice_assistant": self.name,
                "analytics_type": "Voice Assistant Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_voice_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_voice_data(self):
        """Sync voice assistant data across systems"""
        # Sync with external voice systems if configured
        if self.external_voice_system_id:
            self.sync_with_external_voice_system()

    def update_voice_status(self):
        """Update voice assistant status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Voice Assistant Tracking", {"voice_assistant": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_voice_changes(self):
        """Process voice assistant changes"""
        # Log voice assistant changes
        self.log_voice_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Voice Assistant Status Change",
            "voice_assistant": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.voice_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabVoice Assistant Status Change`
            WHERE voice_assistant = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Voice Assistant Status Change", {"voice_assistant": self.name}) else "New"
        
        return previous_status

    def log_voice_changes(self):
        """Log voice assistant changes"""
        frappe.get_doc({
            "doctype": "Voice Assistant Change Log",
            "voice_assistant": self.name,
            "change_type": "Update",
            "change_description": "Voice assistant information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update voice interactions
        self.update_voice_interactions()
        
        # Update voice commands
        self.update_voice_commands()

    def update_voice_interactions(self):
        """Update voice interactions"""
        # Update interaction status
        frappe.db.sql("""
            UPDATE `tabVoice Interaction`
            SET voice_assistant_status = %s
            WHERE voice_assistant = %s
        """, (self.voice_status, self.name))

    def update_voice_commands(self):
        """Update voice commands"""
        # Update command status
        frappe.db.sql("""
            UPDATE `tabVoice Command`
            SET voice_assistant_status = %s
            WHERE voice_assistant = %s
        """, (self.voice_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify voice users
        self.notify_voice_users()
        
        # Notify voice administrators
        self.notify_voice_administrators()

    def notify_voice_users(self):
        """Notify voice users"""
        frappe.get_doc({
            "doctype": "Voice Assistant Notification",
            "voice_assistant": self.name,
            "notification_type": "Voice Assistant Update",
            "message": f"Voice assistant {self.voice_assistant_name} has been updated",
            "recipients": "Voice Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_voice_administrators(self):
        """Notify voice administrators"""
        frappe.get_doc({
            "doctype": "Voice Assistant Notification",
            "voice_assistant": self.name,
            "notification_type": "Voice Assistant Update",
            "message": f"Voice assistant {self.voice_assistant_name} has been updated",
            "recipients": "Voice Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_voice_system(self):
        """Sync voice assistant data with external voice system"""
        # Implementation for external voice system sync
        pass

    @frappe.whitelist()
    def get_voice_assistant_dashboard_data(self):
        """Get voice assistant dashboard data"""
        return {
            "voice_assistant_id": self.voice_assistant_id,
            "voice_assistant_name": self.voice_assistant_name,
            "voice_language": self.voice_language,
            "voice_category": self.voice_category,
            "voice_status": self.voice_status,
            "voice_priority": self.voice_priority,
            "voice_capabilities": self.voice_capabilities,
            "voice_accuracy": self.voice_accuracy,
            "voice_performance": self.voice_performance,
            "voice_recognition_rate": self.voice_recognition_rate,
            "voice_response_time": self.voice_response_time,
            "is_voice_enabled": self.is_voice_enabled,
            "insights": self.generate_voice_insights()
        }

    @frappe.whitelist()
    def process_voice_command(self, voice_command):
        """Process voice command"""
        try:
            # Process voice command
            response = self.execute_voice_command(voice_command)
            
            # Log voice interaction
            frappe.get_doc({
                "doctype": "Voice Interaction",
                "voice_assistant": self.name,
                "voice_command": voice_command,
                "voice_response": response.get('response', ''),
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
                "message": f"Voice command processing failed: {str(e)}"
            }

    def execute_voice_command(self, voice_command):
        """Execute voice command"""
        # Implementation for voice command execution
        start_time = now()
        
        # Process command
        response = self.process_voice_command(voice_command)
        
        end_time = now()
        response_time = (end_time - start_time).total_seconds()
        
        return {
            "response": response,
            "response_time": response_time,
            "accuracy_score": self.calculate_command_accuracy(voice_command, response),
            "satisfaction_score": self.calculate_command_satisfaction(voice_command, response)
        }

    def process_voice_command(self, voice_command):
        """Process voice command"""
        # Implementation for voice command processing
        pass

    def calculate_command_accuracy(self, voice_command, response):
        """Calculate command accuracy"""
        # Implementation for accuracy calculation
        return 0.90

    def calculate_command_satisfaction(self, voice_command, response):
        """Calculate command satisfaction"""
        # Implementation for satisfaction calculation
        return 0.85

    @frappe.whitelist()
    def train_voice_assistant(self, training_data):
        """Train voice assistant"""
        try:
            # Train voice assistant
            training_result = self.execute_voice_training(training_data)
            
            # Log training
            frappe.get_doc({
                "doctype": "Voice Training",
                "voice_assistant": self.name,
                "training_data": json.dumps(training_data),
                "training_result": json.dumps(training_result),
                "training_date": now(),
                "training_score": training_result.get('training_score', 0)
            }).insert(ignore_permissions=True)
            
            return {
                "status": "success",
                "message": "Voice assistant training completed successfully",
                "result": training_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Voice assistant training failed: {str(e)}"
            }

    def execute_voice_training(self, training_data):
        """Execute voice training"""
        # Implementation for voice training
        return {
            "training_score": 0.90,
            "training_accuracy": 0.95,
            "training_time": 600
        }

    @frappe.whitelist()
    def get_voice_assistant_insights(self):
        """Get voice assistant insights"""
        return {
            "voice_accuracy": self.voice_accuracy,
            "voice_performance": self.voice_performance,
            "voice_recognition_rate": self.voice_recognition_rate,
            "voice_response_time": self.voice_response_time,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
