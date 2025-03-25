import uuid

from models.database import Base
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship


# Define ORM models (existing tables)
class User(AsyncAttrs, Base):
    __tablename__ = "Users"

    id = Column(
        "id",
        String,
        primary_key=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    address_id = Column("address_id", String, ForeignKey("Addresses.id"), nullable=True)
    enrolled_clinic_id = Column(
        "enrolled_clinic_id", String, ForeignKey("Clinics.id"), nullable=True
    )
    nric = Column("nric", String, nullable=False, unique=True)
    first_name = Column("first_name", String, nullable=False)
    last_name = Column("last_name", String, nullable=False)
    email = Column("email", String, nullable=False)
    date_of_birth = Column("date_of_birth", Date, nullable=False)
    gender = Column("gender", String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(
        "created_at", DateTime, server_default=func.now(), nullable=False
    )
    updated_at = Column(
        "updated_at",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    address = relationship("Address", back_populates="users")
    enrolled_clinic = relationship("Clinic", back_populates="users")
    vaccine_records = relationship("VaccineRecord", back_populates="user")


class Clinic(AsyncAttrs, Base):
    __tablename__ = "Clinics"

    id = Column(
        "id",
        String,
        primary_key=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    address_id = Column(
        "address_id", String, ForeignKey("Addresses.id"), nullable=False
    )
    name = Column("name", String, nullable=False)
    type = Column("type", String, nullable=False)
    created_at = Column(
        "created_at", DateTime, server_default=func.now(), nullable=False
    )
    updated_at = Column(
        "updated_at",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    users = relationship("User", back_populates="enrolled_clinic")
    address = relationship("Address", back_populates="clinic")
    booking_slots = relationship("BookingSlot", back_populates="polyclinic")


class Address(AsyncAttrs, Base):
    __tablename__ = "Addresses"

    id = Column(
        "id",
        String,
        primary_key=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    postal_code = Column("postal_code", String, nullable=False)
    address = Column("address", String, nullable=False)
    latitude = Column("latitude", Numeric(9, 6), nullable=False)
    longitude = Column("longitude", Numeric(9, 6), nullable=False)
    created_at = Column(
        "created_at", DateTime, server_default=func.now(), nullable=False
    )
    updated_at = Column(
        "updated_at",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    users = relationship("User", back_populates="address")
    clinic = relationship("Clinic", back_populates="address")


class Vaccine(AsyncAttrs, Base):
    __tablename__ = "Vaccines"

    id = Column(
        "id",
        String,
        primary_key=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    name = Column("name", String, unique=True, nullable=False)
    price = Column("price", Float(precision=2), nullable=False)
    doses_required = Column("doses_required", Integer, nullable=False)
    age_criteria = Column("age_criteria", String)
    gender_criteria = Column("gender_criteria", String)
    created_at = Column(
        "created_at", DateTime, server_default=func.now(), nullable=False
    )
    updated_at = Column(
        "updated_at",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    booking_slots = relationship("BookingSlot", back_populates="vaccine")


class BookingSlot(AsyncAttrs, Base):
    __tablename__ = "BookingSlots"

    id = Column(
        "id",
        String,
        primary_key=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    polyclinic_id = Column(
        "polyclinic_id", String, ForeignKey("Clinics.id"), nullable=False
    )
    vaccine_id = Column("vaccine_id", String, ForeignKey("Vaccines.id"), nullable=False)
    datetime = Column("datetime", DateTime, nullable=False)
    created_at = Column(
        "created_at", DateTime, server_default=func.now(), nullable=False
    )
    updated_at = Column(
        "updated_at",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    polyclinic = relationship("Clinic", back_populates="booking_slots")
    vaccine = relationship("Vaccine", back_populates="booking_slots")
    vaccine_record = relationship("VaccineRecord", back_populates="booking_slot")


class VaccineRecord(AsyncAttrs, Base):
    __tablename__ = "VaccineRecords"

    id = Column(
        "id",
        String,
        primary_key=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    user_id = Column("user_id", String, ForeignKey("Users.id"), nullable=False)
    booking_slot_id = Column(
        "booking_slot_id", String, ForeignKey("BookingSlots.id"), nullable=False
    )
    status = Column("status", String, nullable=False)
    created_at = Column(
        "created_at", DateTime, server_default=func.now(), nullable=False
    )
    updated_at = Column(
        "updated_at",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="vaccine_records")
    booking_slot = relationship("BookingSlot", back_populates="vaccine_record")
