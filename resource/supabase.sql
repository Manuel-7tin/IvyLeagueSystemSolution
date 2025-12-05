-- ============================================
-- INSERT INTO papers (12 papers)
-- ============================================
INSERT INTO papers (id, name, code, description, price, revision, category, available)
VALUES
    (101, 'Quantum Mechanics', 'QM', 'This is a course that somehow wanders through ideas like clouds drifting sideways, teaching something uncertain yet strangely fascinating to everyone involved.', 45000, 15000, 'Foundation', TRUE),
    (102, 'Molecular Biology', 'MB', 'This is a course that somehow wanders through ideas like clouds drifting sideways...', 47000, 15000, 'Foundation', TRUE),
    (103, 'Organic Chemistry', 'OC', 'This is a course that somehow wanders...', 50000, 15000, 'Applied', TRUE),
    (104, 'Astrophysics', 'AP', 'This is a course that somehow wanders...', 55000, 20000, 'Applied', TRUE),
    (105, 'Genetics & Evolution', 'GE', 'This is a course that somehow wanders...', 52000, 20000, 'Skill', TRUE),
    (106, 'Thermodynamics', 'TD', 'This is a course that somehow wanders...', 60000, 20000, 'Skill', TRUE),
    (107, 'Advanced Quantum Field Theory', 'QFT', 'This is a course that somehow wanders...', 65000, 25000, 'Professional', TRUE),
    (108, 'Advanced Astrobiology', 'AB', 'This is a course that somehow wanders...', 65000, 25000, 'Professional', TRUE),
    (109, 'Cosmology & Space Systems', 'CSS', 'This is a course that somehow wanders...', 70000, 30000, 'Professional', TRUE),
    (110, 'Planetary Science & Exploration', 'PSE', 'This is a course that somehow wanders...', 70000, 30000, 'Professional', TRUE),
    (111, 'Advanced Computational Biology', 'ACB', 'This is a course that somehow wanders...', 68000, 25000, 'Professional', TRUE),
    (112, 'Advanced Materials Science', 'AMS', 'This is a course that somehow wanders...', 68000, 25000, 'Professional', TRUE);




-- ============================================
-- INSERT INTO diets (2 diets)
-- ============================================
INSERT INTO diets (
    id, name, title, description, available_papers,
    reg_start, reg_deadline, revision_start, revision_deadline, completion_date
)
VALUES
    (18, 'June 2025 Diet', 'June Diet 2025',
     'Mid-year registration window for ACCA students. Includes full revision bootcamp access.',
     ARRAY['QM','MB','OC','AP','GE','TD'],
     '2025-03-01 00:00:00', '2025-05-20 23:59:00',
     '2025-05-25 00:00:00', '2025-06-10 23:59:00', '2025-06-15 00:00:00'),

    (29, 'December 2025 Diet', 'December Diet 2025',
     'End-year exam diet. Includes advanced professional-level papers.',
     ARRAY['QFT','AB','CSS','PSE','ACB','AMS'],
     '2025-08-01 00:00:00', '2025-11-20 23:59:00',
     '2025-11-25 00:00:00', '2025-12-10 23:59:00', '2025-12-15 00:00:00');



-- ============================================
-- INSERT INTO staffs (5 staff)
-- ============================================
INSERT INTO staffs (
    id, title, first_name, last_name, email, phone_number,
    password, code, last_active, gender, birth_date,
    house_address, role, access, employment_type, status,
    hire_date, photo, joined, updated_at
)
VALUES
    (61, 'Mr', 'Emeka', 'Okafor', 'e.okafor@academy.com', '08031234567',
     '9b74c9897bac770ffc029102a200c5de', 'ADM-00001', NOW(), 'Male', '1985-04-12',
     '12 Allen Avenue, Ikeja, Lagos', 'super_admin', TRUE, 'Full-Time', 'Active',
     '2020-01-15', 'https://example.com/photos/staff1.jpg', NOW(), NOW()),

    (62, 'Mrs', 'Amina', 'Lawal', 'a.lawal@academy.com', '08021234567',
     '9b74c9897bac770ffc029102a200c5de', 'TUT-00004', NOW(), 'Female', '1990-06-20',
     '34 Garki Road, Abuja', 'tutor', TRUE, 'Part-Time', 'Active',
     '2021-09-10', 'https://example.com/photos/staff2.jpg', NOW(), NOW()),

    (63, 'Mr', 'Tunde', 'Balogun', 't.balogun@academy.com', '07051239876',
     '9b74c9897bac770ffc029102a200c5de', 'TUT-00004', NOW(), 'Male', '1988-10-02',
     '5 Old Bodija Estate, Ibadan', 'tutor', TRUE, 'Full-Time', 'Active',
     '2019-04-30', 'https://example.com/photos/staff3.jpg', NOW(), NOW()),

    (64, 'Dr', 'Grace', 'Osho', 'g.osho@academy.com', '08181234987',
     '9b74c9897bac770ffc029102a200c5de', 'BRD-00002', NOW(), 'Female', '1979-12-22',
     '9 Lekki Phase 1, Lagos', 'board', TRUE, 'Part-Time', 'Active',
     '2022-02-18', 'https://example.com/photos/staff4.jpg', NOW(), NOW()),

    (65, 'Mr', 'Chinedu', 'Opara', 'c.opara@academy.com', '08082223344',
     '9b74c9897bac770ffc029102a200c5de', 'INT-00003', NOW(), 'Male', '1998-03-10',
     '18 Rumuola Road, Port Harcourt', 'lite_admin', TRUE, 'Intern', 'Active',
     '2024-06-01', 'https://example.com/photos/staff5.jpg', NOW(), NOW());

