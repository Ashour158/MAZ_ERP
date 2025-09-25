# Utility Functions - Frappe-Independent
from datetime import datetime, timedelta
from typing import Any, Dict
import uuid
import re

class Utils:
    """Utility functions to replace Frappe utils"""
    
    @staticmethod
    def now() -> datetime:
        """Get current datetime"""
        return datetime.now()
    
    @staticmethod
    def get_datetime(date_string: str) -> datetime:
        """Parse datetime string"""
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    
    @staticmethod
    def add_days(date: datetime, days: int) -> datetime:
        """Add days to date"""
        return date + timedelta(days=days)
    
    @staticmethod
    def get_time() -> str:
        """Get current time string"""
        return datetime.now().strftime('%H:%M:%S')
    
    @staticmethod
    def make_autoname(pattern: str) -> str:
        """Generate autoname based on pattern"""
        name = pattern.replace('.YYYY.', str(datetime.now().year))
        name = name.replace('.MM.', str(datetime.now().month).zfill(2))
        name = name.replace('.#####', str(uuid.uuid4().hex[:5]))
        return name
    
    @staticmethod
    def get_user_default(key: str) -> Any:
        """Get user default value"""
        return None
    
    @staticmethod
    def get_cached_value(doctype: str, name: str, field: str) -> Any:
        """Get cached value"""
        return None
