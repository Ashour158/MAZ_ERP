# CRM Module Hooks

from frappe import _

app_name = "crm"
app_title = "Advanced Customer Relationship Management"
app_publisher = "ERPNext Team"
app_description = "Complete CRM system with customer management, sales pipeline, marketing automation, customer service, and AI-powered analytics"
app_icon = "octicon octicon-people"
app_color = "blue"
app_email = "crm@erpnext.com"
app_license = "MIT"

# Includes in <head>
# ------------------

app_include_css = "/assets/crm/css/crm.css"
app_include_js = "/assets/crm/js/crm.js"

# include js, css files in header of web template
web_include_css = "/assets/crm/css/crm.css"
web_include_js = "/assets/crm/js/crm.js"

# include custom scss in every website theme (without file extension ".scss")
website_theme_scss = "crm/public/scss/website"

# include js, css files in header of web form
webform_include_js = {"doctype": "public/js/doctype.js"}
webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
role_home_page = {
	"Sales Manager": "crm-dashboard",
	"Sales Representative": "crm-dashboard",
	"Marketing Manager": "crm-dashboard",
	"Customer Service": "crm-dashboard",
	"CRM User": "crm-dashboard"
}

# Generators
# ----------

# automatically create page for each record of this doctype
website_generators = ["Customer", "Lead", "Opportunity", "Campaign"]

# Installation
# ------------

before_install = "crm.install.before_install"
after_install = "crm.install.after_install"

# Uninstallation
# ---------------

before_uninstall = "crm.uninstall.before_uninstall"
after_uninstall = "crm.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "crm.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Customer": "crm.permissions.get_customer_permission_query_conditions",
	"Lead": "crm.permissions.get_lead_permission_query_conditions",
	"Opportunity": "crm.permissions.get_opportunity_permission_query_conditions",
	"Campaign": "crm.permissions.get_campaign_permission_query_conditions",
	"Contact": "crm.permissions.get_contact_permission_query_conditions",
	"Address": "crm.permissions.get_address_permission_query_conditions"
}

has_permission = {
	"Customer": "crm.permissions.has_customer_permission",
	"Lead": "crm.permissions.has_lead_permission",
	"Opportunity": "crm.permissions.has_opportunity_permission",
	"Campaign": "crm.permissions.has_campaign_permission",
	"Contact": "crm.permissions.has_contact_permission",
	"Address": "crm.permissions.has_address_permission"
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Customer": "crm.doctype.customer.customer.Customer",
	"Lead": "crm.doctype.lead.lead.Lead",
	"Opportunity": "crm.doctype.opportunity.opportunity.Opportunity",
	"Campaign": "crm.doctype.campaign.campaign.Campaign"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Customer": {
		"on_update": "crm.events.customer_events.on_customer_update",
		"on_cancel": "crm.events.customer_events.on_customer_cancel",
		"on_trash": "crm.events.customer_events.on_customer_trash"
	},
	"Lead": {
		"on_update": "crm.events.lead_events.on_lead_update",
		"on_cancel": "crm.events.lead_events.on_lead_cancel",
		"on_trash": "crm.events.lead_events.on_lead_trash"
	},
	"Opportunity": {
		"on_update": "crm.events.opportunity_events.on_opportunity_update",
		"on_cancel": "crm.events.opportunity_events.on_opportunity_cancel",
		"on_trash": "crm.events.opportunity_events.on_opportunity_trash"
	},
	"Campaign": {
		"on_update": "crm.events.campaign_events.on_campaign_update",
		"on_cancel": "crm.events.campaign_events.on_campaign_cancel",
		"on_trash": "crm.events.campaign_events.on_campaign_trash"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"crm.tasks.daily.update_customer_health_scores",
		"crm.tasks.daily.process_lead_scoring",
		"crm.tasks.daily.update_opportunity_stages",
		"crm.tasks.daily.send_campaign_emails",
		"crm.tasks.daily.update_customer_analytics"
	],
	"hourly": [
		"crm.tasks.hourly.check_lead_qualification",
		"crm.tasks.hourly.update_opportunity_probability",
		"crm.tasks.hourly.process_campaign_responses"
	],
	"weekly": [
		"crm.tasks.weekly.generate_sales_reports",
		"crm.tasks.weekly.analyze_customer_trends",
		"crm.tasks.weekly.update_marketing_analytics"
	],
	"monthly": [
		"crm.tasks.monthly.generate_crm_analytics",
		"crm.tasks.monthly.update_customer_segments",
		"crm.tasks.monthly.analyze_sales_performance"
	]
}

# Testing
# -------

before_tests = "crm.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"frappe.desk.doctype.event.event.get_events": "crm.event.get_events"
}

# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Customer": "crm.doctype.customer.customer.get_dashboard_data",
	"Lead": "crm.doctype.lead.lead.get_dashboard_data",
	"Opportunity": "crm.doctype.opportunity.opportunity.get_dashboard_data",
	"Campaign": "crm.doctype.campaign.campaign.get_dashboard_data"
}

# exempt linked doctypes from auto deletion
auto_delete_linked_doctypes = ["Customer Segment", "Lead Source", "Opportunity Type", "Campaign Type"]

# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "Customer",
		"filter_by": "owner",
		"redact_fields": ["email", "phone", "mobile_no"],
		"partial": 1,
	},
	{
		"doctype": "Lead",
		"filter_by": "owner",
		"partial": 1,
	},
	{
		"doctype": "Opportunity",
		"filter_by": "owner",
		"strict": False,
	},
	{
		"doctype": "Campaign"
	}
]

# Authentication and authorization
# --------------------------------

auth_hooks = [
	"crm.auth.validate"
]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
translated_search_doctypes = ["Customer", "Lead", "Opportunity", "Campaign"]