-- ============================================
-- PART 2 STARTS & PART 1 ENDS
-- ============================================

-- ============================================
-- INSERT INTO students (10 students)
-- ============================================
INSERT INTO students (
    id, first_name, last_name, title, email, reg_no, password,
    reg_date, acca_reg_no, birth_date, profile_photo, phone_number,
    gender, last_active, joined, house_address, referral_source,
    referrer, employment_status, access, can_pay_partially,
    oxford_brookes, accurate_data, alp_consent, terms_and_cond
)
VALUES
    (1, 'Chukwuemeka', 'Nwosu', 'Mr', 'c.nwosu@student.com', 'ACC-2025-001',
     '9b74c9897bac770ffc029102a200c5de', NOW(), 'ACCA-NG-001', '1999-01-14',
     'https://example.com/photos/student1.jpg', '08051234567', 'Male', NOW(),
     '2023-08-10', '13 Ajose Street, Surulere, Lagos', 'Instagram Ad',
     NULL, 'Employed', TRUE, FALSE, 'Yes', TRUE, TRUE, TRUE),

    (2, 'Aisha', 'Mohammed', 'Miss', 'a.mohammed@student.com', 'ACC-2025-002',
     '9b74c9897bac770ffc029102a200c5de', NOW(), 'ACCA-NG-002', '2000-03-22',
     'https://example.com/photos/student2.jpg', '08161234888', 'Female', NOW(),
     '2023-09-11', '4 Wuse 2, Abuja', 'Friend', 'Fatima Mohammed', 'Student',
     TRUE, FALSE, 'No', TRUE, TRUE, TRUE),

    (3, 'Oluwaseun', 'Adeyemi', 'Mr', 'o.adeyemi@student.com', 'ACC-2025-003',
     '9b74c9897bac770ffc029102a200c5de', NOW(), 'ACCA-NG-003', '1998-06-10',
     'https://example.com/photos/student3.jpg', '09022233445', 'Male', NOW(),
     '2024-01-10', '2 Ring Road, Ibadan', 'Tiktok Ad', NULL, 'Employed',
     TRUE, TRUE, 'Yes', TRUE, TRUE, TRUE),

    (4, 'Kemi', 'Ogunleye', 'Miss', 'k.ogunleye@student.com', 'ACC-2025-004',
     '9b74c9897bac770ffc029102a200c5de', NOW(), 'ACCA-NG-004', '1997-11-02',
     'https://example.com/photos/student4.jpg', '08073339912', 'Female', NOW(),
     '2024-02-15', '7 Bodija Estate, Ibadan', 'Flyer', NULL, 'Unemployed',
     TRUE, FALSE, 'No', TRUE, TRUE, TRUE),

    (5, 'Ifeanyi', 'Okonkwo', 'Mr', 'i.okonkwo@student.com', 'ACC-2025-005',
     '9b74c9897bac770ffc029102a200c5de', NOW(), 'ACCA-NG-005', '1996-12-25',
     'https://example.com/photos/student5.jpg', '08044556677', 'Male', NOW(),
     '2023-05-08', '15 GRA, Onitsha', 'Friend', 'Emeka Nwosu', 'Employed',
     TRUE, TRUE, 'Yes', TRUE, TRUE, TRUE),

    (6, 'Blessing', 'Ojo', 'Miss', 'b.ojo@student.com', 'ACC-2025-006',
     '9b74c9897bac770ffc029102a200c5de', NOW(), 'ACCA-NG-006', '2001-04-18',
     'https://example.com/photos/student6.jpg', '08112223345', 'Female', NOW(),
     '2023-07-19', '10 Airport Road, Benin City', 'Instagram Ad', NULL,
     'Student', TRUE, FALSE, 'No', TRUE, TRUE, TRUE),

    (7, 'Samuel', 'Ogunbiyi', 'Mr', 's.ogunbiyi@student.com', 'ACC-2025-007',
     '9b74c9897bac770ffc029102a200c5de', NOW(), 'ACCA-NG-007', '1995-09-30',
     'https://example.com/photos/student7.jpg', '09033445566', 'Male', NOW(),
     '2023-10-11', '6 Apapa Road, Lagos', 'Facebook Ad', NULL, 'Employed',
     TRUE, TRUE, 'Yes', TRUE, TRUE, TRUE),

    (8, 'Zainab', 'Abdullahi', 'Miss', 'z.abdullahi@student.com', 'ACC-2025-008',
     '9b74c9897bac770ffc029102a200c5de', NOW(), 'ACCA-NG-008', '1999-07-15',
     'https://example.com/photos/student8.jpg', '08099887766', 'Female', NOW(),
     '2024-01-20', '3 Sabon Gari, Kano', 'Friend', 'Aisha Mohammed', 'Student',
     TRUE, FALSE, 'No', TRUE, TRUE, TRUE),

    (9, 'Michael', 'Adewale', 'Mr', 'm.adewale@student.com', 'ACC-2025-009',
     '9b74c9897bac770ffc029102a200c5de', NOW(), 'ACCA-NG-009', '1998-08-08',
     'https://example.com/photos/student9.jpg', '08065554432', 'Male', NOW(),
     '2022-11-06', '14 Ring Road, Akure', 'Flyer', NULL, 'Employed',
     TRUE, TRUE, 'Yes', TRUE, TRUE, TRUE),

    (10, 'Chinelo', 'Okorie', 'Miss', 'c.okorie@student.com', 'ACC-2025-010',
     '9b74c9897bac770ffc029102a200c5de', NOW(), 'ACCA-NG-010', '2000-09-17',
     'https://example.com/photos/student10.jpg', '08134455667', 'Female', NOW(),
     '2023-12-18', '9 Trans Amadi, Port Harcourt', 'Tiktok Ad', NULL,
     'Student', TRUE, FALSE, 'No', TRUE, TRUE, TRUE);



