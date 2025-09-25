# Enhanced Maintenance Module Hooks

from frappe import _

app_name = "maintenance"
app_title = "Enhanced Maintenance"
app_publisher = "ERPNext Team"
app_description = "Advanced maintenance management with AI-powered features"
app_icon = "octicon octicon-tools"
app_color = "blue"
app_email = "support@erpnext.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/maintenance/css/maintenance.css"
# app_include_js = "/assets/maintenance/js/maintenance.js"

# include js, css files in header of web template
# web_include_css = "/assets/maintenance/css/maintenance.css"
# web_include_js = "/assets/maintenance/js/maintenance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "maintenance/public/scss/website"

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

# before_install = "maintenance.install.before_install"
# after_install = "maintenance.install.after_install"

# Uninstallation
# ---------------

# before_uninstall = "maintenance.uninstall.before_uninstall"
# after_uninstall = "maintenance.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "maintenance.notifications.get_notification_config"

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

# scheduler_events = {
# 	"all": [
# 		"maintenance.tasks.all"
# 	],
# 	"daily": [
# 		"maintenance.tasks.daily"
# 	],
# 	"hourly": [
# 		"maintenance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"maintenance.tasks.weekly"
# 	]
# 	"monthly": [
# 		"maintenance.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "maintenance.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "maintenance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "maintenance.task.get_dashboard_data"
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
# 	"maintenance.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
