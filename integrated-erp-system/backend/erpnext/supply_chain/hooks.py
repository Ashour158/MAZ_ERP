# Supply Chain Module Hooks

from frappe import _

app_name = "supply_chain"
app_title = "Supply Chain Management"
app_publisher = "ERPNext Team"
app_description = "Intelligent supply chain management with AI-powered features"
app_icon = "octicon octicon-package"
app_color = "green"
app_email = "support@erpnext.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/supply_chain/css/supply_chain.css"
# app_include_js = "/assets/supply_chain/js/supply_chain.js"

# include js, css files in header of web template
# web_include_css = "/assets/supply_chain/css/supply_chain.css"
# web_include_js = "/assets/supply_chain/js/supply_chain.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "supply_chain/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "supply_chain.install.before_install"
# after_install = "supply_chain.install.after_install"

# Uninstallation
# ---------------

# before_uninstall = "supply_chain.uninstall.before_uninstall"
# after_uninstall = "supply_chain.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "supply_chain.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"supply_chain.tasks.daily.generate_reorder_recommendations",
		"supply_chain.tasks.daily.update_vendor_performance",
		"supply_chain.tasks.daily.analyze_inventory_trends"
	],
	"hourly": [
		"supply_chain.tasks.hourly.check_low_stock_alerts",
		"supply_chain.tasks.hourly.update_ai_models"
	],
	"weekly": [
		"supply_chain.tasks.weekly.generate_supply_chain_analytics",
		"supply_chain.tasks.weekly.optimize_reorder_policies"
	]
}

# Testing
# -------

# before_tests = "supply_chain.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "supply_chain.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "supply_chain.task.get_dashboard_data"
# }

# exempt linked doctypes from auto deletion
# auto_delete_linked_doctypes = ["Auto Delete"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"supply_chain.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