-- ============================================
-- INSERT INTO signees (5 signees)
-- ============================================
INSERT INTO signees (
    id, title, email, password, first_name, last_name,
    phone_number, created_at, email_confirmed,
    birth_date, gender, can_pay_partially
)
VALUES
    (1, 'Mr', 'sig.adebayo@example.com', '9b74c9897bac770ffc029102a200c5de',
     'Tosin', 'Adebayo', '08023455677', NOW(), TRUE, '1990-02-15', 'M', TRUE),

    (2, 'Mrs', 'sig.maryam@example.com', '9b74c9897bac770ffc029102a200c5de',
     'Maryam', 'Sani', '08145566778', NOW(), FALSE, '1988-07-11', 'F', FALSE),

    (3, 'Mr', 'sig.johnson@example.com', '9b74c9897bac770ffc029102a200c5de',
     'Ola', 'Johnson', '08012223344', NOW(), TRUE, '1992-12-03', 'M', TRUE),

    (4, 'Dr', 'sig.khadijah@example.com', '9b74c9897bac770ffc029102a200c5de',
     'Khadijah', 'Yusuf', '08178889900', NOW(), TRUE, '1985-04-23', 'F', FALSE),

    (5, 'Mr', 'sig.emmanuel@example.com', '9b74c9897bac770ffc029102a200c5de',
     'Emmanuel', 'Oche', '07091234566', NOW(), FALSE, '1994-08-14', 'M', TRUE);



-- ============================================
-- INSERT INTO sponsored (5)
-- ============================================
INSERT INTO sponsored (
    id, first_name, last_name, company, papers, token, used, diet_name, created_at
)
VALUES
    (61, 'Ada', 'Okeke', 'ZenithBank', ARRAY['QM','MB'], 'SPON-001', FALSE, 'June 2025 Diet', NOW()),
    (62, 'John', 'Eze', 'GTBank', ARRAY['OC'], 'SPON-002', FALSE, 'June 2025 Diet', NOW()),
    (63, 'Musa', 'Bello', 'Dangote', ARRAY['AP','GE'], 'SPON-003', FALSE, 'June 2025 Diet', NOW()),
    (64, 'Sarah', 'Oni', 'Shell', ARRAY['QFT'], 'SPON-004', FALSE, 'December 2025 Diet', NOW()),
    (65, 'David', 'Orji', 'TotalEnergies', ARRAY['CSS','PSE'], 'SPON-005', TRUE, 'December 2025 Diet', NOW());



