# Enhanced Company DocType with Multi-Company Support

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class Company(Document):
    def autoname(self):
        """Generate unique company code"""
        if not self.company_code:
            self.company_code = make_autoname("COMP-.YYYY.-.MM.-.#####")
        self.name = self.company_code

    def validate(self):
        """Validate company data"""
        self.validate_company_data()
        self.set_defaults()
        self.validate_currency()
        self.validate_tax_settings()
        self.validate_bank_settings()

    def before_save(self):
        """Process before saving"""
        self.update_company_settings()
        self.setup_default_accounts()
        self.setup_default_currencies()

    def after_insert(self):
        """Process after inserting new company"""
        self.create_default_accounts()
        self.create_default_currencies()
        self.setup_company_permissions()
        self.create_company_dashboard()

    def on_update(self):
        """Process on company update"""
        self.update_company_analytics()
        self.sync_company_data()

    def validate_company_data(self):
        """Validate company information"""
        if not self.company_name:
            frappe.throw(_("Company name is required"))
        
        if not self.country:
            frappe.throw(_("Country is required"))
        
        if not self.currency:
            frappe.throw(_("Base currency is required"))

    def validate_currency(self):
        """Validate currency settings"""
        if self.currency:
            # Check if currency exists in system
            if not frappe.db.exists("Currency", self.currency):
                frappe.throw(_("Currency {0} does not exist").format(self.currency))
            
            # Validate currency format
            if len(self.currency) != 3:
                frappe.throw(_("Currency code must be 3 characters"))

    def validate_tax_settings(self):
        """Validate tax settings"""
        if self.tax_id and len(self.tax_id) < 5:
            frappe.throw(_("Tax ID must be at least 5 characters"))
        
        if self.vat_number and not self.validate_vat_number():
            frappe.throw(_("Invalid VAT number format"))

    def validate_bank_settings(self):
        """Validate bank settings"""
        if self.bank_account:
            # Validate bank account format
            if not self.validate_bank_account():
                frappe.throw(_("Invalid bank account format"))

    def set_defaults(self):
        """Set default values for new company"""
        if not self.company_type:
            self.company_type = "Private Limited"
        
        if not self.industry:
            self.industry = "Manufacturing"
        
        if not self.fiscal_year_start:
            self.fiscal_year_start = "01-01"
        
        if not self.fiscal_year_end:
            self.fiscal_year_end = "12-31"

    def update_company_settings(self):
        """Update company-specific settings"""
        # Update company timezone
        if self.timezone:
            frappe.db.set_value("Company", self.name, "timezone", self.timezone)
        
        # Update company currency
        if self.currency:
            frappe.db.set_value("Company", self.name, "currency", self.currency)
        
        # Update company address
        if self.address:
            frappe.db.set_value("Company", self.name, "address", self.address)

    def setup_default_accounts(self):
        """Setup default chart of accounts"""
        if not self.chart_of_accounts:
            self.chart_of_accounts = "Standard"
        
        # Create default accounts if not exists
        self.create_default_accounts()

    def setup_default_currencies(self):
        """Setup default currencies for company"""
        if not self.enabled_currencies:
            # Add base currency
            self.append("enabled_currencies", {
                "currency": self.currency,
                "is_base": 1,
                "exchange_rate": 1.0
            })

    def create_default_accounts(self):
        """Create default chart of accounts"""
        default_accounts = [
            {
                "account_name": "Cash",
                "account_type": "Asset",
                "parent_account": "Assets",
                "account_code": "1000"
            },
            {
                "account_name": "Bank",
                "account_type": "Asset", 
                "parent_account": "Assets",
                "account_code": "1100"
            },
            {
                "account_name": "Accounts Receivable",
                "account_type": "Asset",
                "parent_account": "Assets", 
                "account_code": "1200"
            },
            {
                "account_name": "Inventory",
                "account_type": "Asset",
                "parent_account": "Assets",
                "account_code": "1300"
            },
            {
                "account_name": "Accounts Payable",
                "account_type": "Liability",
                "parent_account": "Liabilities",
                "account_code": "2000"
            },
            {
                "account_name": "Sales Revenue",
                "account_type": "Income",
                "parent_account": "Income",
                "account_code": "4000"
            },
            {
                "account_name": "Cost of Goods Sold",
                "account_type": "Expense",
                "parent_account": "Expenses",
                "account_code": "5000"
            }
        ]
        
        for account_data in default_accounts:
            if not frappe.db.exists("Account", {"account_name": account_data["account_name"], "company": self.name}):
                account = frappe.get_doc({
                    "doctype": "Account",
                    "account_name": account_data["account_name"],
                    "account_type": account_data["account_type"],
                    "parent_account": account_data["parent_account"],
                    "account_code": account_data["account_code"],
                    "company": self.name,
                    "is_group": 0
                })
                account.insert(ignore_permissions=True)

    def create_default_currencies(self):
        """Create default currency settings"""
        if not frappe.db.exists("Currency Exchange Rate", {"company": self.name}):
            # Create base currency exchange rate
            frappe.get_doc({
                "doctype": "Currency Exchange Rate",
                "company": self.name,
                "from_currency": self.currency,
                "to_currency": self.currency,
                "exchange_rate": 1.0,
                "date": now().date()
            }).insert(ignore_permissions=True)

    def setup_company_permissions(self):
        """Setup company-specific permissions"""
        # Create company-specific roles
        company_roles = [
            "Finance Manager - " + self.company_name,
            "Accountant - " + self.company_name,
            "Finance User - " + self.company_name
        ]
        
        for role_name in company_roles:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_name,
                    "desk_access": 1
                }).insert(ignore_permissions=True)

    def create_company_dashboard(self):
        """Create company-specific dashboard"""
        dashboard_data = {
            "company": self.name,
            "dashboard_name": f"{self.company_name} Dashboard",
            "charts": [
                {
                    "chart_name": "Revenue Trend",
                    "chart_type": "line",
                    "data_source": "Journal Entry"
                },
                {
                    "chart_name": "Expense Breakdown", 
                    "chart_type": "pie",
                    "data_source": "Journal Entry"
                },
                {
                    "chart_name": "Cash Flow",
                    "chart_type": "bar",
                    "data_source": "Payment Entry"
                }
            ]
        }
        
        frappe.get_doc({
            "doctype": "Company Dashboard",
            "company": self.name,
            "dashboard_data": json.dumps(dashboard_data)
        }).insert(ignore_permissions=True)

    def update_company_analytics(self):
        """Update company analytics"""
        # Calculate company metrics
        metrics = self.calculate_company_metrics()
        
        # Update analytics
        frappe.db.set_value("Company", self.name, "analytics", json.dumps(metrics))

    def sync_company_data(self):
        """Sync company data across systems"""
        # Sync with external systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def calculate_company_metrics(self):
        """Calculate company performance metrics"""
        # Get financial data
        revenue = self.get_total_revenue()
        expenses = self.get_total_expenses()
        profit = revenue - expenses
        
        # Calculate ratios
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
        expense_ratio = (expenses / revenue * 100) if revenue > 0 else 0
        
        return {
            "total_revenue": revenue,
            "total_expenses": expenses,
            "net_profit": profit,
            "profit_margin": profit_margin,
            "expense_ratio": expense_ratio,
            "last_updated": now().isoformat()
        }

    def get_total_revenue(self):
        """Get total revenue for company"""
        return frappe.db.sql("""
            SELECT SUM(debit) 
            FROM `tabGL Entry` 
            WHERE company = %s 
            AND account_type = 'Income'
            AND posting_date >= %s
        """, (self.name, self.fiscal_year_start))[0][0] or 0

    def get_total_expenses(self):
        """Get total expenses for company"""
        return frappe.db.sql("""
            SELECT SUM(credit) 
            FROM `tabGL Entry` 
            WHERE company = %s 
            AND account_type = 'Expense'
            AND posting_date >= %s
        """, (self.name, self.fiscal_year_start))[0][0] or 0

    def validate_vat_number(self):
        """Validate VAT number format"""
        # Basic VAT number validation
        if len(self.vat_number) < 8:
            return False
        
        # Check for valid characters
        if not self.vat_number.replace("-", "").replace(" ", "").isalnum():
            return False
        
        return True

    def validate_bank_account(self):
        """Validate bank account format"""
        # Basic bank account validation
        if len(self.bank_account) < 10:
            return False
        
        # Check for valid characters
        if not self.bank_account.replace("-", "").replace(" ", "").isdigit():
            return False
        
        return True

    def sync_with_external_system(self):
        """Sync company data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_company_dashboard_data(self):
        """Get company dashboard data"""
        return {
            "company_name": self.company_name,
            "currency": self.currency,
            "fiscal_year": self.fiscal_year_start + " to " + self.fiscal_year_end,
            "metrics": self.calculate_company_metrics(),
            "recent_transactions": self.get_recent_transactions(),
            "financial_summary": self.get_financial_summary()
        }

    def get_recent_transactions(self):
        """Get recent transactions for company"""
        return frappe.db.sql("""
            SELECT 
                name, 
                posting_date, 
                total_debit, 
                total_credit,
                voucher_type
            FROM `tabJournal Entry` 
            WHERE company = %s 
            ORDER BY posting_date DESC 
            LIMIT 10
        """, self.name, as_dict=True)

    def get_financial_summary(self):
        """Get financial summary for company"""
        return {
            "total_assets": self.get_total_assets(),
            "total_liabilities": self.get_total_liabilities(),
            "total_equity": self.get_total_equity(),
            "current_ratio": self.get_current_ratio()
        }

    def get_total_assets(self):
        """Get total assets"""
        return frappe.db.sql("""
            SELECT SUM(debit) - SUM(credit)
            FROM `tabGL Entry` 
            WHERE company = %s 
            AND account_type = 'Asset'
        """, self.name)[0][0] or 0

    def get_total_liabilities(self):
        """Get total liabilities"""
        return frappe.db.sql("""
            SELECT SUM(credit) - SUM(debit)
            FROM `tabGL Entry` 
            WHERE company = %s 
            AND account_type = 'Liability'
        """, self.name)[0][0] or 0

    def get_total_equity(self):
        """Get total equity"""
        return frappe.db.sql("""
            SELECT SUM(credit) - SUM(debit)
            FROM `tabGL Entry` 
            WHERE company = %s 
            AND account_type = 'Equity'
        """, self.name)[0][0] or 0

    def get_current_ratio(self):
        """Get current ratio"""
        current_assets = self.get_current_assets()
        current_liabilities = self.get_current_liabilities()
        
        if current_liabilities > 0:
            return current_assets / current_liabilities
        return 0

    def get_current_assets(self):
        """Get current assets"""
        return frappe.db.sql("""
            SELECT SUM(debit) - SUM(credit)
            FROM `tabGL Entry` 
            WHERE company = %s 
            AND account_type = 'Asset'
            AND is_current_asset = 1
        """, self.name)[0][0] or 0

    def get_current_liabilities(self):
        """Get current liabilities"""
        return frappe.db.sql("""
            SELECT SUM(credit) - SUM(debit)
            FROM `tabGL Entry` 
            WHERE company = %s 
            AND account_type = 'Liability'
            AND is_current_liability = 1
        """, self.name)[0][0] or 0
