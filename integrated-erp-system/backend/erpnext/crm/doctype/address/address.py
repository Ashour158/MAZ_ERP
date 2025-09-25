# Enhanced Address DocType - Complete Address Management with Shipping and Billing

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class Address(Document):
    def autoname(self):
        """Generate unique address ID"""
        if not self.address_id:
            self.address_id = make_autoname("ADD-.YYYY.-.MM.-.#####")
        self.name = self.address_id

    def validate(self):
        """Validate address data"""
        self.validate_address_data()
        self.set_defaults()
        self.validate_address_info()
        self.calculate_address_metrics()
        self.determine_address_priority()

    def before_save(self):
        """Process before saving"""
        self.update_address_settings()
        self.setup_address_permissions()
        self.generate_address_insights()

    def after_insert(self):
        """Process after inserting new address"""
        self.create_address_profile()
        self.setup_address_workflow()
        self.create_address_analytics()
        self.initialize_address_tracking()

    def on_update(self):
        """Process on address update"""
        self.update_address_analytics()
        self.sync_address_data()
        self.update_address_priority()
        self.process_address_changes()

    def validate_address_data(self):
        """Validate address information"""
        if not self.address_line1:
            frappe.throw(_("Address line 1 is required"))
        
        if not self.city:
            frappe.throw(_("City is required"))
        
        if not self.country:
            frappe.throw(_("Country is required"))
        
        if not self.customer:
            frappe.throw(_("Customer is required"))

    def validate_address_info(self):
        """Validate address information"""
        if self.pincode and not self.validate_pincode():
            frappe.throw(_("Invalid pincode format"))
        
        if self.email_id and not self.validate_email():
            frappe.throw(_("Invalid email format"))

    def set_defaults(self):
        """Set default values for new address"""
        if not self.address_type:
            self.address_type = "Billing"
        
        if not self.address_status:
            self.address_status = "Active"
        
        if not self.address_priority:
            self.address_priority = "Medium"
        
        if not self.is_primary_address:
            self.is_primary_address = 0
        
        if not self.is_shipping_address:
            self.is_shipping_address = 0
        
        if not self.is_billing_address:
            self.is_billing_address = 0

    def calculate_address_metrics(self):
        """Calculate address metrics"""
        # Calculate address usage score
        self.address_usage_score = self.calculate_usage_score()
        
        # Calculate address validation score
        self.address_validation_score = self.calculate_validation_score()
        
        # Calculate address completeness score
        self.address_completeness_score = self.calculate_completeness_score()
        
        # Calculate address geocoding score
        self.address_geocoding_score = self.calculate_geocoding_score()

    def calculate_usage_score(self):
        """Calculate address usage score"""
        # Get usage count
        usage_count = frappe.db.sql("""
            SELECT COUNT(*) as usage_count
            FROM `tabAddress Usage`
            WHERE address = %s
            AND usage_date >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, self.name)[0][0]
        
        # Get order count
        order_count = frappe.db.sql("""
            SELECT COUNT(*) as order_count
            FROM `tabSales Order`
            WHERE shipping_address = %s
            OR billing_address = %s
            AND creation >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """, (self.name, self.name))[0][0]
        
        # Calculate usage score
        usage_score = (usage_count * 0.6 + order_count * 0.4) / 10
        
        return min(usage_score, 1.0)

    def calculate_validation_score(self):
        """Calculate address validation score"""
        validation_score = 0
        
        # Check required fields
        if self.address_line1:
            validation_score += 0.2
        if self.city:
            validation_score += 0.2
        if self.state:
            validation_score += 0.2
        if self.country:
            validation_score += 0.2
        if self.pincode:
            validation_score += 0.2
        
        return validation_score

    def calculate_completeness_score(self):
        """Calculate address completeness score"""
        completeness_score = 0
        
        # Check address fields
        if self.address_line1:
            completeness_score += 0.15
        if self.address_line2:
            completeness_score += 0.10
        if self.city:
            completeness_score += 0.15
        if self.state:
            completeness_score += 0.15
        if self.country:
            completeness_score += 0.15
        if self.pincode:
            completeness_score += 0.10
        if self.phone:
            completeness_score += 0.10
        if self.email_id:
            completeness_score += 0.10
        
        return completeness_score

    def calculate_geocoding_score(self):
        """Calculate address geocoding score"""
        if self.latitude and self.longitude:
            return 1.0
        else:
            return 0.0

    def determine_address_priority(self):
        """Determine address priority"""
        if self.is_primary_address:
            self.address_priority = "High"
        elif self.is_shipping_address or self.is_billing_address:
            self.address_priority = "Medium"
        else:
            self.address_priority = "Low"

    def update_address_settings(self):
        """Update address-specific settings"""
        # Update address preferences
        if self.preferences:
            frappe.db.set_value("Address", self.name, "preferences", json.dumps(self.preferences))
        
        # Update address tags
        if self.tags:
            frappe.db.set_value("Address", self.name, "tags", json.dumps(self.tags))

    def setup_address_permissions(self):
        """Setup address-specific permissions"""
        # Create address-specific roles
        address_roles = [
            f"Address - {self.address_id}",
            f"Customer - {self.customer}",
            f"Priority - {self.address_priority}"
        ]
        
        for role_name in address_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_address_insights(self):
        """Generate address insights"""
        insights = {
            "address_priority": self.address_priority,
            "usage_level": self.determine_usage_level(),
            "validation_status": self.determine_validation_status(),
            "completeness_level": self.determine_completeness_level(),
            "geocoding_status": self.determine_geocoding_status(),
            "next_actions": self.recommend_next_actions()
        }
        
        self.address_insights = json.dumps(insights)

    def determine_usage_level(self):
        """Determine usage level"""
        if self.address_usage_score >= 0.8:
            return "High Usage"
        elif self.address_usage_score >= 0.6:
            return "Medium Usage"
        else:
            return "Low Usage"

    def determine_validation_status(self):
        """Determine validation status"""
        if self.address_validation_score >= 0.8:
            return "Validated"
        elif self.address_validation_score >= 0.6:
            return "Partially Validated"
        else:
            return "Not Validated"

    def determine_completeness_level(self):
        """Determine completeness level"""
        if self.address_completeness_score >= 0.8:
            return "Complete"
        elif self.address_completeness_score >= 0.6:
            return "Mostly Complete"
        else:
            return "Incomplete"

    def determine_geocoding_status(self):
        """Determine geocoding status"""
        if self.address_geocoding_score >= 0.8:
            return "Geocoded"
        else:
            return "Not Geocoded"

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.address_validation_score < 0.8:
            actions.append("Validate address information")
            actions.append("Update missing fields")
        
        if self.address_completeness_score < 0.8:
            actions.append("Complete address information")
            actions.append("Add missing details")
        
        if self.address_geocoding_score < 0.8:
            actions.append("Geocode address")
            actions.append("Add latitude and longitude")
        
        if self.address_usage_score < 0.5:
            actions.append("Increase address usage")
            actions.append("Promote address in orders")
        
        return actions

    def create_address_profile(self):
        """Create comprehensive address profile"""
        profile_data = {
            "address_id": self.address_id,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "pincode": self.pincode,
            "customer": self.customer,
            "address_type": self.address_type,
            "address_status": self.address_status,
            "address_priority": self.address_priority,
            "is_primary_address": self.is_primary_address,
            "is_shipping_address": self.is_shipping_address,
            "is_billing_address": self.is_billing_address,
            "phone": self.phone,
            "email_id": self.email_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "metrics": {
                "usage_score": self.address_usage_score,
                "validation_score": self.address_validation_score,
                "completeness_score": self.address_completeness_score,
                "geocoding_score": self.address_geocoding_score
            }
        }
        
        frappe.get_doc({
            "doctype": "Address Profile",
            "address": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_address_workflow(self):
        """Setup address workflow"""
        workflow_data = {
            "address": self.name,
            "workflow_type": "Address Management",
            "steps": [
                {"step": "Address Creation", "status": "Completed"},
                {"step": "Address Validation", "status": "Pending"},
                {"step": "Address Geocoding", "status": "Pending"},
                {"step": "Address Usage", "status": "Pending"},
                {"step": "Address Maintenance", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Address Workflow",
            "address": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_address_analytics(self):
        """Create address analytics"""
        analytics_data = {
            "address": self.name,
            "analytics_type": "Address Analytics",
            "metrics": {
                "usage_score": self.address_usage_score,
                "validation_score": self.address_validation_score,
                "completeness_score": self.address_completeness_score,
                "geocoding_score": self.address_geocoding_score
            },
            "insights": self.generate_address_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Address Analytics",
            "address": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_address_tracking(self):
        """Initialize address tracking"""
        tracking_data = {
            "address": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "usage_count": 0,
            "validation_count": 0
        }
        
        frappe.get_doc({
            "doctype": "Address Tracking",
            "address": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_address_analytics(self):
        """Update address analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "usage_score": self.address_usage_score,
            "validation_score": self.address_validation_score,
            "completeness_score": self.address_completeness_score,
            "geocoding_score": self.address_geocoding_score
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Address Analytics", {"address": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "address": self.name,
                "analytics_type": "Address Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_address_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_address_data(self):
        """Sync address data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_address_priority(self):
        """Update address priority"""
        # Recalculate priority
        self.address_priority = self.determine_address_priority()
        
        # Update tracking
        tracking = frappe.get_doc("Address Tracking", {"address": self.name})
        if tracking:
            tracking.last_activity = now()
            tracking.save()

    def process_address_changes(self):
        """Process address changes"""
        # Log address changes
        self.log_address_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_address_changes(self):
        """Log address changes"""
        frappe.get_doc({
            "doctype": "Address Change Log",
            "address": self.name,
            "change_type": "Update",
            "change_description": "Address information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update customer records
        self.update_customer_records()
        
        # Update order records
        self.update_order_records()

    def update_customer_records(self):
        """Update customer records"""
        # Update customer address count
        frappe.db.sql("""
            UPDATE `tabCustomer`
            SET address_count = (
                SELECT COUNT(*) FROM `tabAddress`
                WHERE customer = %s AND status = 'Active'
            )
            WHERE name = %s
        """, (self.customer, self.customer))

    def update_order_records(self):
        """Update order records"""
        # Update order address information
        frappe.db.sql("""
            UPDATE `tabSales Order`
            SET shipping_address_name = %s
            WHERE shipping_address = %s
        """, (f"{self.address_line1}, {self.city}", self.name))
        
        frappe.db.sql("""
            UPDATE `tabSales Order`
            SET billing_address_name = %s
            WHERE billing_address = %s
        """, (f"{self.address_line1}, {self.city}", self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify sales team
        self.notify_sales_team()
        
        # Notify logistics team
        self.notify_logistics_team()

    def notify_sales_team(self):
        """Notify sales team"""
        frappe.get_doc({
            "doctype": "Address Notification",
            "address": self.name,
            "notification_type": "Address Update",
            "message": f"Address {self.address_line1} has been updated",
            "recipients": "Sales Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_logistics_team(self):
        """Notify logistics team"""
        frappe.get_doc({
            "doctype": "Address Notification",
            "address": self.name,
            "notification_type": "Address Update",
            "message": f"Address {self.address_line1} has been updated",
            "recipients": "Logistics Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def validate_pincode(self):
        """Validate pincode format"""
        import re
        pattern = r'^[0-9]{5,6}$'
        return re.match(pattern, self.pincode) is not None

    def validate_email(self):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.email_id) is not None

    def sync_with_external_system(self):
        """Sync address data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_address_dashboard_data(self):
        """Get address dashboard data"""
        return {
            "address_id": self.address_id,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "pincode": self.pincode,
            "customer": self.customer,
            "address_type": self.address_type,
            "address_status": self.address_status,
            "address_priority": self.address_priority,
            "is_primary_address": self.is_primary_address,
            "is_shipping_address": self.is_shipping_address,
            "is_billing_address": self.is_billing_address,
            "phone": self.phone,
            "email_id": self.email_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "metrics": {
                "usage_score": self.address_usage_score,
                "validation_score": self.address_validation_score,
                "completeness_score": self.address_completeness_score,
                "geocoding_score": self.address_geocoding_score
            },
            "insights": self.generate_address_insights()
        }

    @frappe.whitelist()
    def copy_from_billing_address(self, billing_address):
        """Copy from billing address"""
        billing = frappe.get_doc("Address", billing_address)
        
        self.address_line1 = billing.address_line1
        self.address_line2 = billing.address_line2
        self.city = billing.city
        self.state = billing.state
        self.country = billing.country
        self.pincode = billing.pincode
        self.phone = billing.phone
        self.email_id = billing.email_id
        
        # Set as shipping address
        self.is_shipping_address = 1
        self.address_type = "Shipping"
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Address copied from billing address"
        }

    @frappe.whitelist()
    def copy_from_shipping_address(self, shipping_address):
        """Copy from shipping address"""
        shipping = frappe.get_doc("Address", shipping_address)
        
        self.address_line1 = shipping.address_line1
        self.address_line2 = shipping.address_line2
        self.city = shipping.city
        self.state = shipping.state
        self.country = shipping.country
        self.pincode = shipping.pincode
        self.phone = shipping.phone
        self.email_id = shipping.email_id
        
        # Set as billing address
        self.is_billing_address = 1
        self.address_type = "Billing"
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Address copied from shipping address"
        }

    @frappe.whitelist()
    def geocode_address(self):
        """Geocode address"""
        try:
            # Use geocoding service
            geocoding_result = self.perform_geocoding()
            
            if geocoding_result:
                self.latitude = geocoding_result['latitude']
                self.longitude = geocoding_result['longitude']
                self.address_geocoding_score = 1.0
                
                # Save changes
                self.save()
                
                return {
                    "status": "success",
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "message": "Address geocoded successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "Geocoding failed"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Geocoding error: {str(e)}"
            }

    def perform_geocoding(self):
        """Perform geocoding"""
        # Implementation for geocoding service
        # This would integrate with Google Maps API or similar service
        pass

    @frappe.whitelist()
    def validate_address(self):
        """Validate address"""
        try:
            # Use address validation service
            validation_result = self.perform_address_validation()
            
            if validation_result:
                self.address_validation_score = validation_result['score']
                self.validation_status = validation_result['status']
                
                # Save changes
                self.save()
                
                return {
                    "status": "success",
                    "validation_score": self.address_validation_score,
                    "validation_status": self.validation_status,
                    "message": "Address validated successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "Address validation failed"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Validation error: {str(e)}"
            }

    def perform_address_validation(self):
        """Perform address validation"""
        # Implementation for address validation service
        # This would integrate with address validation API
        pass

    @frappe.whitelist()
    def get_address_insights(self):
        """Get address insights"""
        return {
            "address_priority": self.address_priority,
            "usage_level": self.determine_usage_level(),
            "validation_status": self.determine_validation_status(),
            "completeness_level": self.determine_completeness_level(),
            "geocoding_status": self.determine_geocoding_status(),
            "next_actions": self.recommend_next_actions()
        }