-- ============================================
-- INSERT INTO scholarships (10)
-- ============================================
INSERT INTO scholarships (id, email, paper, discount, used, diet_name, created_at)
VALUES
    (11, 'c.nwosu@student.com', 'QM', 30, FALSE, 'June 2025 Diet', NOW()),
    (12, 'a.mohammed@student.com', 'MB', 25, FALSE, 'June 2025 Diet', NOW()),
    (13, 'o.adeyemi@student.com', 'AP', 40, FALSE, 'June 2025 Diet', NOW()),
    (14, 'k.ogunleye@student.com', 'GE', 20, FALSE, 'June 2025 Diet', NOW()),
    (15, 'i.okonkwo@student.com', 'TD', 15, TRUE, 'June 2025 Diet', NOW()),
    (16, 'b.ojo@student.com', 'QFT', 50, FALSE, 'December 2025 Diet', NOW()),
    (17, 's.ogunbiyi@student.com', 'AB', 10, FALSE, 'December 2025 Diet', NOW()),
    (18, 'z.abdullahi@student.com', 'CSS', 35, TRUE, 'December 2025 Diet', NOW()),
    (19, 'm.adewale@student.com', 'PSE', 30, FALSE, 'December 2025 Diet', NOW()),
    (20, 'c.okorie@student.com', 'AMS', 25, FALSE, 'December 2025 Diet', NOW());

-- ============================================
-- PART 3 STARTS & PART 2 ENDS
-- ============================================
-- ============================================
-- INSERT INTO enrollments (15 enrollments)
-- ============================================

INSERT INTO enrollments (
    id, student_reg_no, new_student, date, sponsored, sponsor,
    sponsored_papers, total_fee, amount_paid, payment_status,
    revision, retake, discount, discount_papers,
    refund, receivable, student_id, diet_id
)
VALUES
    (1, 'ACC-2025-001', FALSE, '2025-01-10', FALSE, NULL,
     NULL, 120000, 60000, 'partially_paid',
     TRUE, FALSE, 0.0, ARRAY[]::text[],
     0, 60000, 1, 18),

    (2, 'ACC-2025-002', TRUE, '2025-01-12', TRUE, 'ZenithBank',
     'QM,MB', 90000, 90000, 'paid',
     TRUE, FALSE, 30.0, ARRAY['QM'],
     0, 0, 2, 18),

    (3, 'ACC-2025-003', FALSE, '2025-01-14', FALSE, NULL,
     NULL, 145000, 100000, 'partially_paid',
     TRUE, FALSE, 15.0, ARRAY['AP'],
     0, 45000, 3, 18),

    (4, 'ACC-2025-004', TRUE, '2025-01-17', FALSE, NULL,
     NULL, 65000, 65000, 'paid',
     TRUE, FALSE, 0.0, ARRAY[]::text[],
     0, 0, 4, 18),

    (5, 'ACC-2025-005', FALSE, '2025-01-18', TRUE, 'GTBank',
     'OC', 50000, 50000, 'paid',
     TRUE, FALSE, 20.0, ARRAY['OC'],
     0, 0, 5, 18),

    (6, 'ACC-2025-006', TRUE, '2025-01-20', FALSE, NULL,
     NULL, 100000, 30000, 'partially_paid',
     TRUE, FALSE, 0.0, ARRAY[]::text[],
     0, 70000, 6, 18),

    (7, 'ACC-2025-007', FALSE, '2025-01-21', FALSE, NULL,
     NULL, 135000, 135000, 'paid',
     TRUE, FALSE, 10.0, ARRAY['GE'],
     0, 0, 7, 18),

    (8, 'ACC-2025-008', TRUE, '2025-01-22', FALSE, NULL,
     NULL, 140000, 140000, 'paid',
     TRUE, FALSE, 0.0, ARRAY[]::text[],
     0, 0, 8, 18),

    (9, 'ACC-2025-009', FALSE, '2025-01-25', TRUE, 'Dangote',
     'AP,GE', 100000, 100000, 'paid',
     TRUE, FALSE, 40.0, ARRAY['AP'],
     0, 0, 9, 18),

    (10, 'ACC-2025-010', TRUE, '2025-02-01', FALSE, NULL,
     NULL, 125000, 50000, 'partially_paid',
     TRUE, FALSE, 0.0, ARRAY[]::text[],
     0, 75000, 10, 18),

    (11, 'ACC-2025-001', FALSE, '2025-09-01', FALSE, NULL,
     NULL, 180000, 90000, 'partially_paid',
     TRUE, FALSE, 0.0, ARRAY[]::text[],
     0, 90000, 1, 29),

    (12, 'ACC-2025-002', FALSE, '2025-09-05', TRUE, 'Shell',
     'QFT', 65000, 65000, 'paid',
     TRUE, FALSE, 50.0, ARRAY['QFT'],
     0, 0, 2, 29),

    (13, 'ACC-2025-003', FALSE, '2025-09-09', FALSE, NULL,
     NULL, 210000, 100000, 'partially_paid',
     TRUE, FALSE, 0.0, ARRAY[]::text[],
     0, 110000, 3, 29),

    (14, 'ACC-2025-004', TRUE, '2025-09-11', FALSE, NULL,
     NULL, 240000, 240000, 'paid',
     TRUE, FALSE, 25.0, ARRAY['PSE'],
     0, 0, 4, 29),

    (15, 'ACC-2025-005', FALSE, '2025-09-15', TRUE, 'TotalEnergies',
     'CSS,PSE', 140000, 140000, 'paid',
     TRUE, FALSE, 35.0, ARRAY['CSS'],
     0, 0, 5, 29);
