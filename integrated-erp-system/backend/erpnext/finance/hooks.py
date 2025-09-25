# Finance Module Hooks

from frappe import _

app_name = "finance"
app_title = "Advanced Finance Management"
app_publisher = "ERPNext Team"
app_description = "Complete financial management system with multi-company support, multi-currency, and advanced accounting features"
app_icon = "octicon octicon-credit-card"
app_color = "blue"
app_email = "finance@erpnext.com"
app_license = "MIT"

# Includes in <head>
# ------------------

app_include_css = "/assets/finance/css/finance.css"
app_include_js = "/assets/finance/js/finance.js"

# include js, css files in header of web template
web_include_css = "/assets/finance/css/finance.css"
web_include_js = "/assets/finance/js/finance.js"

# include custom scss in every website theme (without file extension ".scss")
website_theme_scss = "finance/public/scss/website"

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
	"Finance Manager": "finance-dashboard",
	"Accountant": "finance-dashboard",
	"Finance User": "finance-dashboard"
}

# Generators
# ----------

# automatically create page for each record of this doctype
website_generators = ["Financial Statement", "Invoice Template"]

# Installation
# ------------

before_install = "finance.install.before_install"
after_install = "finance.install.after_install"

# Uninstallation
# ---------------

before_uninstall = "finance.uninstall.before_uninstall"
after_uninstall = "finance.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "finance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Company": "finance.permissions.get_company_permission_query_conditions",
	"Account": "finance.permissions.get_account_permission_query_conditions",
	"Journal Entry": "finance.permissions.get_journal_entry_permission_query_conditions",
	"Payment Entry": "finance.permissions.get_payment_entry_permission_query_conditions",
	"Invoice": "finance.permissions.get_invoice_permission_query_conditions"
}

has_permission = {
	"Company": "finance.permissions.has_company_permission",
	"Account": "finance.permissions.has_account_permission",
	"Journal Entry": "finance.permissions.has_journal_entry_permission",
	"Payment Entry": "finance.permissions.has_payment_entry_permission",
	"Invoice": "finance.permissions.has_invoice_permission"
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Company": "finance.doctype.company.company.Company",
	"Account": "finance.doctype.account.account.Account",
	"Journal Entry": "finance.doctype.journal_entry.journal_entry.JournalEntry"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Company": {
		"on_update": "finance.events.company_events.on_company_update",
		"on_cancel": "finance.events.company_events.on_company_cancel",
		"on_trash": "finance.events.company_events.on_company_trash"
	},
	"Account": {
		"on_update": "finance.events.account_events.on_account_update",
		"on_cancel": "finance.events.account_events.on_account_cancel"
	},
	"Journal Entry": {
		"on_submit": "finance.events.journal_entry_events.on_journal_entry_submit",
		"on_cancel": "finance.events.journal_entry_events.on_journal_entry_cancel"
	},
	"Payment Entry": {
		"on_submit": "finance.events.payment_entry_events.on_payment_entry_submit",
		"on_cancel": "finance.events.payment_entry_events.on_payment_entry_cancel"
	},
	"Invoice": {
		"on_submit": "finance.events.invoice_events.on_invoice_submit",
		"on_cancel": "finance.events.invoice_events.on_invoice_cancel"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"finance.tasks.daily.update_exchange_rates",
		"finance.tasks.daily.generate_financial_reports",
		"finance.tasks.daily.process_recurring_invoices",
		"finance.tasks.daily.update_account_balances"
	],
	"hourly": [
		"finance.tasks.hourly.check_payment_status",
		"finance.tasks.hourly.update_currency_rates"
	],
	"weekly": [
		"finance.tasks.weekly.generate_weekly_reports",
		"finance.tasks.weekly.analyze_financial_trends"
	],
	"monthly": [
		"finance.tasks.monthly.generate_monthly_reports",
		"finance.tasks.monthly.close_accounting_periods",
		"finance.tasks.monthly.generate_tax_reports"
	]
}

# Testing
# -------

before_tests = "finance.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"frappe.desk.doctype.event.event.get_events": "finance.event.get_events"
}

# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Company": "finance.doctype.company.company.get_dashboard_data",
	"Account": "finance.doctype.account.account.get_dashboard_data",
	"Journal Entry": "finance.doctype.journal_entry.journal_entry.get_dashboard_data"
}

# exempt linked doctypes from auto deletion
auto_delete_linked_doctypes = ["Financial Statement", "Invoice Template"]

# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "Company",
		"filter_by": "owner",
		"redact_fields": ["tax_id", "bank_account"],
		"partial": 1,
	},
	{
		"doctype": "Account",
		"filter_by": "company",
		"partial": 1,
	},
	{
		"doctype": "Journal Entry",
		"filter_by": "company",
		"strict": False,
	},
	{
		"doctype": "Invoice"
	}
]

# Authentication and authorization
# --------------------------------

auth_hooks = [
	"finance.auth.validate"
]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
translated_search_doctypes = ["Company", "Account", "Currency"]
