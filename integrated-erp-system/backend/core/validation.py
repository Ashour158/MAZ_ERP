# Custom Validation System - Frappe-Independent
from typing import Any, List, Dict
import re
from datetime import datetime

class ValidationError(Exception):
    """Custom validation error"""
    pass

class ValidationSystem:
    """Custom validation system to replace Frappe validation"""
    
    @staticmethod
    def throw(message: str):
        """Throw validation error"""
        raise ValidationError(message)
    
    @staticmethod
    def msgprint(message: str):
        """Print message (can be replaced with logging)"""
        print(f"INFO: {message}")
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?[\d\s\-\(\)]+$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_required(value: Any, field_name: str):
        """Validate required field"""
        if not value:
            ValidationSystem.throw(f"{field_name} is required")
    
    @staticmethod
    def validate_length(value: str, min_length: int, max_length: int, field_name: str):
        """Validate string length"""
        if len(value) < min_length:
            ValidationSystem.throw(f"{field_name} must be at least {min_length} characters")
        if len(value) > max_length:
            ValidationSystem.throw(f"{field_name} must be no more than {max_length} characters")