-- ==========
-- ==========

-- ============================================
-- INSERT INTO registrations (pivot table)
-- ============================================
INSERT INTO registrations (enrollment_id, paper_id, registration_date)
VALUES
    -- Enrollment 1: QM, MB
    (1, 101, NOW()), (1, 102, NOW()),

    -- Enrollment 2: QM, MB
    (2, 101, NOW()), (2, 102, NOW()),

    -- Enrollment 3: OC, AP
    (3, 103, NOW()), (3, 104, NOW()),

    -- Enrollment 4: GE
    (4, 105, NOW()),

    -- Enrollment 5: OC
    (5, 103, NOW()),

    -- Enrollment 6: QM, TD
    (6, 101, NOW()), (6, 106, NOW()),

    -- Enrollment 7: GE, TD
    (7, 105, NOW()), (7, 106, NOW()),

    -- Enrollment 8: QM, MB, TD
    (8, 101, NOW()), (8, 102, NOW()), (8, 106, NOW()),

    -- Enrollment 9: AP, GE
    (9, 104, NOW()), (9, 105, NOW()),

    -- Enrollment 10: MB, OC
    (10, 102, NOW()), (10, 103, NOW()),

    -- Enrollment 11 (Diet 2): QFT, AB
    (11, 107, NOW()), (11, 108, NOW()),

    -- Enrollment 12: QFT
    (12, 107, NOW()),

    -- Enrollment 13: CSS, PSE
    (13, 109, NOW()), (13, 110, NOW()),

    -- Enrollment 14: PSE, ACB
    (14, 110, NOW()), (14, 111, NOW()),

    -- Enrollment 15: CSS, PSE
    (15, 109, NOW()), (15, 110, NOW());
-- ==========
-- ==========

