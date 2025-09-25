# Bulk Operations System - Advanced Bulk Management

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class BulkOperations(Document):
    def autoname(self):
        """Generate unique bulk operation ID"""
        if not self.bulk_operation_id:
            self.bulk_operation_id = make_autoname("BULK-.YYYY.-.MM.-.#####")
        self.name = self.bulk_operation_id

    def validate(self):
        """Validate bulk operation data"""
        self.validate_bulk_operation_data()
        self.set_defaults()
        self.validate_operation_parameters()
        self.calculate_bulk_operation_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_bulk_operation_settings()
        self.setup_bulk_operation_permissions()
        self.generate_bulk_operation_insights()

    def after_insert(self):
        """Process after inserting new bulk operation"""
        self.create_bulk_operation_profile()
        self.setup_bulk_operation_workflow()
        self.create_bulk_operation_analytics()
        self.initialize_bulk_operation_tracking()

    def on_update(self):
        """Process on bulk operation update"""
        self.update_bulk_operation_analytics()
        self.sync_bulk_operation_data()
        self.update_bulk_operation_status()
        self.process_bulk_operation_changes()

    def validate_bulk_operation_data(self):
        """Validate bulk operation information"""
        if not self.bulk_operation_name:
            frappe.throw(_("Bulk operation name is required"))
        
        if not self.operation_type:
            frappe.throw(_("Operation type is required"))
        
        if not self.target_doctype:
            frappe.throw(_("Target doctype is required"))

    def validate_operation_parameters(self):
        """Validate operation parameters"""
        if not self.operation_parameters:
            frappe.throw(_("Operation parameters are required"))
        
        # Validate operation parameters format
        try:
            parameters = json.loads(self.operation_parameters)
            if not isinstance(parameters, dict):
                frappe.throw(_("Operation parameters must be a valid JSON object"))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format in operation parameters"))

    def set_defaults(self):
        """Set default values for new bulk operation"""
        if not self.bulk_operation_status:
            self.bulk_operation_status = "Pending"
        
        if not self.bulk_operation_priority:
            self.bulk_operation_priority = "Medium"
        
        if not self.bulk_operation_category:
            self.bulk_operation_category = "General"
        
        if not self.is_scheduled:
            self.is_scheduled = 0

    def calculate_bulk_operation_metrics(self):
        """Calculate bulk operation metrics"""
        # Calculate record count
        self.record_count = self.calculate_record_count()
        
        # Calculate estimated duration
        self.estimated_duration = self.calculate_estimated_duration()
        
        # Calculate success rate
        self.success_rate = self.calculate_success_rate()
        
        # Calculate efficiency score
        self.efficiency_score = self.calculate_efficiency_score()

    def calculate_record_count(self):
        """Calculate record count"""
        if self.filter_conditions:
            # Get count based on filter conditions
            count = frappe.db.sql("""
                SELECT COUNT(*) as record_count
                FROM `tab{0}`
                WHERE {1}
            """.format(self.target_doctype, self.filter_conditions))[0][0]
            return count
        else:
            # Get total count
            count = frappe.db.sql("""
                SELECT COUNT(*) as record_count
                FROM `tab{0}`
            """.format(self.target_doctype))[0][0]
            return count

    def calculate_estimated_duration(self):
        """Calculate estimated duration"""
        # Base duration calculation
        base_duration = 2  # 2 minutes base
        
        # Add duration based on record count
        if self.record_count:
            record_duration = self.record_count / 100  # 1 second per 100 records
            base_duration += record_duration
        
        # Add duration based on operation complexity
        complexity_duration = {
            "Simple": 0,
            "Medium": 5,
            "Complex": 15
        }
        
        complexity = self.calculate_complexity()
        base_duration += complexity_duration.get(complexity, 0)
        
        return base_duration

    def calculate_complexity(self):
        """Calculate bulk operation complexity"""
        complexity_factors = {
            'operation_type': self.get_operation_type_complexity(),
            'record_count': self.get_record_count_complexity(),
            'operation_parameters': self.get_parameters_complexity(),
            'target_doctype': self.get_doctype_complexity()
        }
        
        # Calculate complexity score
        complexity_score = (
            complexity_factors['operation_type'] * 0.3 +
            complexity_factors['record_count'] * 0.3 +
            complexity_factors['operation_parameters'] * 0.2 +
            complexity_factors['target_doctype'] * 0.2
        )
        
        if complexity_score <= 3:
            return "Simple"
        elif complexity_score <= 6:
            return "Medium"
        else:
            return "Complex"

    def get_operation_type_complexity(self):
        """Get operation type complexity"""
        type_complexity = {
            "Update": 2,
            "Delete": 3,
            "Create": 1,
            "Assign": 2,
            "Status Change": 1,
            "Bulk Edit": 4,
            "Bulk Delete": 5,
            "Bulk Create": 3
        }
        
        return type_complexity.get(self.operation_type, 2)

    def get_record_count_complexity(self):
        """Get record count complexity"""
        if self.record_count:
            if self.record_count > 10000:
                return 5
            elif self.record_count > 1000:
                return 3
            elif self.record_count > 100:
                return 2
            else:
                return 1
        else:
            return 1

    def get_parameters_complexity(self):
        """Get parameters complexity"""
        if self.operation_parameters:
            parameters = json.loads(self.operation_parameters)
            parameter_count = len(parameters)
            
            if parameter_count > 10:
                return 5
            elif parameter_count > 5:
                return 3
            elif parameter_count > 2:
                return 2
            else:
                return 1
        else:
            return 1

    def get_doctype_complexity(self):
        """Get doctype complexity"""
        # Get doctype complexity based on field count
        field_count = frappe.db.sql("""
            SELECT COUNT(*) as field_count
            FROM `tabDocField`
            WHERE parent = %s
        """, self.target_doctype)[0][0]
        
        if field_count > 50:
            return 5
        elif field_count > 20:
            return 3
        elif field_count > 10:
            return 2
        else:
            return 1

    def calculate_success_rate(self):
        """Calculate bulk operation success rate"""
        # Get bulk operation history
        history = frappe.db.sql("""
            SELECT COUNT(*) as total_operations,
                   SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as successful_operations
            FROM `tabBulk Operation History`
            WHERE bulk_operation = %s
            AND operation_date >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, self.name, as_dict=True)[0]
        
        if history['total_operations'] > 0:
            success_rate = (history['successful_operations'] / history['total_operations']) * 100
            return round(success_rate, 2)
        else:
            return 0

    def calculate_efficiency_score(self):
        """Calculate bulk operation efficiency score"""
        # Get performance data
        performance_data = frappe.db.sql("""
            SELECT AVG(execution_time) as avg_execution_time,
                   AVG(record_count) as avg_record_count
            FROM `tabBulk Operation History`
            WHERE bulk_operation = %s
            AND operation_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        # Calculate efficiency based on execution time and record count
        if performance_data['avg_execution_time'] and performance_data['avg_record_count']:
            efficiency = (performance_data['avg_record_count'] / performance_data['avg_execution_time']) * 100
            return min(efficiency, 100)
        else:
            return 0

    def update_bulk_operation_settings(self):
        """Update bulk operation-specific settings"""
        # Update bulk operation preferences
        if self.preferences:
            frappe.db.set_value("Bulk Operations", self.name, "preferences", json.dumps(self.preferences))
        
        # Update bulk operation tags
        if self.tags:
            frappe.db.set_value("Bulk Operations", self.name, "tags", json.dumps(self.tags))

    def setup_bulk_operation_permissions(self):
        """Setup bulk operation-specific permissions"""
        # Create bulk operation-specific roles
        bulk_operation_roles = [
            f"Bulk Operation - {self.bulk_operation_id}",
            f"Type - {self.operation_type}",
            f"Category - {self.bulk_operation_category}"
        ]
        
        for role_name in bulk_operation_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_bulk_operation_insights(self):
        """Generate bulk operation insights"""
        insights = {
            "record_count": self.record_count,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.bulk_operation_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify bulk operation optimization opportunities"""
        opportunities = []
        
        # Check for performance bottlenecks
        bottlenecks = self.identify_performance_bottlenecks()
        if bottlenecks:
            opportunities.append("Address performance bottlenecks")
        
        # Check for automation opportunities
        automation_opportunities = self.identify_automation_opportunities()
        if automation_opportunities:
            opportunities.append("Implement automation")
        
        # Check for operation optimization
        operation_optimization = self.identify_operation_optimization()
        if operation_optimization:
            opportunities.append("Optimize operation parameters")
        
        return opportunities

    def identify_performance_bottlenecks(self):
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Check for slow operations
        slow_operations = frappe.db.sql("""
            SELECT operation_type, AVG(execution_time) as avg_execution_time
            FROM `tabBulk Operation History`
            WHERE bulk_operation = %s
            AND execution_time > %s
            GROUP BY operation_type
        """, (self.name, 300), as_dict=True)  # Operations taking more than 5 minutes
        
        if slow_operations:
            bottlenecks.append("Slow operations identified")
        
        # Check for large record counts
        if self.record_count > 5000:
            bottlenecks.append("Large record count may cause performance issues")
        
        return bottlenecks

    def identify_automation_opportunities(self):
        """Identify automation opportunities"""
        opportunities = []
        
        # Check for repetitive operations
        repetitive_operations = frappe.db.sql("""
            SELECT operation_type, COUNT(*) as operation_count
            FROM `tabBulk Operation History`
            WHERE bulk_operation = %s
            AND operation_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY operation_type
            HAVING operation_count > 5
        """, self.name, as_dict=True)
        
        if repetitive_operations:
            opportunities.append("High-frequency operations can be automated")
        
        # Check for scheduled operations
        if self.is_scheduled:
            opportunities.append("Scheduled operations can be optimized")
        
        return opportunities

    def identify_operation_optimization(self):
        """Identify operation optimization opportunities"""
        opportunities = []
        
        # Check for operation parameters
        if self.operation_parameters:
            parameters = json.loads(self.operation_parameters)
            if len(parameters) > 10:
                opportunities.append("Consider simplifying operation parameters")
        
        # Check for filter conditions
        if self.filter_conditions and len(self.filter_conditions) > 200:
            opportunities.append("Consider optimizing filter conditions")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.bulk_operation_status == "Pending":
            actions.append("Review bulk operation configuration")
            actions.append("Validate operation parameters")
            actions.append("Execute bulk operation")
        elif self.bulk_operation_status == "In Progress":
            actions.append("Monitor progress")
            actions.append("Address any issues")
            actions.append("Validate results")
        elif self.bulk_operation_status == "Completed":
            actions.append("Review results")
            actions.append("Validate data integrity")
            actions.append("Update related records")
        elif self.bulk_operation_status == "Failed":
            actions.append("Review error logs")
            actions.append("Fix issues")
            actions.append("Retry operation")
        else:
            actions.append("Review bulk operation status")
            actions.append("Take appropriate action")
        
        return actions

    def create_bulk_operation_profile(self):
        """Create comprehensive bulk operation profile"""
        profile_data = {
            "bulk_operation_id": self.bulk_operation_id,
            "bulk_operation_name": self.bulk_operation_name,
            "operation_type": self.operation_type,
            "target_doctype": self.target_doctype,
            "bulk_operation_status": self.bulk_operation_status,
            "bulk_operation_priority": self.bulk_operation_priority,
            "bulk_operation_category": self.bulk_operation_category,
            "record_count": self.record_count,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "is_scheduled": self.is_scheduled
        }
        
        frappe.get_doc({
            "doctype": "Bulk Operation Profile",
            "bulk_operation": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_bulk_operation_workflow(self):
        """Setup bulk operation workflow"""
        workflow_data = {
            "bulk_operation": self.name,
            "workflow_type": "Bulk Operation Management",
            "steps": [
                {"step": "Configuration", "status": "Completed"},
                {"step": "Validation", "status": "Pending"},
                {"step": "Execution", "status": "Pending"},
                {"step": "Verification", "status": "Pending"},
                {"step": "Completion", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Bulk Operation Workflow",
            "bulk_operation": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_bulk_operation_analytics(self):
        """Create bulk operation analytics"""
        analytics_data = {
            "bulk_operation": self.name,
            "analytics_type": "Bulk Operation Analytics",
            "metrics": {
                "record_count": self.record_count,
                "estimated_duration": self.estimated_duration,
                "success_rate": self.success_rate,
                "efficiency_score": self.efficiency_score
            },
            "insights": self.generate_bulk_operation_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Bulk Operation Analytics",
            "bulk_operation": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_bulk_operation_tracking(self):
        """Initialize bulk operation tracking"""
        tracking_data = {
            "bulk_operation": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "operation_count": 0,
            "success_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Bulk Operation Tracking",
            "bulk_operation": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_bulk_operation_analytics(self):
        """Update bulk operation analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "record_count": self.record_count,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.calculate_success_rate(),
            "efficiency_score": self.calculate_efficiency_score()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Bulk Operation Analytics", {"bulk_operation": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "bulk_operation": self.name,
                "analytics_type": "Bulk Operation Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_bulk_operation_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_bulk_operation_data(self):
        """Sync bulk operation data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_bulk_operation_status(self):
        """Update bulk operation status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Bulk Operation Tracking", {"bulk_operation": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_bulk_operation_changes(self):
        """Process bulk operation changes"""
        # Log bulk operation changes
        self.log_bulk_operation_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Bulk Operation Status Change",
            "bulk_operation": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.bulk_operation_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabBulk Operation Status Change`
            WHERE bulk_operation = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Bulk Operation Status Change", {"bulk_operation": self.name}) else "New"
        
        return previous_status

    def log_bulk_operation_changes(self):
        """Log bulk operation changes"""
        frappe.get_doc({
            "doctype": "Bulk Operation Change Log",
            "bulk_operation": self.name,
            "change_type": "Update",
            "change_description": "Bulk operation information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update bulk operation history
        self.update_bulk_operation_history()
        
        # Update bulk operation logs
        self.update_bulk_operation_logs()

    def update_bulk_operation_history(self):
        """Update bulk operation history"""
        # Update history status
        frappe.db.sql("""
            UPDATE `tabBulk Operation History`
            SET bulk_operation_status = %s
            WHERE bulk_operation = %s
        """, (self.bulk_operation_status, self.name))

    def update_bulk_operation_logs(self):
        """Update bulk operation logs"""
        # Update log status
        frappe.db.sql("""
            UPDATE `tabBulk Operation Log`
            SET bulk_operation_status = %s
            WHERE bulk_operation = %s
        """, (self.bulk_operation_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify bulk operation users
        self.notify_bulk_operation_users()
        
        # Notify data administrators
        self.notify_data_administrators()

    def notify_bulk_operation_users(self):
        """Notify bulk operation users"""
        frappe.get_doc({
            "doctype": "Bulk Operation Notification",
            "bulk_operation": self.name,
            "notification_type": "Bulk Operation Update",
            "message": f"Bulk operation {self.bulk_operation_name} has been updated",
            "recipients": "Bulk Operation Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_data_administrators(self):
        """Notify data administrators"""
        frappe.get_doc({
            "doctype": "Bulk Operation Notification",
            "bulk_operation": self.name,
            "notification_type": "Bulk Operation Update",
            "message": f"Bulk operation {self.bulk_operation_name} has been updated",
            "recipients": "Data Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync bulk operation data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_bulk_operation_dashboard_data(self):
        """Get bulk operation dashboard data"""
        return {
            "bulk_operation_id": self.bulk_operation_id,
            "bulk_operation_name": self.bulk_operation_name,
            "operation_type": self.operation_type,
            "target_doctype": self.target_doctype,
            "bulk_operation_status": self.bulk_operation_status,
            "bulk_operation_priority": self.bulk_operation_priority,
            "bulk_operation_category": self.bulk_operation_category,
            "record_count": self.record_count,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "is_scheduled": self.is_scheduled,
            "insights": self.generate_bulk_operation_insights()
        }

    @frappe.whitelist()
    def execute_bulk_operation(self):
        """Execute bulk operation"""
        if self.bulk_operation_status != "Pending":
            return {
                "status": "error",
                "message": "Only pending operations can be executed"
            }
        
        try:
            # Update status
            self.bulk_operation_status = "In Progress"
            self.start_date = now()
            self.started_by = frappe.session.user
            
            # Save changes
            self.save()
            
            # Execute operation
            result = self.execute_operation()
            
            # Update status
            self.bulk_operation_status = "Completed"
            self.completion_date = now()
            self.completed_by = frappe.session.user
            
            # Log completion
            frappe.get_doc({
                "doctype": "Bulk Operation History",
                "bulk_operation": self.name,
                "operation_type": self.operation_type,
                "operation_date": now(),
                "status": "Completed",
                "execution_time": result.get('execution_time', 0),
                "records_processed": result.get('records_processed', 0)
            }).insert(ignore_permissions=True)
            
            # Save changes
            self.save()
            
            return {
                "status": "success",
                "message": "Bulk operation completed successfully",
                "result": result
            }
            
        except Exception as e:
            # Update status
            self.bulk_operation_status = "Failed"
            self.failure_date = now()
            self.failure_reason = str(e)
            
            # Log failure
            frappe.get_doc({
                "doctype": "Bulk Operation History",
                "bulk_operation": self.name,
                "operation_type": self.operation_type,
                "operation_date": now(),
                "status": "Failed",
                "error_message": str(e)
            }).insert(ignore_permissions=True)
            
            # Save changes
            self.save()
            
            return {
                "status": "error",
                "message": "Bulk operation failed",
                "error": str(e)
            }

    def execute_operation(self):
        """Execute bulk operation"""
        start_time = now()
        
        # Get records to process
        records = self.get_records_to_process()
        
        # Process records
        processed_count = 0
        failed_count = 0
        
        for record in records:
            try:
                self.process_record(record)
                processed_count += 1
            except Exception as e:
                failed_count += 1
                self.log_record_error(record, str(e))
        
        end_time = now()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            "execution_time": execution_time,
            "records_processed": processed_count,
            "records_failed": failed_count
        }

    def get_records_to_process(self):
        """Get records to process"""
        if self.filter_conditions:
            records = frappe.db.sql("""
                SELECT name
                FROM `tab{0}`
                WHERE {1}
            """.format(self.target_doctype, self.filter_conditions), as_dict=True)
        else:
            records = frappe.db.sql("""
                SELECT name
                FROM `tab{0}`
            """.format(self.target_doctype), as_dict=True)
        
        return records

    def process_record(self, record):
        """Process individual record"""
        if self.operation_type == "Update":
            self.update_record(record)
        elif self.operation_type == "Delete":
            self.delete_record(record)
        elif self.operation_type == "Assign":
            self.assign_record(record)
        elif self.operation_type == "Status Change":
            self.change_record_status(record)
        elif self.operation_type == "Bulk Edit":
            self.bulk_edit_record(record)
        elif self.operation_type == "Bulk Delete":
            self.bulk_delete_record(record)
        elif self.operation_type == "Bulk Create":
            self.bulk_create_record(record)

    def update_record(self, record):
        """Update record"""
        # Implementation for updating record
        pass

    def delete_record(self, record):
        """Delete record"""
        # Implementation for deleting record
        pass

    def assign_record(self, record):
        """Assign record"""
        # Implementation for assigning record
        pass

    def change_record_status(self, record):
        """Change record status"""
        # Implementation for changing record status
        pass

    def bulk_edit_record(self, record):
        """Bulk edit record"""
        # Implementation for bulk editing record
        pass

    def bulk_delete_record(self, record):
        """Bulk delete record"""
        # Implementation for bulk deleting record
        pass

    def bulk_create_record(self, record):
        """Bulk create record"""
        # Implementation for bulk creating record
        pass

    def log_record_error(self, record, error_message):
        """Log record error"""
        frappe.get_doc({
            "doctype": "Bulk Operation Error",
            "bulk_operation": self.name,
            "record_id": record.name,
            "error_message": error_message,
            "error_date": now()
        }).insert(ignore_permissions=True)

    @frappe.whitelist()
    def get_bulk_operation_insights(self):
        """Get bulk operation insights"""
        return {
            "record_count": self.record_count,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
