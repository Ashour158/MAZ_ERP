# Enhanced Forecast DocType - Complete Sales Forecasting System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class Forecast(Document):
    def autoname(self):
        """Generate unique forecast ID"""
        if not self.forecast_id:
            self.forecast_id = make_autoname("FOR-.YYYY.-.MM.-.#####")
        self.name = self.forecast_id

    def validate(self):
        """Validate forecast data"""
        self.validate_forecast_data()
        self.set_defaults()
        self.validate_forecast_period()
        self.calculate_forecast_metrics()
        self.determine_forecast_status()

    def before_save(self):
        """Process before saving"""
        self.update_forecast_settings()
        self.setup_forecast_permissions()
        self.generate_forecast_insights()

    def after_insert(self):
        """Process after inserting new forecast"""
        self.create_forecast_profile()
        self.setup_forecast_workflow()
        self.create_forecast_analytics()
        self.initialize_forecast_tracking()

    def on_update(self):
        """Process on forecast update"""
        self.update_forecast_analytics()
        self.sync_forecast_data()
        self.update_forecast_status()
        self.process_forecast_changes()

    def validate_forecast_data(self):
        """Validate forecast information"""
        if not self.forecast_name:
            frappe.throw(_("Forecast name is required"))
        
        if not self.forecast_period:
            frappe.throw(_("Forecast period is required"))
        
        if not self.forecast_start_date:
            frappe.throw(_("Forecast start date is required"))
        
        if not self.forecast_end_date:
            frappe.throw(_("Forecast end date is required"))

    def validate_forecast_period(self):
        """Validate forecast period"""
        if self.forecast_start_date >= self.forecast_end_date:
            frappe.throw(_("Forecast start date must be before end date"))

    def set_defaults(self):
        """Set default values for new forecast"""
        if not self.forecast_status:
            self.forecast_status = "Draft"
        
        if not self.forecast_type:
            self.forecast_type = "Sales"
        
        if not self.forecast_priority:
            self.forecast_priority = "Medium"
        
        if not self.forecast_confidence:
            self.forecast_confidence = 50

    def calculate_forecast_metrics(self):
        """Calculate forecast metrics"""
        # Calculate forecast totals
        self.calculate_forecast_totals()
        
        # Calculate forecast accuracy
        self.calculate_forecast_accuracy()
        
        # Calculate forecast variance
        self.calculate_forecast_variance()
        
        # Calculate forecast performance
        self.calculate_forecast_performance()

    def calculate_forecast_totals(self):
        """Calculate forecast totals"""
        total_forecast = 0
        total_actual = 0
        total_variance = 0
        
        for period in self.forecast_periods:
            period.forecast_amount = period.forecast_quantity * period.forecast_rate
            period.actual_amount = period.actual_quantity * period.actual_rate
            period.variance_amount = period.forecast_amount - period.actual_amount
            period.variance_percentage = (period.variance_amount / period.forecast_amount) * 100 if period.forecast_amount > 0 else 0
            
            total_forecast += period.forecast_amount
            total_actual += period.actual_amount
            total_variance += period.variance_amount
        
        self.total_forecast = total_forecast
        self.total_actual = total_actual
        self.total_variance = total_variance

    def calculate_forecast_accuracy(self):
        """Calculate forecast accuracy"""
        if self.total_forecast > 0:
            accuracy = (1 - abs(self.total_variance) / self.total_forecast) * 100
            self.forecast_accuracy = max(0, min(100, accuracy))
        else:
            self.forecast_accuracy = 0

    def calculate_forecast_variance(self):
        """Calculate forecast variance"""
        if self.total_forecast > 0:
            self.forecast_variance = (self.total_variance / self.total_forecast) * 100
        else:
            self.forecast_variance = 0

    def calculate_forecast_performance(self):
        """Calculate forecast performance"""
        if self.total_forecast > 0:
            performance = (self.total_actual / self.total_forecast) * 100
            self.forecast_performance = performance
        else:
            self.forecast_performance = 0

    def determine_forecast_status(self):
        """Determine forecast status"""
        if self.forecast_status == "Draft":
            self.status = "Draft"
        elif self.forecast_status == "Submitted":
            self.status = "Submitted"
        elif self.forecast_status == "Approved":
            self.status = "Approved"
        elif self.forecast_status == "Active":
            self.status = "Active"
        elif self.forecast_status == "Completed":
            self.status = "Completed"
        else:
            self.status = "Draft"

    def update_forecast_settings(self):
        """Update forecast-specific settings"""
        # Update forecast preferences
        if self.preferences:
            frappe.db.set_value("Forecast", self.name, "preferences", json.dumps(self.preferences))
        
        # Update forecast tags
        if self.tags:
            frappe.db.set_value("Forecast", self.name, "tags", json.dumps(self.tags))

    def setup_forecast_permissions(self):
        """Setup forecast-specific permissions"""
        # Create forecast-specific roles
        forecast_roles = [
            f"Forecast - {self.forecast_id}",
            f"User - {self.assigned_to}",
            f"Status - {self.forecast_status}"
        ]
        
        for role_name in forecast_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def generate_forecast_insights(self):
        """Generate forecast insights"""
        insights = {
            "forecast_status": self.forecast_status,
            "accuracy_analysis": self.analyze_accuracy(),
            "variance_analysis": self.analyze_variance(),
            "performance_analysis": self.analyze_performance(),
            "trend_analysis": self.analyze_trends(),
            "next_actions": self.recommend_next_actions(),
            "ai_recommendations": self.get_ai_recommendations()
        }
        
        self.forecast_insights = json.dumps(insights)

    def analyze_accuracy(self):
        """Analyze forecast accuracy"""
        accuracy_analysis = {
            "overall_accuracy": self.forecast_accuracy,
            "accuracy_trend": self.calculate_accuracy_trend(),
            "accuracy_by_period": self.calculate_accuracy_by_period(),
            "accuracy_benchmarks": self.get_accuracy_benchmarks()
        }
        
        return accuracy_analysis

    def calculate_accuracy_trend(self):
        """Calculate accuracy trend"""
        # Get historical accuracy data
        historical_accuracy = frappe.db.sql("""
            SELECT forecast_accuracy, creation
            FROM `tabForecast`
            WHERE assigned_to = %s
            AND forecast_type = %s
            ORDER BY creation DESC
            LIMIT 5
        """, (self.assigned_to, self.forecast_type), as_dict=True)
        
        if len(historical_accuracy) >= 2:
            recent_accuracy = historical_accuracy[0]['forecast_accuracy']
            previous_accuracy = historical_accuracy[1]['forecast_accuracy']
            
            if recent_accuracy > previous_accuracy:
                return "Improving"
            elif recent_accuracy < previous_accuracy:
                return "Declining"
            else:
                return "Stable"
        else:
            return "New"

    def calculate_accuracy_by_period(self):
        """Calculate accuracy by period"""
        period_accuracy = []
        
        for period in self.forecast_periods:
            if period.forecast_amount > 0:
                accuracy = (1 - abs(period.variance_amount) / period.forecast_amount) * 100
                period_accuracy.append({
                    "period": period.period_name,
                    "accuracy": accuracy
                })
        
        return period_accuracy

    def get_accuracy_benchmarks(self):
        """Get accuracy benchmarks"""
        benchmarks = {
            "excellent": 90,
            "good": 80,
            "average": 70,
            "poor": 60
        }
        
        return benchmarks

    def analyze_variance(self):
        """Analyze forecast variance"""
        variance_analysis = {
            "overall_variance": self.forecast_variance,
            "variance_trend": self.calculate_variance_trend(),
            "variance_by_period": self.calculate_variance_by_period(),
            "variance_causes": self.identify_variance_causes()
        }
        
        return variance_analysis

    def calculate_variance_trend(self):
        """Calculate variance trend"""
        # Get historical variance data
        historical_variance = frappe.db.sql("""
            SELECT forecast_variance, creation
            FROM `tabForecast`
            WHERE assigned_to = %s
            AND forecast_type = %s
            ORDER BY creation DESC
            LIMIT 5
        """, (self.assigned_to, self.forecast_type), as_dict=True)
        
        if len(historical_variance) >= 2:
            recent_variance = historical_variance[0]['forecast_variance']
            previous_variance = historical_variance[1]['forecast_variance']
            
            if abs(recent_variance) < abs(previous_variance):
                return "Improving"
            elif abs(recent_variance) > abs(previous_variance):
                return "Worsening"
            else:
                return "Stable"
        else:
            return "New"

    def calculate_variance_by_period(self):
        """Calculate variance by period"""
        period_variance = []
        
        for period in self.forecast_periods:
            period_variance.append({
                "period": period.period_name,
                "variance": period.variance_percentage
            })
        
        return period_variance

    def identify_variance_causes(self):
        """Identify variance causes"""
        causes = []
        
        # Analyze variance patterns
        if self.forecast_variance > 10:
            causes.append("Over-forecasting")
        elif self.forecast_variance < -10:
            causes.append("Under-forecasting")
        
        # Analyze seasonal patterns
        seasonal_variance = self.analyze_seasonal_variance()
        if seasonal_variance:
            causes.append("Seasonal variations")
        
        # Analyze market conditions
        market_variance = self.analyze_market_variance()
        if market_variance:
            causes.append("Market conditions")
        
        return causes

    def analyze_seasonal_variance(self):
        """Analyze seasonal variance"""
        # Implementation for seasonal analysis
        return False

    def analyze_market_variance(self):
        """Analyze market variance"""
        # Implementation for market analysis
        return False

    def analyze_performance(self):
        """Analyze forecast performance"""
        performance_analysis = {
            "overall_performance": self.forecast_performance,
            "performance_trend": self.calculate_performance_trend(),
            "performance_by_period": self.calculate_performance_by_period(),
            "performance_benchmarks": self.get_performance_benchmarks()
        }
        
        return performance_analysis

    def calculate_performance_trend(self):
        """Calculate performance trend"""
        # Get historical performance data
        historical_performance = frappe.db.sql("""
            SELECT forecast_performance, creation
            FROM `tabForecast`
            WHERE assigned_to = %s
            AND forecast_type = %s
            ORDER BY creation DESC
            LIMIT 5
        """, (self.assigned_to, self.forecast_type), as_dict=True)
        
        if len(historical_performance) >= 2:
            recent_performance = historical_performance[0]['forecast_performance']
            previous_performance = historical_performance[1]['forecast_performance']
            
            if recent_performance > previous_performance:
                return "Improving"
            elif recent_performance < previous_performance:
                return "Declining"
            else:
                return "Stable"
        else:
            return "New"

    def calculate_performance_by_period(self):
        """Calculate performance by period"""
        period_performance = []
        
        for period in self.forecast_periods:
            if period.forecast_amount > 0:
                performance = (period.actual_amount / period.forecast_amount) * 100
                period_performance.append({
                    "period": period.period_name,
                    "performance": performance
                })
        
        return period_performance

    def get_performance_benchmarks(self):
        """Get performance benchmarks"""
        benchmarks = {
            "excellent": 110,
            "good": 100,
            "average": 90,
            "poor": 80
        }
        
        return benchmarks

    def analyze_trends(self):
        """Analyze forecast trends"""
        trend_analysis = {
            "forecast_trend": self.calculate_forecast_trend(),
            "actual_trend": self.calculate_actual_trend(),
            "variance_trend": self.calculate_variance_trend(),
            "seasonal_trends": self.analyze_seasonal_trends()
        }
        
        return trend_analysis

    def calculate_forecast_trend(self):
        """Calculate forecast trend"""
        # Analyze forecast values over time
        forecast_values = [period.forecast_amount for period in self.forecast_periods]
        
        if len(forecast_values) >= 2:
            if forecast_values[-1] > forecast_values[0]:
                return "Increasing"
            elif forecast_values[-1] < forecast_values[0]:
                return "Decreasing"
            else:
                return "Stable"
        else:
            return "Insufficient Data"

    def calculate_actual_trend(self):
        """Calculate actual trend"""
        # Analyze actual values over time
        actual_values = [period.actual_amount for period in self.forecast_periods]
        
        if len(actual_values) >= 2:
            if actual_values[-1] > actual_values[0]:
                return "Increasing"
            elif actual_values[-1] < actual_values[0]:
                return "Decreasing"
            else:
                return "Stable"
        else:
            return "Insufficient Data"

    def analyze_seasonal_trends(self):
        """Analyze seasonal trends"""
        # Implementation for seasonal trend analysis
        return {}

    def recommend_next_actions(self):
        """Recommend next actions"""
        actions = []
        
        if self.forecast_status == "Draft":
            actions.append("Review forecast details")
            actions.append("Submit for approval")
            actions.append("Share with team")
        elif self.forecast_status == "Submitted":
            actions.append("Wait for approval")
            actions.append("Address feedback")
            actions.append("Update forecast if needed")
        elif self.forecast_status == "Approved":
            actions.append("Activate forecast")
            actions.append("Monitor progress")
            actions.append("Update regularly")
        elif self.forecast_status == "Active":
            actions.append("Track performance")
            actions.append("Update forecast")
            actions.append("Address variances")
        else:
            actions.append("Review forecast status")
            actions.append("Take appropriate action")
        
        return actions

    def get_ai_recommendations(self):
        """Get AI recommendations"""
        recommendations = []
        
        # Analyze forecast accuracy
        if self.forecast_accuracy < 70:
            recommendations.append("Improve forecast accuracy")
            recommendations.append("Review forecasting methods")
            recommendations.append("Consider additional data sources")
        
        # Analyze variance
        if abs(self.forecast_variance) > 15:
            recommendations.append("Reduce forecast variance")
            recommendations.append("Improve forecasting models")
            recommendations.append("Consider market factors")
        
        # Analyze performance
        if self.forecast_performance < 90:
            recommendations.append("Improve forecast performance")
            recommendations.append("Review forecast assumptions")
            recommendations.append("Consider external factors")
        
        return recommendations

    def create_forecast_profile(self):
        """Create comprehensive forecast profile"""
        profile_data = {
            "forecast_id": self.forecast_id,
            "forecast_name": self.forecast_name,
            "assigned_to": self.assigned_to,
            "forecast_period": self.forecast_period,
            "forecast_start_date": self.forecast_start_date,
            "forecast_end_date": self.forecast_end_date,
            "forecast_status": self.forecast_status,
            "forecast_type": self.forecast_type,
            "forecast_priority": self.forecast_priority,
            "forecast_confidence": self.forecast_confidence,
            "total_forecast": self.total_forecast,
            "total_actual": self.total_actual,
            "total_variance": self.total_variance,
            "forecast_accuracy": self.forecast_accuracy,
            "forecast_variance": self.forecast_variance,
            "forecast_performance": self.forecast_performance
        }
        
        frappe.get_doc({
            "doctype": "Forecast Profile",
            "forecast": self.name,
            "profile_data": json.dumps(profile_data)
        }).insert(ignore_permissions=True)

    def setup_forecast_workflow(self):
        """Setup forecast workflow"""
        workflow_data = {
            "forecast": self.name,
            "workflow_type": "Forecast Management",
            "steps": [
                {"step": "Forecast Creation", "status": "Completed"},
                {"step": "Internal Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Activation", "status": "Pending"},
                {"step": "Monitoring", "status": "Pending"},
                {"step": "Completion", "status": "Pending"}
            ]
        }
        
        frappe.get_doc({
            "doctype": "Forecast Workflow",
            "forecast": self.name,
            "workflow_data": json.dumps(workflow_data)
        }).insert(ignore_permissions=True)

    def create_forecast_analytics(self):
        """Create forecast analytics"""
        analytics_data = {
            "forecast": self.name,
            "analytics_type": "Forecast Analytics",
            "metrics": {
                "total_forecast": self.total_forecast,
                "total_actual": self.total_actual,
                "total_variance": self.total_variance,
                "forecast_accuracy": self.forecast_accuracy,
                "forecast_variance": self.forecast_variance,
                "forecast_performance": self.forecast_performance
            },
            "insights": self.generate_forecast_insights(),
            "created_date": now().isoformat()
        }
        
        frappe.get_doc({
            "doctype": "Forecast Analytics",
            "forecast": self.name,
            "analytics_data": json.dumps(analytics_data)
        }).insert(ignore_permissions=True)

    def initialize_forecast_tracking(self):
        """Initialize forecast tracking"""
        tracking_data = {
            "forecast": self.name,
            "tracking_start_date": now().isoformat(),
            "last_activity": now().isoformat(),
            "activity_count": 0,
            "status_changes": 0,
            "accuracy_updates": 0
        }
        
        frappe.get_doc({
            "doctype": "Forecast Tracking",
            "forecast": self.name,
            "tracking_data": json.dumps(tracking_data)
        }).insert(ignore_permissions=True)

    def update_forecast_analytics(self):
        """Update forecast analytics"""
        # Calculate updated metrics
        updated_metrics = {
            "total_forecast": self.total_forecast,
            "total_actual": self.total_actual,
            "total_variance": self.total_variance,
            "forecast_accuracy": self.forecast_accuracy,
            "forecast_variance": self.forecast_variance,
            "forecast_performance": self.forecast_performance
        }
        
        # Update analytics record
        analytics = frappe.get_doc("Forecast Analytics", {"forecast": self.name})
        if analytics:
            analytics.analytics_data = json.dumps({
                "forecast": self.name,
                "analytics_type": "Forecast Analytics",
                "metrics": updated_metrics,
                "insights": self.generate_forecast_insights(),
                "updated_date": now().isoformat()
            })
            analytics.save()

    def sync_forecast_data(self):
        """Sync forecast data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def update_forecast_status(self):
        """Update forecast status"""
        # Log status change
        self.log_status_change()
        
        # Update tracking
        tracking = frappe.get_doc("Forecast Tracking", {"forecast": self.name})
        if tracking:
            tracking.status_changes += 1
            tracking.last_activity = now()
            tracking.save()

    def process_forecast_changes(self):
        """Process forecast changes"""
        # Log forecast changes
        self.log_forecast_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_status_change(self):
        """Log status change"""
        frappe.get_doc({
            "doctype": "Forecast Status Change",
            "forecast": self.name,
            "old_status": self.get_previous_status(),
            "new_status": self.forecast_status,
            "change_date": now(),
            "changed_by": frappe.session.user
        }).insert(ignore_permissions=True)

    def get_previous_status(self):
        """Get previous status"""
        previous_status = frappe.db.sql("""
            SELECT new_status
            FROM `tabForecast Status Change`
            WHERE forecast = %s
            ORDER BY creation DESC
            LIMIT 1
        """, self.name)[0][0] if frappe.db.exists("Forecast Status Change", {"forecast": self.name}) else "New"
        
        return previous_status

    def log_forecast_changes(self):
        """Log forecast changes"""
        frappe.get_doc({
            "doctype": "Forecast Change Log",
            "forecast": self.name,
            "change_type": "Update",
            "change_description": "Forecast information updated",
            "changed_by": frappe.session.user,
            "change_date": now()
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update user records
        self.update_user_records()
        
        # Update team records
        self.update_team_records()

    def update_user_records(self):
        """Update user records"""
        # Update user forecast count
        frappe.db.sql("""
            UPDATE `tabUser`
            SET forecast_count = (
                SELECT COUNT(*) FROM `tabForecast`
                WHERE assigned_to = %s AND status = 'Active'
            )
            WHERE name = %s
        """, (self.assigned_to, self.assigned_to))

    def update_team_records(self):
        """Update team records"""
        # Update team forecast count
        if self.team:
            frappe.db.sql("""
                UPDATE `tabTeam`
                SET forecast_count = (
                    SELECT COUNT(*) FROM `tabForecast`
                    WHERE team = %s AND status = 'Active'
                )
                WHERE name = %s
            """, (self.team, self.team))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify assigned user
        self.notify_assigned_user()
        
        # Notify team members
        self.notify_team_members()

    def notify_assigned_user(self):
        """Notify assigned user"""
        frappe.get_doc({
            "doctype": "Forecast Notification",
            "forecast": self.name,
            "notification_type": "Forecast Update",
            "message": f"Forecast {self.forecast_name} has been updated",
            "recipients": self.assigned_to,
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_team_members(self):
        """Notify team members"""
        if self.team:
            frappe.get_doc({
                "doctype": "Forecast Notification",
                "forecast": self.name,
                "notification_type": "Forecast Update",
                "message": f"Forecast {self.forecast_name} has been updated",
                "recipients": f"Team - {self.team}",
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync forecast data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_forecast_dashboard_data(self):
        """Get forecast dashboard data"""
        return {
            "forecast_id": self.forecast_id,
            "forecast_name": self.forecast_name,
            "assigned_to": self.assigned_to,
            "forecast_period": self.forecast_period,
            "forecast_start_date": self.forecast_start_date,
            "forecast_end_date": self.forecast_end_date,
            "forecast_status": self.forecast_status,
            "forecast_type": self.forecast_type,
            "forecast_priority": self.forecast_priority,
            "forecast_confidence": self.forecast_confidence,
            "total_forecast": self.total_forecast,
            "total_actual": self.total_actual,
            "total_variance": self.total_variance,
            "forecast_accuracy": self.forecast_accuracy,
            "forecast_variance": self.forecast_variance,
            "forecast_performance": self.forecast_performance,
            "insights": self.generate_forecast_insights()
        }

    @frappe.whitelist()
    def update_forecast_period(self, period_data):
        """Update forecast period"""
        for period in self.forecast_periods:
            if period.period_name == period_data['period_name']:
                period.forecast_quantity = period_data['forecast_quantity']
                period.forecast_rate = period_data['forecast_rate']
                period.actual_quantity = period_data['actual_quantity']
                period.actual_rate = period_data['actual_rate']
                break
        
        # Recalculate totals
        self.calculate_forecast_totals()
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Forecast period updated successfully"
        }

    @frappe.whitelist()
    def approve_forecast(self, approver_notes=None):
        """Approve forecast"""
        if self.forecast_status != "Draft":
            return {
                "status": "error",
                "message": "Only draft forecasts can be approved"
            }
        
        self.forecast_status = "Approved"
        self.approver = frappe.session.user
        self.approval_date = now()
        self.approver_notes = approver_notes
        
        # Log approval
        frappe.get_doc({
            "doctype": "Forecast Approval",
            "forecast": self.name,
            "approver": frappe.session.user,
            "approval_date": now(),
            "approver_notes": approver_notes
        }).insert(ignore_permissions=True)
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Forecast approved successfully"
        }

    @frappe.whitelist()
    def activate_forecast(self):
        """Activate forecast"""
        if self.forecast_status != "Approved":
            return {
                "status": "error",
                "message": "Only approved forecasts can be activated"
            }
        
        self.forecast_status = "Active"
        self.activation_date = now()
        self.activated_by = frappe.session.user
        
        # Log activation
        frappe.get_doc({
            "doctype": "Forecast Activation",
            "forecast": self.name,
            "activated_by": frappe.session.user,
            "activation_date": now()
        }).insert(ignore_permissions=True)
        
        # Save changes
        self.save()
        
        return {
            "status": "success",
            "message": "Forecast activated successfully"
        }

    @frappe.whitelist()
    def get_forecast_insights(self):
        """Get forecast insights"""
        return {
            "forecast_status": self.forecast_status,
            "accuracy_analysis": self.analyze_accuracy(),
            "variance_analysis": self.analyze_variance(),
            "performance_analysis": self.analyze_performance(),
            "trend_analysis": self.analyze_trends(),
            "next_actions": self.recommend_next_actions(),
            "ai_recommendations": self.get_ai_recommendations()
        }
