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
    nric = Column("nric", String, nullable=False, unique=True)
    first_name = Column("first_name", String, nullable=False)
    last_name = Column("last_name", String, nullable=False)
    email = Column("email", String, nullable=False)
    date_of_birth = Column("date_of_birth", Date, nullable=False)
    gender = Column("gender", String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    vaccine_record = relationship("VaccineRecord", back_populates="user")
    address = relationship("Address", back_populates="user")


class Polyclinic(AsyncAttrs, Base):
    __tablename__ = "Polyclinics"

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
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    address = relationship("Address", back_populates="polyclinic")
    booking_slot = relationship("BookingSlot", back_populates="polyclinic")


class GeneralPractitioner(AsyncAttrs, Base):
    __tablename__ = "GeneralPractitioners"

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
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    address = relationship("Address", back_populates="general_practitioner")


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
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="address")
    polyclinic = relationship("Polyclinic", back_populates="address")
    general_practitioner = relationship("GeneralPractitioner", back_populates="address")


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
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    booking_slot = relationship("BookingSlot", back_populates="vaccine")


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
        "polyclinic_id", Integer, ForeignKey("Polyclinics.id"), nullable=False
    )
    vaccine_id = Column(
        "vaccine_id", Integer, ForeignKey("Vaccines.id"), nullable=False
    )
    datetime = Column("datetime", DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    polyclinic = relationship("Polyclinic", back_populates="booking_slot")
    vaccine = relationship("Vaccine", back_populates="booking_slot")
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
    user_id = Column("user_id", Integer, ForeignKey("Users.id"), nullable=False)
    booking_slot_id = Column(
        "booking_slot_id", Integer, ForeignKey("BookingSlots.id"), nullable=False
    )
    status = Column("status", String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="vaccine_record")
    booking_slot = relationship("BookingSlot", back_populates="vaccine_record")
