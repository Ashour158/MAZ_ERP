# Base Document Class - Frappe-Independent
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import uuid

class BaseDocument(ABC):
    """Base document class to replace Frappe Document"""
    
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}
        self.name = self.data.get('name') or self.generate_name()
        self.creation = datetime.now()
        self.modified = datetime.now()
        self.owner = self.data.get('owner', 'system')
        self.modified_by = self.data.get('modified_by', 'system')
        self.docstatus = self.data.get('docstatus', 0)
        self.idx = self.data.get('idx', 0)
    
    def generate_name(self) -> str:
        """Generate unique name for document"""
        return f"{self.__class__.__name__}-{uuid.uuid4().hex[:8]}"
    
    def validate(self):
        """Validate document data"""
        pass
    
    def before_save(self):
        """Process before saving"""
        pass
    
    def after_insert(self):
        """Process after inserting"""
        pass
    
    def on_update(self):
        """Process on update"""
        pass
    
    def save(self):
        """Save document to database"""
        self.validate()
        self.before_save()
        # Database save logic here
        self.after_insert()
    
    def update(self, data: Dict[str, Any]):
        """Update document data"""
        self.data.update(data)
        self.modified = datetime.now()
        self.on_update()
    
    def get(self, field: str, default: Any = None) -> Any:
        """Get field value"""
        return self.data.get(field, default)
    
    def set(self, field: str, value: Any):
        """Set field value"""
        self.data[field] = value
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'creation': self.creation,
            'modified': self.modified,
            'owner': self.owner,
            'modified_by': self.modified_by,
            'docstatus': self.docstatus,
            'idx': self.idx,
            **self.data
        }