-- ============================================
-- INSERT INTO payments (15)
-- ============================================
INSERT INTO payments (
    id, amount, payment_reference, student_reg, sponsored, context, purpose,
    paystack_id, message, medium, currency, ip, attempts, history, fee,
    auth_data, fee_breakdown, customer_data, created_at, paid_at,
    receipt_number, receipt, enrollment_id
)
VALUES
    (1, 60000, 'PAY-REF-001', 'ACC-2025-001', FALSE,
     ARRAY['enrollment'], 'tuition', 900001,
     'Payment received', 'card', 'NGN', '102.45.11.1', 1,
     '{}'::json, 250, '{}'::json, '{}'::json, '{}'::json,
     '2025-01-10', '2025-01-10', 'RCT-001', NULL, 1),

    (2, 90000, 'PAY-REF-002', 'ACC-2025-002', TRUE,
     ARRAY['sponsored'], 'tuition', 900002,
     'Paid by sponsor', 'bank', 'NGN', '105.22.12.4', 1,
     '{}'::json, 300, '{}'::json, '{}'::json, '{}'::json,
     '2025-01-12', '2025-01-12', 'RCT-002', NULL, 2),

    (3, 100000, 'PAY-REF-003', 'ACC-2025-003', FALSE,
     ARRAY['enrollment'], 'tuition', 900003,
     'Part payment', 'transfer', 'NGN', '102.45.11.3', 2,
     '{}'::json, 300, '{}'::json, '{}'::json, '{}'::json,
     '2025-01-14', '2025-01-14', 'RCT-003', NULL, 3),

    (4, 65000, 'PAY-REF-004', 'ACC-2025-004', FALSE,
     ARRAY['enrollment'], 'tuition', 900004,
     'Full payment', 'card', 'NGN', '103.55.14.5', 1,
     '{}'::json, 200, '{}'::json, '{}'::json, '{}'::json,
     '2025-01-17', '2025-01-17', 'RCT-004', NULL, 4),

    (5, 50000, 'PAY-REF-005', 'ACC-2025-005', TRUE,
     ARRAY['sponsored'], 'tuition', 900005,
     'Sponsor covered full fee', 'bank', 'NGN', '122.11.18.1', 1,
     '{}'::json, 200, '{}'::json, '{}'::json, '{}'::json,
     '2025-01-18', '2025-01-18', 'RCT-005', NULL, 5),

    (6, 30000, 'PAY-REF-006', 'ACC-2025-006', FALSE,
     ARRAY['enrollment'], 'tuition', 900006,
     'First installment', 'transfer', 'NGN', '103.14.22.6', 1,
     '{}'::json, 150, '{}'::json, '{}'::json, '{}'::json,
     '2025-01-20', '2025-01-20', 'RCT-006', NULL, 6),

    (7, 135000, 'PAY-REF-007', 'ACC-2025-007', FALSE,
     ARRAY['enrollment'], 'tuition', 900007,
     'Full payment', 'card', 'NGN', '102.88.11.2', 1,
     '{}'::json, 350, '{}'::json, '{}'::json, '{}'::json,
     '2025-01-21', '2025-01-21', 'RCT-007', NULL, 7),

    (8, 140000, 'PAY-REF-008', 'ACC-2025-008', FALSE,
     ARRAY['enrollment'], 'tuition', 900008,
     'Full payment', 'card', 'NGN', '102.88.11.5', 1,
     '{}'::json, 350, '{}'::json, '{}'::json, '{}'::json,
     '2025-01-22', '2025-01-22', 'RCT-008', NULL, 8),

    (9, 100000, 'PAY-REF-009', 'ACC-2025-009', TRUE,
     ARRAY['sponsored'], 'tuition', 900009,
     'Sponsor covered tuition', 'bank', 'NGN', '101.47.16.9', 1,
     '{}'::json, 200, '{}'::json, '{}'::json, '{}'::json,
     '2025-01-25', '2025-01-25', 'RCT-009', NULL, 9),

    (10, 50000, 'PAY-REF-010', 'ACC-2025-010', FALSE,
     ARRAY['enrollment'], 'tuition', 900010,
     'Part payment', 'transfer', 'NGN', '111.72.14.9', 1,
     '{}'::json, 150, '{}'::json, '{}'::json, '{}'::json,
     '2025-02-01', '2025-02-01', 'RCT-010', NULL, 10),

    (11, 90000, 'PAY-REF-011', 'ACC-2025-001', FALSE,
     ARRAY['enrollment'], 'tuition', 900011,
     'Part payment', 'transfer', 'NGN', '112.22.66.3', 1,
     '{}'::json, 200, '{}'::json, '{}'::json, '{}'::json,
     '2025-09-01', '2025-09-01', 'RCT-011', NULL, 11),

    (12, 65000, 'PAY-REF-012', 'ACC-2025-002', TRUE,
     ARRAY['sponsored'], 'tuition', 900012,
     'Sponsor payment', 'bank', 'NGN', '100.20.22.2', 1,
     '{}'::json, 200, '{}'::json, '{}'::json, '{}'::json,
     '2025-09-05', '2025-09-05', 'RCT-012', NULL, 12),

    (13, 100000, 'PAY-REF-013', 'ACC-2025-003', FALSE,
     ARRAY['enrollment'], 'tuition', 900013,
     'First installment', 'transfer', 'NGN', '100.91.32.1', 1,
     '{}'::json, 300, '{}'::json, '{}'::json, '{}'::json,
     '2025-09-09', '2025-09-09', 'RCT-013', NULL, 13),

    (14, 240000, 'PAY-REF-014', 'ACC-2025-004', FALSE,
     ARRAY['enrollment'], 'tuition', 900014,
     'Full payment', 'card', 'NGN', '103.22.16.6', 1,
     '{}'::json, 450, '{}'::json, '{}'::json, '{}'::json,
     '2025-09-11', '2025-09-11', 'RCT-014', NULL, 14),

    (15, 140000, 'PAY-REF-015', 'ACC-2025-005', TRUE,
     ARRAY['sponsored'], 'tuition', 900015,
     'Sponsor full coverage', 'bank', 'NGN', '103.22.11.8', 1,
     '{}'::json, 350, '{}'::json, '{}'::json, '{}'::json,
     '2025-09-15', '2025-09-15', 'RCT-015', NULL, 15);

-- ============================================
-- PART 4 STARTS & PART 3 ENDS
-- ============================================

-- ============================================
-- CORRECT INSERT INTO mcq_tests (4 tests)
-- ============================================

INSERT INTO mcq_tests (
    id, test_name, file_name, diet_name, paper_code,
    course_spec, high_score, duration, date_uploaded, file_id
)
VALUES
    (1, 'QM Basic Test', 'QM_test1.pdf', 'June 2025 Diet', 'QM',
     'QM 2025_June', 30, 25, '2025-03-10', NULL),

    (2, 'AP Astrophysics MCQ Set A', 'AP_setA.pdf', 'June 2025 Diet', 'AP',
     'AP 2025_June', 40, 35, '2025-03-12', NULL),

    (3, 'QFT Advanced Quantum Field Test', 'QFT_test1.pdf', 'December 2025 Diet', 'QFT',
     'QFT 2025_Dec', 50, 45, '2025-09-15', NULL),

    (4, 'PSE Planetary Science Quick Quiz', 'PSE_quiz1.pdf', 'December 2025 Diet', 'PSE',
     'PSE 2025_Dec', 35, 30, '2025-09-20', NULL);

-- ==========
-- ==========

-- ============================================
-- CORRECT INSERT INTO mcq_history (20 rows)
-- ============================================

