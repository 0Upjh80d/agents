-- Insert sample data into Users
INSERT INTO Users (id, address_id, enrolled_clinic_id, nric, first_name, last_name, email, date_of_birth, gender, password)
VALUES
-- User for getting no vaccine recommendations
('d2e8d855-1c1a-4fe6-a8b8-ac823250a414', '0968e1e9-f766-4268-bd05-52a2795e8e99', NULL, 'S1111111J', 'Jane', 'Doe', 'jane.doe@example.com', '2008-01-01', 'F', '$2b$12$//InOGG5Oo6zeAVdyAth3.b7dwZSVAp8ovAXrdkY/GAccLe8B/hDq'),
-- User for getting vaccination records
('8045a3aa-e221-4d9c-89c5-822ab96d4885', '9d02493b-e55b-44fb-b4f5-2f530ffcef06', '225d024f-3d0e-427d-aef9-1fe9a2fc4e13', 'S1234567A', 'Test', 'User', 'test.user@example.com', '2005-01-01', 'F', '$2b$12$I4QqYcmEDKCFi0V3FodWWuFIi4IUKINf/DqvSmXlAdU/lEFjxZSRq');

-- Insert sample data into Clinics
INSERT INTO Clinics (id, address_id, name, type)
VALUES
('225d024f-3d0e-427d-aef9-1fe9a2fc4e13', '9d02493b-e55b-44fb-b4f5-2f530ffcef06', 'Ang Mo Kio Polyclinic', 'polyclinic'),
('bd760847-db7e-439f-add8-3610167478ca', '7cb8712c-7824-49ef-88ce-b418a71e78f9', 'Yishun Polyclinic', 'polyclinic'),
('492f66d8-fd4b-4d61-a343-1c85898337f1', '0968e1e9-f766-4268-bd05-52a2795e8e99', 'Bartley Clinic', 'gp'),
('1be076b3-6452-4f2d-9f2d-cfa7544dc073', '51650b4e-48fb-4665-80f4-c27b8c7de411', 'Raffles Medical (Compass One)', 'gp');

-- Insert sample data into Addresses
INSERT INTO Addresses (id, postal_code, address, latitude, longitude)
VALUES
('9d02493b-e55b-44fb-b4f5-2f530ffcef06', '569666', '21 ANG MO KIO CENTRAL 2 ANG MO KIO POLYCLINIC SINGAPORE 569666', 1.3743245905856, 103.845677779279),
('7cb8712c-7824-49ef-88ce-b418a71e78f9', '768898', '2 YISHUN AVENUE 9 NATIONAL HEALTHCARE GROUP POLYCLINICS (YISHUN POLYCLINIC) SINGAPORE 768898', 1.43035851992416, 103.839190698939),
('0968e1e9-f766-4268-bd05-52a2795e8e99', '534869', '187 UPPER PAYA LEBAR ROAD SINGAPORE 534869', 1.34010826990085, 103.885032592997),
('51650b4e-48fb-4665-80f4-c27b8c7de411', '545078', '1 SENGKANG SQUARE COMPASS ONE SINGAPORE 545078', 1.39205314156706, 103.89507054384);

-- Insert sample data into Vaccines
INSERT INTO Vaccines (id, name, price, doses_required, age_criteria, gender_criteria)
VALUES
('9004aab3-8993-4d37-81c3-78844191e5ec', 'Influenza (INF)', 9.00, 1, '18+ years old', 'None'),
('a67ed08a-95f0-47d4-a97b-8153f1d7874a', 'Human Papillomavirus (HPV)', 23.00, 3, '18-26 years old', 'F'),
('599b1189-0687-4a38-8de5-95850cfa9ee7', 'Pneumococcal Conjugate (PCV13)', 16.00, 1, '65+ years old', 'None');

-- Insert sample data into BookingSlots
INSERT INTO BookingSlots (id, polyclinic_id, vaccine_id, datetime)
VALUES
('97ba51db-48d8-4873-b1ee-57a9b7f766f0', '225d024f-3d0e-427d-aef9-1fe9a2fc4e13', '9004aab3-8993-4d37-81c3-78844191e5ec', '2025-04-01 09:00:00'),
('21b89cd2-f99c-4113-bb46-5cc21d566b97', '225d024f-3d0e-427d-aef9-1fe9a2fc4e13', 'a67ed08a-95f0-47d4-a97b-8153f1d7874a', '2025-04-01 10:00:00'),
('213fa5e7-abbb-4e55-bccc-318db42ace81', 'bd760847-db7e-439f-add8-3610167478ca', '599b1189-0687-4a38-8de5-95850cfa9ee7', '2025-04-02 14:00:00'),
('e7bbc307-ae75-4854-bd91-d6851ae085fd', 'bd760847-db7e-439f-add8-3610167478ca', '9004aab3-8993-4d37-81c3-78844191e5ec', '2025-04-03 11:00:00');

-- Insert sample data into VaccinationRecords
INSERT INTO VaccineRecords (id, user_id, booking_slot_id, status)
VALUES
('b6732344-bc30-4401-9a69-b91e28273b8d', '8045a3aa-e221-4d9c-89c5-822ab96d4885', '97ba51db-48d8-4873-b1ee-57a9b7f766f0', 'booked'),
('7eb3a1a2-dd8c-4cd7-84d5-cd5621ab4fc1', '8045a3aa-e221-4d9c-89c5-822ab96d4885', '21b89cd2-f99c-4113-bb46-5cc21d566b97', 'completed');
