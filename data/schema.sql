-- Users table with general information, credentials and audit timestamps
CREATE TABLE Users (
    id TEXT PRIMARY KEY,
    address_id TEXT,
    enrolled_clinic_id TEXT,
    nric VARCHAR(9) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    password VARCHAR(255) NOT NULL, -- hashed password
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (address_id) REFERENCES Addresses(id) ON DELETE CASCADE,
    FOREIGN KEY (enrolled_clinic_id) REFERENCES Clinics(id) ON DELETE CASCADE
);

-- Clinics table with basic information and audit timestamps
CREATE TABLE Clinics (
    id TEXT PRIMARY KEY,
    address_id TEXT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'polyclinic', 'gp'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (address_id) REFERENCES Addresses(id) ON DELETE CASCADE
);

-- Addresses table with location information (i.e., long and lat) and audit timestamps
CREATE TABLE Addresses (
    id TEXT PRIMARY KEY,
    postal_code VARCHAR(6) NOT NULL,
    address VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Vaccines table including vaccine information, eligibility criterias and audit timestamps
CREATE TABLE Vaccines (
    id TEXT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    doses_required INTEGER NOT NULL,
    age_criteria VARCHAR(50),
    gender_criteria VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- BookingSlots table representing available slots for appointments and audit timestamps
CREATE TABLE BookingSlots (
    id TEXT PRIMARY KEY,
    polyclinic_id TEXT NOT NULL,
    vaccine_id TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (polyclinic_id) REFERENCES Clinics(id) ON DELETE CASCADE,
    FOREIGN KEY (vaccine_id) REFERENCES Vaccines(id) ON DELETE CASCADE,
    UNIQUE (polyclinic_id, vaccine_id, datetime)
);

-- VaccineRecords table representing booked or completed appointments (or vaccinations) and audit timestamps
CREATE TABLE VaccineRecords (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    booking_slot_id TEXT UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'booked', 'completed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_slot_id) REFERENCES BookingSlots(id) ON DELETE CASCADE
);
