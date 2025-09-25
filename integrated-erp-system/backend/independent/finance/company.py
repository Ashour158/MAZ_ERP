# Independent Company Class - Frappe-Free
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.base_document import BaseDocument
from core.validation import ValidationSystem
from core.utils import Utils
from typing import Dict, Any, List

class Company(BaseDocument):
    """Frappe-independent Company class"""
    
    def __init__(self, data: Dict[str, Any] = None):
        super().__init__(data)
    
    def validate(self):
        """Validate company data"""
        self.validate_company_data()
        self.set_defaults()
        self.calculate_financial_metrics()
        self.setup_multi_currency()
    
    def validate_company_data(self):
        """Validate company information"""
        ValidationSystem.validate_required(self.data.get('company_name'), "Company name")
        ValidationSystem.validate_required(self.data.get('company_type'), "Company type")
        ValidationSystem.validate_required(self.data.get('currency'), "Currency")
        
        if self.data.get('email') and not ValidationSystem.validate_email(self.data['email']):
            ValidationSystem.throw("Invalid email format")
    
    def set_defaults(self):
        """Set default values"""
        if not self.data.get('company_status'):
            self.data['company_status'] = "Active"
        if not self.data.get('fiscal_year_start'):
            self.data['fiscal_year_start'] = "2024-01-01"
        if not self.data.get('fiscal_year_end'):
            self.data['fiscal_year_end'] = "2024-12-31"
    
    def calculate_financial_metrics(self):
        """Calculate financial metrics"""
        self.data['total_revenue'] = self.calculate_total_revenue()
        self.data['total_expenses'] = self.calculate_total_expenses()
        self.data['net_profit'] = self.data['total_revenue'] - self.data['total_expenses']
        self.data['profit_margin'] = (self.data['net_profit'] / self.data['total_revenue']) * 100 if self.data['total_revenue'] > 0 else 0
    
    def calculate_total_revenue(self) -> float:
        """Calculate total revenue"""
        # Placeholder - implement actual logic
        return 1000000.0
    
    def calculate_total_expenses(self) -> float:
        """Calculate total expenses"""
        # Placeholder - implement actual logic
        return 750000.0
    
    def setup_multi_currency(self):
        """Setup multi-currency support"""
        base_currency = self.data.get('currency', 'USD')
        supported_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']
        
        currency_rates = {}
        for currency in supported_currencies:
            if currency == base_currency:
                currency_rates[currency] = 1.0
            else:
                # Placeholder rates - in real system, fetch from API
                currency_rates[currency] = 0.85 if currency == 'EUR' else 0.75
        
        self.data['currency_rates'] = currency_rates
        self.data['supported_currencies'] = supported_currencies
    
    def generate_financial_statements(self):
        """Generate financial statements"""
        statements = {
            'profit_loss': self.generate_profit_loss_statement(),
            'balance_sheet': self.generate_balance_sheet(),
            'cash_flow': self.generate_cash_flow_statement()
        }
        return statements
    
    def generate_profit_loss_statement(self) -> Dict:
        """Generate P&L statement"""
        return {
            'revenue': self.data['total_revenue'],
            'cost_of_goods_sold': self.data['total_expenses'] * 0.6,
            'gross_profit': self.data['total_revenue'] - (self.data['total_expenses'] * 0.6),
            'operating_expenses': self.data['total_expenses'] * 0.4,
            'net_profit': self.data['net_profit'],
            'profit_margin': self.data['profit_margin']
        }
    
    def generate_balance_sheet(self) -> Dict:
        """Generate balance sheet"""
        return {
            'assets': {
                'current_assets': 500000,
                'fixed_assets': 1000000,
                'total_assets': 1500000
            },
            'liabilities': {
                'current_liabilities': 200000,
                'long_term_liabilities': 300000,
                'total_liabilities': 500000
            },
            'equity': {
                'share_capital': 800000,
                'retained_earnings': 200000,
                'total_equity': 1000000
            }
        }
    
    def generate_cash_flow_statement(self) -> Dict:
        """Generate cash flow statement"""
        return {
            'operating_cash_flow': self.data['net_profit'] * 0.8,
            'investing_cash_flow': -50000,
            'financing_cash_flow': 100000,
            'net_cash_flow': (self.data['net_profit'] * 0.8) - 50000 + 100000
        }
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert currency"""
        if from_currency == to_currency:
            return amount
        
        from_rate = self.data['currency_rates'].get(from_currency, 1.0)
        to_rate = self.data['currency_rates'].get(to_currency, 1.0)
        
        # Convert to base currency first, then to target currency
        base_amount = amount / from_rate
        converted_amount = base_amount * to_rate
        
        return converted_amount
