# Independent Database Layer - Frappe-Free
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

Base = declarative_base()

class DatabaseManager:
    """Database manager to replace Frappe database operations"""
    
    def __init__(self, database_url: str = "sqlite:///erp_system.db"):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute raw SQL query"""
        try:
            with self.get_session() as session:
                result = session.execute(query, params or {})
                return [dict(row) for row in result]
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
    
    def get_list(self, doctype: str, filters: Dict = None, fields: List[str] = None, 
                order_by: str = None, limit: int = None) -> List[Dict]:
        """Get list of records"""
        try:
            with self.get_session() as session:
                # This would be implemented based on the specific doctype
                # For now, return empty list as placeholder
                return []
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
    
    def get_doc(self, doctype: str, name: str) -> Optional[Dict]:
        """Get single document"""
        try:
            with self.get_session() as session:
                # This would be implemented based on the specific doctype
                # For now, return None as placeholder
                return None
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
    
    def set_value(self, doctype: str, name: str, field: str, value: Any):
        """Set field value"""
        try:
            with self.get_session() as session:
                # This would be implemented based on the specific doctype
                # For now, just pass as placeholder
                pass
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
    
    def exists(self, doctype: str, name: str) -> bool:
        """Check if document exists"""
        try:
            with self.get_session() as session:
                # This would be implemented based on the specific doctype
                # For now, return False as placeholder
                return False
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")

# Database Models
class ContactModel(Base):
    """Contact database model"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email_id = Column(String(255))
    mobile_no = Column(String(20))
    customer = Column(String(255))
    contact_type = Column(String(50))
    contact_status = Column(String(50))
    contact_priority = Column(String(50))
    designation = Column(String(100))
    department = Column(String(100))
    is_primary_contact = Column(Boolean, default=False)
    is_decision_maker = Column(Boolean, default=False)
    is_influencer = Column(Boolean, default=False)
    is_gatekeeper = Column(Boolean, default=False)
    contact_engagement_score = Column(Float, default=0.0)
    contact_influence_score = Column(Float, default=0.0)
    communication_frequency = Column(Integer, default=0)
    response_rate = Column(Float, default=0.0)
    contact_insights = Column(Text)
    creation = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = Column(String(255))
    modified_by = Column(String(255))
    docstatus = Column(Integer, default=0)
    idx = Column(Integer, default=0)

class AccountModel(Base):
    """Account database model"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    account_name = Column(String(255))
    account_type = Column(String(100))
    account_status = Column(String(50))
    account_priority = Column(String(50))
    account_code = Column(String(100))
    territory = Column(String(100))
    industry = Column(String(100))
    company_size = Column(String(50))
    annual_revenue = Column(Float)
    employee_count = Column(Integer)
    website = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    account_owner = Column(String(255))
    account_health_score = Column(Float, default=0.0)
    account_value = Column(Float, default=0.0)
    account_insights = Column(Text)
    creation = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = Column(String(255))
    modified_by = Column(String(255))
    docstatus = Column(Integer, default=0)
    idx = Column(Integer, default=0)

class CustomerModel(Base):
    """Customer database model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    customer_name = Column(String(255))
    customer_type = Column(String(100))
    customer_status = Column(String(50))
    customer_priority = Column(String(50))
    customer_code = Column(String(100))
    territory = Column(String(100))
    industry = Column(String(100))
    company_size = Column(String(50))
    annual_revenue = Column(Float)
    employee_count = Column(Integer)
    website = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    account_owner = Column(String(255))
    health_score = Column(Float, default=0.0)
    churn_risk = Column(String(50))
    total_spent = Column(Float, default=0.0)
    satisfaction = Column(Float, default=0.0)
    last_activity = Column(DateTime)
    customer_insights = Column(Text)
    creation = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = Column(String(255))
    modified_by = Column(String(255))
    docstatus = Column(Integer, default=0)
    idx = Column(Integer, default=0)

class OpportunityModel(Base):
    """Opportunity database model"""
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    opportunity_name = Column(String(255))
    customer = Column(String(255))
    contact = Column(String(255))
    opportunity_amount = Column(Float)
    probability = Column(Float)
    opportunity_stage = Column(String(100))
    expected_closing = Column(DateTime)
    status = Column(String(50))
    aging = Column(Integer, default=0)
    ai_recommendation = Column(Text)
    manager_recommendation = Column(Text)
    opportunity_insights = Column(Text)
    creation = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = Column(String(255))
    modified_by = Column(String(255))
    docstatus = Column(Integer, default=0)
    idx = Column(Integer, default=0)

class LeadModel(Base):
    """Lead database model"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(255))
    email_id = Column(String(255))
    mobile_no = Column(String(20))
    company = Column(String(255))
    designation = Column(String(100))
    industry = Column(String(100))
    lead_source = Column(String(100))
    lead_status = Column(String(50))
    lead_score = Column(Float, default=0.0)
    lead_quality = Column(String(50))
    lead_insights = Column(Text)
    creation = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = Column(String(255))
    modified_by = Column(String(255))
    docstatus = Column(Integer, default=0)
    idx = Column(Integer, default=0)

# Global database manager instance
db_manager = DatabaseManager()
