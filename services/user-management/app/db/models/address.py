import uuid
from sqlalchemy import (Boolean, Column, String, DateTime, ForeignKey, func, Integer)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..base import Base

class Country(Base):
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(3), unique=True, nullable=False)  # ISO country code
    
    states = relationship("State", back_populates="country")

class State(Base):
    __tablename__ = 'states'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    
    country = relationship("Country", back_populates="states")
    cities = relationship("City", back_populates="state")
    addresses = relationship("Address", back_populates="state")

class City(Base):
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    state_id = Column(Integer, ForeignKey('states.id'), nullable=False)
    
    state = relationship("State", back_populates="cities")
    addresses = relationship("Address", back_populates="city")

class Address(Base):
    __tablename__ = 'addresses'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    address_line = Column(String(200), nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)
    state_id = Column(Integer, ForeignKey('states.id'), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    pin_code = Column(String(10), nullable=True)
    
    # Address type (home, work, etc.)
    address_type = Column(String(20), default='home', nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    
    user = relationship("User", back_populates="addresses")
    city = relationship("City", back_populates="addresses")
    state = relationship("State", back_populates="addresses")
    country = relationship("Country")
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)