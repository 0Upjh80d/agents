from models.database import Base
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship


# Define ORM models (existing tables)
class User(AsyncAttrs, Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, nullable=False)
    first_name = Column("first_name", String, nullable=False)
    last_name = Column("last_name", String, nullable=False)
    email = Column("email", String, nullable=False)
    date_of_birth = Column("date_of_birth", Date, nullable=False)
    gender = Column("gender", String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    vaccine_record = relationship("VaccineRecord", back_populates="user")


class Vaccine(AsyncAttrs, Base):
    __tablename__ = "vaccines"

    id = Column("id", Integer, primary_key=True, nullable=False)
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
    vaccine_stock = relationship("VaccineStock", back_populates="vaccine")


class Polyclinic(AsyncAttrs, Base):
    __tablename__ = "polyclinics"

    id = Column("id", Integer, primary_key=True, nullable=False)
    name = Column("name", String, nullable=False)
    address = Column("address", String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    booking_slot = relationship("BookingSlot", back_populates="polyclinic")
    vaccine_stock = relationship("VaccineStock", back_populates="polyclinic")


class BookingSlot(AsyncAttrs, Base):
    __tablename__ = "booking_slots"

    id = Column("id", Integer, primary_key=True, nullable=False)
    polyclinic_id = Column(
        "polyclinic_id", Integer, ForeignKey("polyclinics.id"), nullable=False
    )
    vaccine_id = Column(
        "vaccine_id", Integer, ForeignKey("vaccines.id"), nullable=False
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
    __tablename__ = "vaccine_records"

    id = Column("id", Integer, primary_key=True, nullable=False)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=False)
    booking_slot_id = Column(
        "booking_slot_id", Integer, ForeignKey("booking_slots.id"), nullable=False
    )
    status = Column("status", String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="vaccine_record")
    booking_slot = relationship("BookingSlot", back_populates="vaccine_record")


class VaccineStock(AsyncAttrs, Base):
    __tablename__ = "vaccine_stock_inventory"

    id = Column("id", Integer, primary_key=True, nullable=False)
    polyclinic_id = Column(
        "polyclinic_id", Integer, ForeignKey("polyclinics.id"), nullable=False
    )
    vaccine_id = Column(
        "vaccine_id", Integer, ForeignKey("vaccines.id"), nullable=False
    )
    stock_quantity = Column("stock_quantity", Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    polyclinic = relationship("Polyclinic", back_populates="vaccine_stock")
    vaccine = relationship("Vaccine", back_populates="vaccine_stock")
