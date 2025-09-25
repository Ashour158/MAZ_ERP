# Coding System - Advanced Contact and Account Coding

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
import re
from datetime import datetime, timedelta

class CodingSystem(Document):
    def autoname(self):
        """Generate unique coding system ID"""
        if not self.coding_system_id:
            self.coding_system_id = make_autoname("COD-.YYYY.-.MM.-.#####")
        self.name = self.coding_system_id

    def validate(self):
        """Validate coding system data"""
        self.validate_coding_data()
        self.set_defaults()
        self.validate_coding_rules()
        self.calculate_coding_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_coding_settings()
        self.setup_coding_permissions()
        self.generate_coding_insights()

    def after_insert(self):
        """Process after inserting new coding system"""
        self.create_coding_profile()
        self.setup_coding_workflow()
        self.create_coding_analytics()
        self.initialize_coding_tracking()

    def on_update(self):
        """Process on coding system update"""
        self.update_coding_analytics()
        self.sync_coding_data()
        self.update_coding_status()
        self.process_coding_changes()

    def validate_coding_data(self):
        """Validate coding system information"""
        if not self.coding_system_name:
            frappe.throw(_("Coding system name is required"))
        
        if not self.coding_type:
            frappe.throw(_("Coding type is required"))
        
        if not self.coding_rules:
            frappe.throw(_("Coding rules are required"))

    def validate_coding_rules(self):
        """Validate coding rules"""
        if not self.coding_rules:
            frappe.throw(_("Coding rules are required"))
        
        # Validate coding rules format
        try:
            rules = json.loads(self.coding_rules)
            if not isinstance(rules, dict):
                frappe.throw(_("Coding rules must be a valid JSON object"))
            
            # Validate rule structure
            self.validate_rule_structure(rules)
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON format in coding rules"))

    def validate_rule_structure(self, rules):
        """Validate coding rule structure"""
        required_fields = ['territory_based', 'coding_format', 'auto_generation', 'prefix', 'suffix']
        
        for field in required_fields:
            if field not in rules:
                frappe.throw(_("Coding rules must include: {0}").format(field))
        
        # Validate territory-based rules
        if rules['territory_based']:
            if 'territory_mapping' not in rules:
                frappe.throw(_("Territory mapping is required for territory-based coding"))
        
        # Validate coding format
        if rules['coding_format'] not in ['numeric', 'alphanumeric', 'text', 'mixed']:
            frappe.throw(_("Invalid coding format. Must be: numeric, alphanumeric, text, or mixed"))

    def set_defaults(self):
        """Set default values for new coding system"""
        if not self.coding_status:
            self.coding_status = "Active"
        
        if not self.coding_priority:
            self.coding_priority = "High"
        
        if not self.coding_category:
            self.coding_category = "General"
        
        if not self.is_auto_generation_enabled:
            self.is_auto_generation_enabled = 1

    def calculate_coding_metrics(self):
        """Calculate coding system metrics"""
        # Calculate coding efficiency
        self.coding_efficiency = self.calculate_coding_efficiency()
        
        # Calculate coding accuracy
        self.coding_accuracy = self.calculate_coding_accuracy()
        
        # Calculate coding performance
        self.coding_performance = self.calculate_coding_performance()
        
        # Calculate coding coverage
        self.coding_coverage = self.calculate_coding_coverage()

    def calculate_coding_efficiency(self):
        """Calculate coding efficiency"""
        # Get coding efficiency data
        efficiency_data = frappe.db.sql("""
            SELECT AVG(efficiency_percentage) as avg_efficiency,
                   COUNT(*) as total_operations
            FROM `tabCoding Operation`
            WHERE coding_system = %s
            AND operation_date >= DATE_SUB(NOW(), INTERVAL 30 DAYS)
        """, self.name, as_dict=True)[0]
        
        if efficiency_data['total_operations'] > 0:
            return round(efficiency_data['avg_efficiency'], 2)
        else:
            return 0

    def calculate_coding_accuracy(self):
        """Calculate coding accuracy"""
        # Get coding accuracy data
        accuracy_data = frappe.db.sql("""
            SELECT AVG(accuracy_percentage) as avg_accuracy,
                   COUNT(*) as total_codes
            FROM `tabCoding Accuracy`
            WHERE coding_system = %s
            AND accuracy_date >= DATE_SUB(NOW(), INTERVAL 30 DAYS)
        """, self.name, as_dict=True)[0]
        
        if accuracy_data['total_codes'] > 0:
            return round(accuracy_data['avg_accuracy'], 2)
        else:
            return 0

    def calculate_coding_performance(self):
        """Calculate coding performance"""
        # Get coding performance data
        performance_data = frappe.db.sql("""
            SELECT AVG(processing_time) as avg_processing_time,
                   AVG(success_rate) as avg_success_rate
            FROM `tabCoding Performance`
            WHERE coding_system = %s
            AND performance_date >= DATE_SUB(NOW(), INTERVAL 30 DAYS)
        """, self.name, as_dict=True)[0]
        
        if performance_data['avg_processing_time']:
            # Calculate performance score based on processing time and success rate
            time_score = max(0, 100 - (performance_data['avg_processing_time'] / 10))
            success_score = performance_data['avg_success_rate']
            performance = (time_score + success_score) / 2
            return min(performance, 100)
        else:
            return 0

    def calculate_coding_coverage(self):
        """Calculate coding coverage"""
        # Get coding coverage data
        coverage_data = frappe.db.sql("""
            SELECT COUNT(*) as total_records,
                   SUM(CASE WHEN code IS NOT NULL AND code != '' THEN 1 ELSE 0 END) as coded_records
            FROM `tab{0}`
            WHERE {1}
        """.format(self.target_doctype, self.filter_conditions), as_dict=True)[0]
        
        if coverage_data['total_records'] > 0:
            coverage = (coverage_data['coded_records'] / coverage_data['total_records']) * 100
            return round(coverage, 2)
        else:
            return 0

    def update_coding_settings(self):
        """Update coding-specific settings"""
        # Update coding preferences
        if self.preferences:
            frappe.db.set_value("Coding System", self.name, "preferences", json.dumps(self.preferences))
        
        # Update coding tags
        if self.tags:
            frappe.db.set_value("Coding System", self.name, "tags", json.dumps(self.tags))

    def setup_coding_permissions(self):
        """Setup coding-specific permissions"""
        # Create coding-specific roles
        coding_roles = [
            f"Coding - {self.coding_system_id}",
            f"Type - {self.coding_type}",
            f"Category - {self.coding_category}"
        ]
        
        for role_name in coding_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_coding_insights(self):
        """Generate coding insights"""
        insights = {
            "coding_efficiency": self.coding_efficiency,
            "coding_accuracy": self.coding_accuracy,
            "coding_performance": self.coding_performance,
            "coding_coverage": self.coding_coverage,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.coding_insights = json.dumps(insights)

    def identify_optimization_opportunities(self):
        """Identify coding optimization opportunities"""
        opportunities = []
        
        # Check for efficiency improvements
        if self.coding_efficiency < 80:
            opportunities.append("Optimize coding efficiency")
        
        # Check for accuracy improvements
        if self.coding_accuracy < 90:
            opportunities.append("Improve coding accuracy")
        
        # Check for performance improvements
        if self.coding_performance < 80:
            opportunities.append("Enhance coding performance")
        
        # Check for coverage improvements
        if self.coding_coverage < 95:
            opportunities.append("Increase coding coverage")
        
        return opportunities

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.coding_status == "Active":
            actions.append("Monitor coding performance")
            actions.append("Update coding rules")
            actions.append("Optimize coding settings")
        elif self.coding_status == "Testing":
            actions.append("Complete coding testing")
            actions.append("Validate coding rules")
            actions.append("Deploy coding system")
        else:
            actions.append("Review coding status")
            actions.append("Take appropriate action")
        
        return actions

    def create_coding_profile(self):
        """Create comprehensive coding profile"""
        profile_data = {
            "coding_system_id": self.coding_system_id,
            "coding_system_name": self.coding_system_name,
            "coding_type": self.coding_type,
            "coding_category": self.coding_category,
            "coding_status": self.coding_status,
            "coding_priority": self.coding_priority,
            "coding_efficiency": self.coding_efficiency,
            "coding_accuracy": self.coding_accuracy,
            "coding_performance": self.coding_performance,
            "coding_coverage": self.coding_coverage,
            "is_auto_generation_enabled": self.is_auto_generation_enabled
        }
        
        frappe.get_doc({
            "doctype": "Coding Profile",
            "coding_system": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_coding_workflow(self):
        """Setup coding workflow"""
        workflow_data = {
            "coding_system": self.name,
            "workflow_type": "Coding Management",
            "steps": [
                {"step": "Coding Configuration", "status": "Completed"},
                {"step": "Coding Testing", "status": "Pending"},
                {"step": "Coding Deployment", "status": "Pending"},
                {"step": "Coding Monitoring", "status": "Pending"},
                {"step": "Coding Optimization", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Coding Workflow",
            "coding_system": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_coding_analytics(self):
        """Create coding analytics"""
        analytics_data = {
            "coding_system": self.name,
            "analytics_type": "Coding Analytics",
            "metrics": {
                "coding_efficiency": self.coding_efficiency,
                "coding_accuracy": self.coding_accuracy,
                "coding_performance": self.coding_performance,
                "coding_coverage": self.coding_coverage
            },
            "insights": self.generate_coding_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Coding Analytics",
            "coding_system": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_coding_tracking(self):
        """Initialize coding tracking"""
        tracking_data = {
            "coding_system": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "code_generation_count": 0,
            "success_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Coding Tracking",
            "coding_system": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_coding_analytics(self):
        """Update coding analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "coding_efficiency": self.calculate_coding_efficiency(),
            "coding_accuracy": self.calculate_coding_accuracy(),
            "coding_performance": self.calculate_coding_performance(),
            "coding_coverage": self.calculate_coding_coverage()
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Coding Analytics", {"coding_system": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "coding_system": self.name,
                "analytics_type": "Coding Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_coding_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_coding_data(self):
        """Sync coding data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_coding_status(self):
        """Update coding status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Coding Tracking", {"coding_system": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_coding_changes(self):
        """Process coding changes"""
        # Log coding changes
        self.log_coding_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Coding Status Change",
            "coding_system": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.coding_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabCoding Status Change`
            WHERE coding_system = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Coding Status Change", {"coding_system": self.name}) else "New"
        
        return previous_status

    def log_coding_changes(self):
        """Log coding changes"""
        frappe.get_doc({
            "doctype": "Coding Change Log",
            "coding_system": self.name,
            "change_type": "Update",
            "change_description": "Coding system information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update coding operations
        self.update_coding_operations()
        
        # Update coding accuracy
        self.update_coding_accuracy()

    def update_coding_operations(self):
        """Update coding operations"""
        # Update operation status
        frappe.db.sql("""
            UPDATE `tabCoding Operation`
            SET coding_system_status = %s
            WHERE coding_system = %s
        """, (self.coding_status, self.name))

    def update_coding_accuracy(self):
        """Update coding accuracy"""
        # Update accuracy status
        frappe.db.sql("""
            UPDATE `tabCoding Accuracy`
            SET coding_system_status = %s
            WHERE coding_system = %s
        """, (self.coding_status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify coding users
        self.notify_coding_users()
        
        # Notify coding administrators
        self.notify_coding_administrators()

    def notify_coding_users(self):
        """Notify coding users"""
        frappe.get_doc({
            "doctype": "Coding Notification",
            "coding_system": self.name,
            "notification_type": "Coding Update",
            "message": f"Coding system {self.coding_system_name} has been updated",
            "recipients": "Coding Users",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_coding_administrators(self):
        """Notify coding administrators"""
        frappe.get_doc({
            "doctype": "Coding Notification",
            "coding_system": self.name,
            "notification_type": "Coding Update",
            "message": f"Coding system {self.coding_system_name} has been updated",
            "recipients": "Coding Administrators",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync coding data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_coding_dashboard_data(self):
        """Get coding dashboard data"""
        return {
            "coding_system_id": self.coding_system_id,
            "coding_system_name": self.coding_system_name,
            "coding_type": self.coding_type,
            "coding_category": self.coding_category,
            "coding_status": self.coding_status,
            "coding_priority": self.coding_priority,
            "coding_efficiency": self.coding_efficiency,
            "coding_accuracy": self.coding_accuracy,
            "coding_performance": self.coding_performance,
            "coding_coverage": self.coding_coverage,
            "is_auto_generation_enabled": self.is_auto_generation_enabled,
            "insights": self.generate_coding_insights()
        }

    @frappe.whitelist()
    def generate_code(self, record_data, territory=None):
        """Generate code for a record"""
        try:
            # Get coding rules
            rules = json.loads(self.coding_rules)
            
            # Generate code based on rules
            code = self.execute_code_generation(record_data, rules, territory)
            
            # Log code generation
            frappe.get_doc({
                "doctype": "Coding Operation",
                "coding_system": self.name,
                "record_data": json.dumps(record_data),
                "generated_code": code,
                "territory": territory,
                "operation_date": now(),
                "generated_by": frappe.session.user
            }).insert(ignore_permissions=True)
            
            return {
                "status": "success",
                "code": code,
                "message": "Code generated successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Code generation failed: {str(e)}"
            }

    def execute_code_generation(self, record_data, rules, territory=None):
        """Execute code generation based on rules"""
        code_parts = []
        
        # Add prefix if specified
        if rules.get('prefix'):
            code_parts.append(rules['prefix'])
        
        # Add territory code if territory-based
        if rules.get('territory_based') and territory:
            territory_code = self.get_territory_code(territory, rules)
            code_parts.append(territory_code)
        
        # Generate main code based on format
        main_code = self.generate_main_code(record_data, rules)
        code_parts.append(main_code)
        
        # Add suffix if specified
        if rules.get('suffix'):
            code_parts.append(rules['suffix'])
        
        # Join all parts
        code = ''.join(code_parts)
        
        # Validate code format
        self.validate_generated_code(code, rules)
        
        return code

    def get_territory_code(self, territory, rules):
        """Get territory code"""
        territory_mapping = rules.get('territory_mapping', {})
        return territory_mapping.get(territory, 'DEF')

    def generate_main_code(self, record_data, rules):
        """Generate main code based on format"""
        coding_format = rules.get('coding_format', 'numeric')
        
        if coding_format == 'numeric':
            return self.generate_numeric_code(record_data, rules)
        elif coding_format == 'alphanumeric':
            return self.generate_alphanumeric_code(record_data, rules)
        elif coding_format == 'text':
            return self.generate_text_code(record_data, rules)
        elif coding_format == 'mixed':
            return self.generate_mixed_code(record_data, rules)
        else:
            return self.generate_numeric_code(record_data, rules)

    def generate_numeric_code(self, record_data, rules):
        """Generate numeric code"""
        # Get next sequence number
        sequence_length = rules.get('sequence_length', 4)
        next_number = self.get_next_sequence_number()
        
        # Format with leading zeros
        return str(next_number).zfill(sequence_length)

    def generate_alphanumeric_code(self, record_data, rules):
        """Generate alphanumeric code"""
        # Get next sequence number
        sequence_length = rules.get('sequence_length', 4)
        next_number = self.get_next_sequence_number()
        
        # Convert to alphanumeric
        return self.number_to_alphanumeric(next_number, sequence_length)

    def generate_text_code(self, record_data, rules):
        """Generate text code"""
        # Use record data to generate text code
        if 'name' in record_data:
            # Use first 3 characters of name
            name_part = record_data['name'][:3].upper()
            return name_part
        else:
            return 'TXT'

    def generate_mixed_code(self, record_data, rules):
        """Generate mixed code"""
        # Combine text and numeric
        text_part = self.generate_text_code(record_data, rules)
        numeric_part = self.generate_numeric_code(record_data, rules)
        return f"{text_part}{numeric_part}"

    def get_next_sequence_number(self):
        """Get next sequence number"""
        # Get current max sequence
        max_sequence = frappe.db.sql("""
            SELECT MAX(CAST(sequence_number AS UNSIGNED)) as max_seq
            FROM `tabCoding Sequence`
            WHERE coding_system = %s
        """, self.name, as_dict=True)[0]
        
        next_number = (max_sequence['max_seq'] or 0) + 1
        
        # Store sequence number
        frappe.get_doc({
            "doctype": "Coding Sequence",
            "coding_system": self.name,
            "sequence_number": str(next_number),
            "generated_date": now()
        }).insert(ignore_permissions=True)
        
        return next_number

    def number_to_alphanumeric(self, number, length):
        """Convert number to alphanumeric"""
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = ""
        
        while number > 0:
            result = chars[number % 36] + result
            number //= 36
        
        # Pad with zeros if needed
        return result.zfill(length)

    def validate_generated_code(self, code, rules):
        """Validate generated code"""
        # Check code length
        min_length = rules.get('min_length', 1)
        max_length = rules.get('max_length', 10)
        
        if len(code) < min_length or len(code) > max_length:
            frappe.throw(_("Generated code length is invalid"))
        
        # Check code format
        if rules.get('coding_format') == 'numeric':
            if not code.isdigit():
                frappe.throw(_("Generated code must be numeric"))
        elif rules.get('coding_format') == 'alphanumeric':
            if not code.isalnum():
                frappe.throw(_("Generated code must be alphanumeric"))

    @frappe.whitelist()
    def get_coding_insights(self):
        """Get coding insights"""
        return {
            "coding_efficiency": self.coding_efficiency,
            "coding_accuracy": self.coding_accuracy,
            "coding_performance": self.coding_performance,
            "coding_coverage": self.coding_coverage,
            "optimization_opportunities": self.identify_optimization_opportunities(),
            "next_actions": self.recommend_next_actions()
        }

    @frappe.whitelist()
    def export_coded_data(self, filters=None):
        """Export data with codes"""
        try:
            # Get records with codes
            records = self.get_coded_records(filters)
            
            # Format for export
            export_data = self.format_export_data(records)
            
            # Log export
            frappe.get_doc({
                "doctype": "Coding Export",
                "coding_system": self.name,
                "export_filters": json.dumps(filters or {}),
                "export_data": json.dumps(export_data),
                "export_date": now(),
                "exported_by": frappe.session.user
            }).insert(ignore_permissions=True)
            
            return {
                "status": "success",
                "data": export_data,
                "message": "Data exported successfully with codes"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Export failed: {str(e)}"
            }

    def get_coded_records(self, filters=None):
        """Get records with codes"""
        # Build query
        query = f"""
            SELECT name, code, territory, creation, modified
            FROM `tab{self.target_doctype}`
            WHERE code IS NOT NULL AND code != ''
        """
        
        if filters:
            for key, value in filters.items():
                query += f" AND {key} = '{value}'"
        
        return frappe.db.sql(query, as_dict=True)

    def format_export_data(self, records):
        """Format data for export"""
        export_data = []
        
        for record in records:
            export_data.append({
                "id": record.name,
                "code": record.code,
                "territory": record.territory,
                "created_date": record.creation,
                "modified_date": record.modified
            })
        
        return export_data
