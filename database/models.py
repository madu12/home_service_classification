from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    
    service_requests = relationship('ServiceRequest', 
                                    foreign_keys='ServiceRequest.predicted_category_id', 
                                    back_populates='predicted_category', 
                                    cascade='all, delete-orphan')
    
    confirmed_requests = relationship('ServiceRequest', 
                                      foreign_keys='ServiceRequest.user_confirmed_category_id', 
                                      back_populates='user_confirmed_category', 
                                      cascade='all, delete-orphan')

class ServiceRequest(Base):
    __tablename__ = 'service_requests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_description = Column(String, nullable=False)
    predicted_category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    user_confirmed_category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_feedback = Column(Boolean, default=False)
    
    predicted_category = relationship('Category', 
                                      foreign_keys=[predicted_category_id], 
                                      back_populates='service_requests')
    
    user_confirmed_category = relationship('Category', 
                                           foreign_keys=[user_confirmed_category_id], 
                                           back_populates='confirmed_requests')