INSERT INTO mcq_history (
    id, course_spec, score, high_score, result, code, date_taken,
    student_id, test_id
)
VALUES
    -- Test 1 (QM – 30 marks)
    (1,  'QM 2025_June', 25, 30, '{"1":["A","A"],"2":["B","B"],"3":["C","C"]}', 'MCQ-QM-001', '2025-03-15', 1, 1),
    (2,  'QM 2025_June', 22, 30, '{"1":["A","A"],"2":["C","B"],"3":["D","C"]}', 'MCQ-QM-002', '2025-03-15', 2, 1),
    (3,  'QM 2025_June', 27, 30, '{"1":["A","A"],"2":["B","B"],"3":["D","D"]}', 'MCQ-QM-003', '2025-03-15', 3, 1),
    (4,  'QM 2025_June', 18, 30, '{"1":["A","B"],"2":["B","C"],"3":["C","D"]}', 'MCQ-QM-004', '2025-03-15', 4, 1),
    (5,  'QM 2025_June', 20, 30, '{"1":["A","A"],"2":["D","B"],"3":["B","C"]}', 'MCQ-QM-005', '2025-03-15', 5, 1),

    -- Test 2 (AP – 40 marks)
    (6,  'AP 2025_June', 30, 40, '{"1":["A","A"],"2":["C","C"],"3":["D","D"]}', 'MCQ-AP-006', '2025-03-20', 6, 2),
    (7,  'AP 2025_June', 35, 40, '{"1":["B","B"],"2":["C","C"],"3":["A","A"]}', 'MCQ-AP-007', '2025-03-20', 7, 2),
    (8,  'AP 2025_June', 28, 40, '{"1":["C","A"],"2":["A","B"],"3":["D","D"]}', 'MCQ-AP-008', '2025-03-20', 8, 2),
    (9,  'AP 2025_June', 40, 40, '{"1":["A","A"],"2":["B","B"],"3":["C","C"]}', 'MCQ-AP-009', '2025-03-20', 9, 2),
    (10, 'AP 2025_June', 25, 40, '{"1":["A","C"],"2":["D","B"],"3":["C","D"]}', 'MCQ-AP-010', '2025-03-20', 10, 2),

    -- Test 3 (QFT – 50 marks)
    (11, 'QFT 2025_Dec', 45, 50, '{"1":["A","A"],"2":["C","C"],"3":["B","B"]}', 'MCQ-QFT-011', '2025-10-10', 1, 3),
    (12, 'QFT 2025_Dec', 38, 50, '{"1":["D","C"],"2":["C","C"],"3":["B","B"]}', 'MCQ-QFT-012', '2025-10-10', 2, 3),
    (13, 'QFT 2025_Dec', 50, 50, '{"1":["A","A"],"2":["B","B"],"3":["C","C"]}', 'MCQ-QFT-013', '2025-10-10', 3, 3),
    (14, 'QFT 2025_Dec', 41, 50, '{"1":["A","A"],"2":["B","C"],"3":["A","B"]}', 'MCQ-QFT-014', '2025-10-10', 4, 3),
    (15, 'QFT 2025_Dec', 37, 50, '{"1":["D","A"],"2":["C","B"],"3":["B","C"]}', 'MCQ-QFT-015', '2025-10-10', 5, 3),

    -- Test 4 (PSE – 35 marks)
    (16, 'PSE 2025_Dec', 30, 35, '{"1":["A","A"],"2":["D","C"],"3":["C","C"]}', 'MCQ-PSE-016', '2025-10-15', 6, 4),
    (17, 'PSE 2025_Dec', 32, 35, '{"1":["A","A"],"2":["C","C"],"3":["B","B"]}', 'MCQ-PSE-017', '2025-10-15', 7, 4),
    (18, 'PSE 2025_Dec', 27, 35, '{"1":["D","A"],"2":["C","C"],"3":["D","B"]}', 'MCQ-PSE-018', '2025-10-15', 8, 4),
    (19, 'PSE 2025_Dec', 35, 35, '{"1":["A","A"],"2":["B","B"],"3":["C","C"]}', 'MCQ-PSE-019', '2025-10-15', 9, 4),
    (20, 'PSE 2025_Dec', 21, 35, '{"1":["A","C"],"2":["D","B"],"3":["C","D"]}', 'MCQ-PSE-020', '2025-10-15', 10, 4);


-- ==========
-- ==========

