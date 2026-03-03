"""
models/user.py - User model (candidates and employers) with authentication.
"""

from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class UserRole(str, enum.Enum):
    candidate = "candidate"
    employer = "employer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.candidate)

    # Authentication fields
    password_hash = Column(String, nullable=True)  # Nullable initially for migration
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, unique=True, nullable=True, index=True)
    verification_token_expires = Column(DateTime, nullable=True)

    # Login tracking
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime, nullable=True)

    # Password reset
    reset_token = Column(String, unique=True, nullable=True, index=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Account status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="employer", cascade="all, delete-orphan")

    # Multiple indexes for query performance
    __table_args__ = (
        Index('idx_email_verified', 'email', 'email_verified'),
        Index('idx_email_verification_token', 'email_verification_token'),
        Index('idx_reset_token', 'reset_token'),
        Index('idx_last_login', 'last_login'),
    )
