# Data Import/Export System - Advanced Data Management

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
import csv
import pandas as pd
import io
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class DataImportExport(Document):
    def autoname(self):
        """Generate unique import/export ID"""
        if not self.import_export_id:
            self.import_export_id = make_autoname("IE-.YYYY.-.MM.-.#####")
        self.name = self.import_export_id

    def validate(self):
        """Validate import/export data"""
        self.validate_import_export_data()
        self.set_defaults()
        self.validate_file_format()
        self.calculate_import_export_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_import_export_settings()
        self.setup_import_export_permissions()
        self.generate_import_export_insights()

    def after_insert(self):
        """Process after inserting new import/export"""
        self.create_import_export_profile()
        self.setup_import_export_workflow()
        self.create_import_export_analytics()
        self.initialize_import_export_tracking()

    def on_update(self):
        """Process on import/export update"""
        self.update_import_export_analytics()
        self.sync_import_export_data()
        self.update_import_export_status()
        self.process_import_export_changes()

    def validate_import_export_data(self):
        """Validate import/export information"""
        if not self.import_export_name:
            frappe.throw(_("Import/Export name is required"))
        
        if not self.import_export_type:
            frappe.throw(_("Import/Export type is required"))
        
        if not self.data_source:
            frappe.throw(_("Data source is required"))

    def validate_file_format(self):
        """Validate file format"""
        if self.import_export_type == "Import":
            if not self.file_attachment:
                frappe.throw(_("File attachment is required for import"))
            
            # Validate file format
            if not self.file_attachment.endswith(('.csv', '.xlsx', '.xls', '.json')):
                frappe.throw(_("Only CSV, Excel, and JSON files are supported"))

    def set_defaults(self):
        """Set default values for new import/export"""
        if not self.import_export_status:
            self.import_export_status = "Pending"
        
        if not self.import_export_priority:
            self.import_export_priority = "Medium"
        
        if not self.import_export_category:
            self.import_export_category = "General"
        
        if not self.is_scheduled:
            self.is_scheduled = 0

    def calculate_import_export_metrics(self):
        """Calculate import/export metrics"""
        # Calculate data volume
        self.data_volume = self.calculate_data_volume()
        
        # Calculate estimated duration
        self.estimated_duration = self.calculate_estimated_duration()
        
        # Calculate success rate
        self.success_rate = self.calculate_success_rate()
        
        # Calculate efficiency score
        self.efficiency_score = self.calculate_efficiency_score()

    def calculate_data_volume(self):
        """Calculate data volume"""
        if self.import_export_type == "Import":
            # Calculate based on file size
            file_size = frappe.db.get_value("File", {"attached_to_name": self.name}, "file_size") or 0
            return file_size
        else:
            # Calculate based on record count
            record_count = frappe.db.sql("""
                SELECT COUNT(*) as record_count
                FROM `tab{0}`
                WHERE {1}
            """.format(self.target_doctype, self.filter_conditions))[0][0]
            return record_count

    def calculate_estimated_duration(self):
        """Calculate estimated duration"""
        # Base duration calculation
        base_duration = 5  # 5 minutes base
        
        # Add duration based on data volume
        if self.data_volume:
            volume_duration = self.data_volume / 1000  # 1 second per 1000 records
            base_duration += volume_duration
        
        # Add duration based on complexity
        complexity_duration = {
            "Simple": 0,
            "Medium": 5,
            "Complex": 15
        }
        
        complexity = self.calculate_complexity()
        base_duration += complexity_duration.get(complexity, 0)
        
        return base_duration

    def calculate_complexity(self):
        """Calculate import/export complexity"""
        complexity_factors = {
            'data_volume': self.get_volume_complexity(),
            'data_mapping': self.get_mapping_complexity(),
            'data_transformation': self.get_transformation_complexity(),
            'data_validation': self.get_validation_complexity()
        }
        
        # Calculate complexity score
        complexity_score = (
            complexity_factors['data_volume'] * 0.3 +
            complexity_factors['data_mapping'] * 0.3 +
            complexity_factors['data_transformation'] * 0.2 +
            complexity_factors['data_validation'] * 0.2
        )
        
        if complexity_score <= 3:
            return "Simple"
        elif complexity_score <= 6:
            return "Medium"
        else:
            return "Complex"

    def get_volume_complexity(self):
        """Get volume-based complexity"""
        if self.data_volume:
            if self.data_volume > 100000:
                return 5
            elif self.data_volume > 10000:
                return 3
            elif self.data_volume > 1000:
                return 2
            else:
                return 1
        else:
            return 1

    def get_mapping_complexity(self):
        """Get mapping-based complexity"""
        if self.field_mapping:
            mapping_count = len(json.loads(self.field_mapping))
            if mapping_count > 20:
                return 5
            elif mapping_count > 10:
                return 3
            elif mapping_count > 5:
                return 2
            else:
                return 1
        else:
            return 1

    def get_transformation_complexity(self):
        """Get transformation-based complexity"""
        if self.data_transformation:
            transformation_count = len(json.loads(self.data_transformation))
            if transformation_count > 10:
                return 5
            elif transformation_count > 5:
                return 3
            elif transformation_count > 2:
                return 2
            else:
                return 1
        else:
            return 1

    def get_validation_complexity(self):
        """Get validation-based complexity"""
        if self.data_validation:
            validation_count = len(json.loads(self.data_validation))
            if validation_count > 15:
                return 5
            elif validation_count > 8:
                return 3
            elif validation_count > 3:
                return 2
            else:
                return 1
        else:
            return 1

    def calculate_success_rate(self):
        """Calculate import/export success rate"""
        # Get import/export history
        history = frappe.db.sql("""
            SELECT COUNT(*) as total_operations,
                   SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as successful_operations
            FROM `tabImport Export History`
            WHERE import_export = %s
            AND operation_date >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, self.name, as_dict=True)[0]
        
        if history['total_operations'] > 0:
            success_rate = (history['successful_operations'] / history['total_operations']) * 100
            return round(success_rate, 2)
        else:
            return 0

    def calculate_efficiency_score(self):
        """Calculate import/export efficiency score"""
        # Get performance data
        performance_data = frappe.db.sql("""
            SELECT AVG(execution_time) as avg_execution_time,
                   AVG(data_volume) as avg_data_volume
            FROM `tabImport Export History`
            WHERE import_export = %s
            AND operation_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name, as_dict=True)[0]
        
        # Calculate efficiency based on execution time and data volume
        if performance_data['avg_execution_time'] and performance_data['avg_data_volume']:
            efficiency = (performance_data['avg_data_volume'] / performance_data['avg_execution_time']) * 100
            return min(efficiency, 100)
        else:
            return 0

    def update_import_export_settings(self):
        """Update import/export-specific settings"""
        # Update import/export preferences
        if self.preferences:
            frappe.db.set_value("Data Import Export", self.name, "preferences", json.dumps(self.preferences))
        
        # Update import/export tags
        if self.tags:
            frappe.db.set_value("Data Import Export", self.name, "tags", json.dumps(self.tags))

    def setup_import_export_permissions(self):
        """Setup import/export-specific permissions"""
        # Create import/export-specific roles
        import_export_roles = [
            f"Import Export - {self.import_export_id}",
            f"Type - {self.import_export_type}",
            f"Category - {self.import_export_category}"
        ]
        
        for role_name in import_export_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_import_export_insights(self):
        """Generate import/export insights"""
        insights = {
            "data_volume": self.data_volume,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.import_export_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify import/export optimization opportunities"""
        opportunities = []
        
        # Check for performance bottlenecks
        bottlenecks = self.identify_performance_bottlenecks()
        if bottlenecks:
            opportunities.append("Address performance bottlenecks")
        
        # Check for automation opportunities
        automation_opportunities = self.identify_automation_opportunities()
        if automation_opportunities:
            opportunities.append("Implement automation")
        
        # Check for data quality issues
        data_quality_issues = self.identify_data_quality_issues()
        if data_quality_issues:
            opportunities.append("Improve data quality")
        
        return opportunities

    def identify_performance_bottlenecks(self):
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Check for slow operations
        slow_operations = frappe.db.sql("""
            SELECT operation_type, AVG(execution_time) as avg_execution_time
            FROM `tabImport Export History`
            WHERE import_export = %s
            AND execution_time > %s
            GROUP BY operation_type
        """, (self.name, 300), as_dict=True)  # Operations taking more than 5 minutes
        
        if slow_operations:
            bottlenecks.append("Slow operations identified")
        
        # Check for data volume issues
        if self.data_volume > 100000:
            bottlenecks.append("Large data volume may cause performance issues")
        
        return bottlenecks

    def identify_automation_opportunities(self):
        """Identify automation opportunities"""
        opportunities = []
        
        # Check for repetitive operations
        repetitive_operations = frappe.db.sql("""
            SELECT operation_type, COUNT(*) as operation_count
            FROM `tabImport Export History`
            WHERE import_export = %s
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

    def identify_data_quality_issues(self):
        """Identify data quality issues"""
        issues = []
        
        # Check for validation failures
        validation_failures = frappe.db.sql("""
            SELECT COUNT(*) as failure_count
            FROM `tabImport Export History`
            WHERE import_export = %s
            AND validation_errors > 0
            AND operation_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        if validation_failures > 0:
            issues.append("Data validation failures identified")
        
        # Check for data mapping issues
        mapping_issues = frappe.db.sql("""
            SELECT COUNT(*) as mapping_count
            FROM `tabImport Export History`
            WHERE import_export = %s
            AND mapping_errors > 0
            AND operation_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, self.name)[0][0]
        
        if mapping_issues > 0:
            issues.append("Data mapping issues identified")
        
        return issues

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.import_export_status == "Pending":
            actions.append("Review import/export configuration")
            actions.append("Validate data mapping")
            actions.append("Execute import/export")
        elif self.import_export_status == "In Progress":
            actions.append("Monitor progress")
            actions.append("Address any issues")
            actions.append("Validate results")
        elif self.import_export_status == "Completed":
            actions.append("Review results")
            actions.append("Validate data quality")
            actions.append("Update related records")
        elif self.import_export_status == "Failed":
            actions.append("Review error logs")
            actions.append("Fix issues")
            actions.append("Retry operation")
        else:
            actions.append("Review import/export status")
            actions.append("Take appropriate action")
        
        return actions

    def create_import_export_profile(self):
        """Create comprehensive import/export profile"""
        profile_data = {
            "import_export_id": self.import_export_id,
            "import_export_name": self.import_export_name,
            "import_export_type": self.import_export_type,
            "import_export_category": self.import_export_category,
            "import_export_status": self.import_export_status,
            "import_export_priority": self.import_export_priority,
            "data_source": self.data_source,
            "target_doctype": self.target_doctype,
            "data_volume": self.data_volume,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "is_scheduled": self.is_scheduled
        }
        
        frappe.get_doc({
            "doctype": "Import Export Profile",
            "import_export": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_import_export_workflow(self):
        """Setup import/export workflow"""
        workflow_data = {
            "import_export": self.name,
            "workflow_type": "Import Export Management",
            "steps": [
                {"step": "Configuration", "status": "Completed"},
                {"step": "Validation", "status": "Pending"},
                {"step": "Execution", "status": "Pending"},
                {"step": "Verification", "status": "Pending"},
                {"step": "Completion", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Import Export Workflow",
            "import_export": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_import_export_analytics(self):
        """Create import/export analytics"""
        analytics_data = {
            "import_export": self.name,
            "analytics_type": "Import Export Analytics",
            "metrics": {
                "data_volume": self.data_volume,
                "estimated_duration": self.estimated_duration,
                "success_rate": self.success_rate,
                "efficiency_score": self.efficiency_score
            },
            "insights": self.generate_import_export_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Import Export Analytics",
            "import_export": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_import_export_tracking(self):
        """Initialize import/export tracking"""
        tracking_data = {
            "import_export": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "operation_count": 0,
            "success_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Import Export Tracking",
            "import_export": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_import_export_analytics(self):
        """Update import/export analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "data_volume": self.data_volume,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.calculate_success_rate(),
            "efficiency_score": self.calculate_efficiency_score()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Import Export Analytics", {"import_export": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "import_export": self.name,
                "analytics_type": "Import Export Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_import_export_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_import_export_data(self):
        """Sync import/export data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_import_export_status(self):
        """Update import/export status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Import Export Tracking", {"import_export": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_import_export_changes(self):
        """Process import/export changes"""
        # Log import/export changes
        self.log_import_export_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Import Export Status Change",
            "import_export": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.import_export_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabImport Export Status Change`
            WHERE import_export = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Import Export Status Change", {"import_export": self.name}) else "New"
        
        return previous_status

    def log_import_export_changes(self):
        """Log import/export changes"""
        frappe.get_doc({
            "doctype": "Import Export Change Log",
            "import_export": self.name,
            "change_type": "Update",
            "change_description": "Import/Export information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update import/export history
        self.update_import_export_history()
        
        # Update import/export logs
        self.update_import_export_logs()

    def update_import_export_history(self):
        """Update import/export history"""
        # Update history status
        frappe.db.sql("""
            UPDATE `tabImport Export History`
            SET import_export_status = %s
            WHERE import_export = %s
        """, (self.import_export_status, self.name))

    def update_import_export_logs(self):
        """Update import/export logs"""
        # Update log status
        frappe.db.sql("""
            UPDATE `tabImport Export Log`
            SET import_export_status = %s
            WHERE import_export = %s
        """, (self.import_export_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify import/export users
        self.notify_import_export_users()
        
        # Notify data administrators
        self.notify_data_administrators()

    def notify_import_export_users(self):
        """Notify import/export users"""
        frappe.get_doc({
            "doctype": "Import Export Notification",
            "import_export": self.name,
            "notification_type": "Import Export Update",
            "message": f"Import/Export {self.import_export_name} has been updated",
            "recipients": "Import Export Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_data_administrators(self):
        """Notify data administrators"""
        frappe.get_doc({
            "doctype": "Import Export Notification",
            "import_export": self.name,
            "notification_type": "Import Export Update",
            "message": f"Import/Export {self.import_export_name} has been updated",
            "recipients": "Data Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync import/export data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_import_export_dashboard_data(self):
        """Get import/export dashboard data"""
        return {
            "import_export_id": self.import_export_id,
            "import_export_name": self.import_export_name,
            "import_export_type": self.import_export_type,
            "import_export_category": self.import_export_category,
            "import_export_status": self.import_export_status,
            "import_export_priority": self.import_export_priority,
            "data_source": self.data_source,
            "target_doctype": self.target_doctype,
            "data_volume": self.data_volume,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "is_scheduled": self.is_scheduled,
            "insights": self.generate_import_export_insights()
        }

    @frappe.whitelist()
    def execute_import_export(self):
        """Execute import/export operation"""
        if self.import_export_status != "Pending":
            return {
                "status": "error",
                "message": "Only pending operations can be executed"
            }
        
        try:
            if self.import_export_type == "Import":
                result = self.execute_import()
            else:
                result = self.execute_export()
            
            # Update status
            self.import_export_status = "Completed"
            self.completion_date = now()
            self.completed_by = frappe.session.user
            
            # Log completion
            frappe.get_doc({
                "doctype": "Import Export History",
                "import_export": self.name,
                "operation_type": self.import_export_type,
                "operation_date": now(),
                "status": "Completed",
                "execution_time": result.get('execution_time', 0),
                "records_processed": result.get('records_processed', 0)
            }).insert(ignore_permissions=True)
            
            # Save changes
            self.save()
            
            return {
                "status": "success",
                "message": f"{self.import_export_type} operation completed successfully",
                "result": result
            }
            
        except Exception as e:
            # Update status
            self.import_export_status = "Failed"
            self.failure_date = now()
            self.failure_reason = str(e)
            
            # Log failure
            frappe.get_doc({
                "doctype": "Import Export History",
                "import_export": self.name,
                "operation_type": self.import_export_type,
                "operation_date": now(),
                "status": "Failed",
                "error_message": str(e)
            }).insert(ignore_permissions=True)
            
            # Save changes
            self.save()
            
            return {
                "status": "error",
                "message": f"{self.import_export_type} operation failed",
                "error": str(e)
            }

    def execute_import(self):
        """Execute import operation"""
        # Implementation for import operation
        start_time = now()
        
        # Read file
        file_data = self.read_import_file()
        
        # Process data
        processed_data = self.process_import_data(file_data)
        
        # Import data
        import_result = self.import_data(processed_data)
        
        end_time = now()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            "execution_time": execution_time,
            "records_processed": import_result.get('records_processed', 0),
            "records_imported": import_result.get('records_imported', 0),
            "records_failed": import_result.get('records_failed', 0)
        }

    def execute_export(self):
        """Execute export operation"""
        # Implementation for export operation
        start_time = now()
        
        # Get data
        export_data = self.get_export_data()
        
        # Process data
        processed_data = self.process_export_data(export_data)
        
        # Export data
        export_result = self.export_data(processed_data)
        
        end_time = now()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            "execution_time": execution_time,
            "records_processed": export_result.get('records_processed', 0),
            "records_exported": export_result.get('records_exported', 0),
            "file_path": export_result.get('file_path', '')
        }

    def read_import_file(self):
        """Read import file"""
        # Implementation for reading import file
        pass

    def process_import_data(self, file_data):
        """Process import data"""
        # Implementation for processing import data
        pass

    def import_data(self, processed_data):
        """Import data"""
        # Implementation for importing data
        pass

    def get_export_data(self):
        """Get export data"""
        # Implementation for getting export data
        pass

    def process_export_data(self, export_data):
        """Process export data"""
        # Implementation for processing export data
        pass

    def export_data(self, processed_data):
        """Export data"""
        # Implementation for exporting data
        pass

    @frappe.whitelist()
    def get_import_export_insights(self):
        """Get import/export insights"""
        return {
            "data_volume": self.data_volume,
            "estimated_duration": self.estimated_duration,
            "success_rate": self.success_rate,
            "efficiency_score": self.efficiency_score,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