-- ============================================
-- INSERT INTO attempts (10 rows)
-- ============================================
INSERT INTO attempts (
    id, email, first_name, last_name, user_type, phone_number,
    created_at, purpose, context, amount, closed_at,
    payment_reference, payment_status, failure_cause, other_data
)
VALUES
    (1, 'john.okoro@example.com', 'John', 'Okoro', 'student', '08031234567',
     '2025-02-01 10:15:00', 'registration', ARRAY['web','signup'], 35000,
     NULL, 'ATTEMPT-QM-001', 'pending', NULL,
     '{"dob":"2002-06-14","courses":["QM"],"notes":"First-time registration"}'),

    (2, 'amina.bello@example.com', 'Amina', 'Bello', 'student', '08145678901',
     '2025-02-02 14:22:00', 'payment', ARRAY['mobile','retry'], 40000,
     '2025-02-02 14:45:00', 'ATTEMPT-AP-002', 'success', NULL,
     '{"dob":"2000-11-03","courses":["AP"],"attempt_no":1}'),

    (3, 'segun.adeleke@example.com', 'Segun', 'Adeleke', 'guest', '09078901234',
     '2025-02-05 09:10:00', 'registration', ARRAY['web'], 35000,
     NULL, 'ATTEMPT-QM-003', 'pending', 'Card declined',
     '{"dob":"1999-05-21","courses":["QM"],"device":"Android"}'),

    (4, 'linda.james@example.com', 'Linda', 'James', 'student', '08098765432',
     '2025-02-08 11:40:00', 'enrollment', ARRAY['portal'], 50000,
     '2025-02-08 12:00:00', 'ATTEMPT-QFT-004', 'success', NULL,
     '{"dob":"1998-02-09","courses":["QFT","AP"],"promo_code":"FEB25"}'),

    (5, 'victor.emeka@example.com', 'Victor', 'Emeka', 'student', '08130294857',
     '2025-02-10 08:55:00', 'payment', ARRAY['web','retry'], 12000,
     NULL, 'ATTEMPT-PSE-005', 'pending', 'Insufficient funds',
     '{"dob":"2001-09-02","courses":["PSE"],"attempt_no":2}'),

    (6, 'bola.akin@example.com', 'Bola', 'Akin', 'guest', '09022446688',
     '2025-02-11 19:30:00', 'registration', ARRAY['mobile'], 35000,
     '2025-02-11 19:36:00', 'ATTEMPT-QM-006', 'success', NULL,
     '{"dob":"1997-12-12","courses":["QM"],"source":"Instagram Ad"}'),

    (7, 'mercy.udoh@example.com', 'Mercy', 'Udoh', 'student', '08066778899',
     '2025-02-12 16:10:00', 'payment', ARRAY['web'], 45000,
     NULL, 'ATTEMPT-AP-007', 'pending', NULL,
     '{"dob":"1996-07-18","courses":["AP","QM"],"extra_info":"Reattempt"}'),

    (8, 'tunde.folorunsho@example.com', 'Tunde', 'Folorunsho', 'student', '08177889900',
     '2025-02-14 13:00:00', 'enrollment', ARRAY['portal'], 48000,
     '2025-02-14 13:20:00', 'ATTEMPT-QFT-008', 'success', NULL,
     '{"dob":"1995-03-09","courses":["QFT"],"device":"iPhone"}'),

    (9, 'gloria.adams@example.com', 'Gloria', 'Adams', 'guest', '09055667788',
     '2025-02-15 17:44:00', 'registration', ARRAY['web','promo'], 30000,
     NULL, 'ATTEMPT-QM-009', 'pending', 'Network timeout',
     '{"dob":"2003-04-21","courses":["QM"],"promo_used":"NEW2025"}'),

    (10, 'peter.onoja@example.com', 'Peter', 'Onoja', 'student', '08044332211',
     '2025-02-18 12:33:00', 'payment', ARRAY['mobile'], 20000,
     '2025-02-18 12:45:00', 'ATTEMPT-PSE-010', 'success', NULL,
     '{"dob":"1994-10-12","courses":["PSE"],"receipt_requested":true}');


-- ============================================
-- PART 5 STARTS & PART 4 ENDS
-- ============================================

-- INSERT INTO reviews
INSERT INTO reviews (id, student_id, paper_id, diet_id, rating, paper_code, comment, created_at)
VALUES
    (1, 1, 101, 18, 10, 'QM', 'Great introduction to core Quantum Mechanics concepts—super easy to follow!', NOW()),
    (2, 2, 101, 29, 8, 'QM', 'Solid Quantum Mechanics overview, but could use more real-world applications.', NOW()),
    (3, 3, 102, 29, 10, 'MB', 'Molecular Biology explanations were detailed and very engaging!', NOW()),
    (4, 4, 103, 18, 6, 'OC', 'Organic Chemistry reactions were challenging but still well presented.', NOW()),
    (5, 5, 104, 29, 10, 'AP', 'Astrophysics content was amazing—especially the stellar formation modules.', NOW()),
    (6, 6, 105, 18, 8, 'GE', 'Genetics & Evolution concepts were clear, especially the evolutionary models.', NOW()),
    (7, 7, 106, 29, 10, 'TD', 'Thermodynamics laws and practical examples were incredibly well explained.', NOW()),
    (8, 8, 107, 18, 10, 'QFT', 'Advanced Quantum Field Theory lectures were deep but surprisingly intuitive.', NOW()),
    (9, 9, 108, 18, 8, 'AB', 'Astrobiology discussions were fascinating, especially on exoplanet environments.', NOW()),
    (10,10,110, 29, 10, 'PSE', 'Planetary Science content was excellent—great explanations of planetary formation!', NOW());


