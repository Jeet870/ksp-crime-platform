-- create_tables.sql
-- Run this file to create all tables for the KSP Crime Platform

-- TABLE 1: officers
CREATE TABLE IF NOT EXISTS officers (
    officer_id      SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    badge_number    VARCHAR(20) UNIQUE NOT NULL,
    role            VARCHAR(50) NOT NULL,
    district        VARCHAR(100) NOT NULL,
    police_station  VARCHAR(100),
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE 2: firs
CREATE TABLE IF NOT EXISTS firs (
    fir_id              SERIAL PRIMARY KEY,
    fir_number          VARCHAR(50) UNIQUE NOT NULL,
    date_filed          DATE NOT NULL,
    time_filed          TIME,
    police_station      VARCHAR(100) NOT NULL,
    district            VARCHAR(100) NOT NULL,
    crime_type          VARCHAR(100) NOT NULL,
    ipc_sections        TEXT,
    location_description VARCHAR(255),
    latitude            DECIMAL(9, 6),
    longitude           DECIMAL(9, 6),
    description_text    TEXT NOT NULL,
    status              VARCHAR(50) DEFAULT 'open',
    filed_by_officer_id INTEGER REFERENCES officers(officer_id),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_firs_district ON firs(district);
CREATE INDEX IF NOT EXISTS idx_firs_date ON firs(date_filed);
CREATE INDEX IF NOT EXISTS idx_firs_crime_type ON firs(crime_type);

-- TABLE 3: accused
CREATE TABLE IF NOT EXISTS accused (
    accused_id      SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    alias           VARCHAR(100),
    age             INTEGER,
    gender          VARCHAR(10),
    address         TEXT,
    phone_number    VARCHAR(20),
    aadhaar_last4   CHAR(4),
    prior_cases_count INTEGER DEFAULT 0,
    district        VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE 4: fir_accused
CREATE TABLE IF NOT EXISTS fir_accused (
    id              SERIAL PRIMARY KEY,
    fir_id          INTEGER NOT NULL REFERENCES firs(fir_id),
    accused_id      INTEGER NOT NULL REFERENCES accused(accused_id),
    role_in_case    VARCHAR(100),
    arrest_status   VARCHAR(50) DEFAULT 'not_arrested',
    UNIQUE(fir_id, accused_id)
);

-- TABLE 5: victims
CREATE TABLE IF NOT EXISTS victims (
    victim_id       SERIAL PRIMARY KEY,
    fir_id          INTEGER NOT NULL REFERENCES firs(fir_id),
    name            VARCHAR(100) NOT NULL,
    age             INTEGER,
    gender          VARCHAR(10),
    address         TEXT,
    phone_number    VARCHAR(20),
    injury_details  TEXT
);

-- TABLE 6: vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id          SERIAL PRIMARY KEY,
    registration_number VARCHAR(20) UNIQUE,
    vehicle_type        VARCHAR(50),
    make_model          VARCHAR(100),
    color               VARCHAR(50),
    owner_accused_id    INTEGER REFERENCES accused(accused_id),
    fir_id              INTEGER REFERENCES firs(fir_id)
);

-- TABLE 7: bank_transactions
CREATE TABLE IF NOT EXISTS bank_transactions (
    transaction_id      SERIAL PRIMARY KEY,
    account_number      VARCHAR(50) NOT NULL,
    accused_id          INTEGER REFERENCES accused(accused_id),
    amount              DECIMAL(15, 2),
    transaction_date    DATE NOT NULL,
    transaction_type    VARCHAR(20),
    counterparty_account VARCHAR(50),
    flagged             BOOLEAN DEFAULT FALSE,
    flag_reason         TEXT
);

-- Verify all tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;