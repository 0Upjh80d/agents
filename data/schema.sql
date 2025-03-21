-- Users table with unique email and audit timestamps
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Vaccines table including eligibility criteria and audit timestamps
CREATE TABLE vaccines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    -- longitude DECIMAL(9,6),
    -- latitude DECIMAL(9,6),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- BookingSlots table representing available slots for appointments
CREATE TABLE booking_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    polyclinic_id INTEGER NOT NULL,
    vaccine_id INTEGER NOT NULL,
    datetime DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (polyclinic_id) REFERENCES Polyclinics(id) ON DELETE CASCADE,
    FOREIGN KEY (vaccine_id) REFERENCES Vaccines(id) ON DELETE CASCADE,
    UNIQUE (polyclinic_id, vaccine_id, datetime)
);

-- VaccineRecords table representing booked appointments (or vaccinations)
CREATE TABLE vaccine_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    booking_slot_id INTEGER NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL, -- 'booked', 'completed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_slot_id) REFERENCES BookingSlots(id) ON DELETE CASCADE
);

-- PolyclinicVaccineInventory table representing stock per polyclinic and vaccine
CREATE TABLE vaccine_stock_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    polyclinic_id INTEGER NOT NULL,
    vaccine_id INTEGER NOT NULL,
    stock_quantity INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (polyclinic_id) REFERENCES Polyclinics(id) ON DELETE CASCADE,
    FOREIGN KEY (vaccine_id) REFERENCES Vaccines(id) ON DELETE CASCADE,
    UNIQUE (polyclinic_id, vaccine_id)
);
