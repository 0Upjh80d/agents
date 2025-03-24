-- Users table with unique email and audit timestamps
CREATE TABLE users (
    id TEXT PRIMARY KEY, -- UUID stored as text
    nric VARCHAR(9) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    password VARCHAR(255) NOT NULL, -- hashed password
    postal_code VARCHAR(6) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Vaccines table including eligibility criteria and audit timestamps
CREATE TABLE vaccines (
    id TEXT PRIMARY KEY, -- UUID stored as text
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    doses_required INTEGER NOT NULL,
    age_criteria VARCHAR(50),
    gender_criteria VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Polyclinics table with basic location info and audit timestamps
CREATE TABLE polyclinics (
    id TEXT PRIMARY KEY, -- UUID stored as text
    name VARCHAR(100) NOT NULL,
    postal_code VARCHAR(6) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- GeneralPractitioners table with basic location info and audit timestamps
CREATE TABLE general_practitioners (
    id TEXT PRIMARY KEY, -- UUID stored as text
    name VARCHAR(100) NOT NULL,
    postal_code VARCHAR(6) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Addresses table with location info and audit timestamps
CREATE TABLE addresses (
    id TEXT PRIMARY KEY, -- UUID stored as text
    postal_code VARCHAR(6) NOT NULL,
    address VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- BookingSlots table representing available slots for appointments
CREATE TABLE booking_slots (
    id TEXT PRIMARY KEY, -- UUID stored as text
    polyclinic_id TEXT NOT NULL,  -- UUID stored as text
    vaccine_id TEXT NOT NULL,     -- UUID stored as text
    datetime DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (polyclinic_id) REFERENCES Polyclinics(id) ON DELETE CASCADE,
    FOREIGN KEY (vaccine_id) REFERENCES Vaccines(id) ON DELETE CASCADE,
    UNIQUE (polyclinic_id, vaccine_id, datetime)
);

-- VaccineRecords table representing booked appointments (or vaccinations)
CREATE TABLE vaccine_records (
    id TEXT PRIMARY KEY, -- UUID stored as text
    user_id TEXT NOT NULL,  -- UUID stored as text
    booking_slot_id TEXT UNIQUE NOT NULL,  -- UUID stored as text
    status VARCHAR(20) NOT NULL, -- 'booked', 'completed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_slot_id) REFERENCES BookingSlots(id) ON DELETE CASCADE
);
