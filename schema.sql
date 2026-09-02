-- AtliQ Grands Hospitality Relational Database Schema DDL

-- 1. Dim Hotels
CREATE TABLE IF NOT EXISTS dim_hotels (
    property_id INT PRIMARY KEY,
    property_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL
);

-- 2. Dim Rooms
CREATE TABLE IF NOT EXISTS dim_rooms (
    room_id VARCHAR(10) PRIMARY KEY,
    room_class VARCHAR(50) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL
);

-- 3. Dim Date
CREATE TABLE IF NOT EXISTS dim_date (
    date VARCHAR(10) PRIMARY KEY, -- YYYY-MM-DD
    mmm_yy VARCHAR(10) NOT NULL,
    week_no VARCHAR(10) NOT NULL,
    day_type VARCHAR(15) NOT NULL, -- weekday / weekend
    day_of_week VARCHAR(15) NOT NULL
);

-- 4. Fact Aggregated Bookings (Capacity & Bookings)
CREATE TABLE IF NOT EXISTS fact_aggregated_bookings (
    property_id INT NOT NULL,
    check_in_date VARCHAR(10) NOT NULL,
    room_category VARCHAR(10) NOT NULL,
    successful_bookings INT NOT NULL,
    capacity INT NOT NULL,
    PRIMARY KEY (property_id, check_in_date, room_category),
    FOREIGN KEY (property_id) REFERENCES dim_hotels(property_id),
    FOREIGN KEY (room_category) REFERENCES dim_rooms(room_id),
    FOREIGN KEY (check_in_date) REFERENCES dim_date(date)
);

-- 5. Fact Bookings (Granular Reservation Level)
CREATE TABLE IF NOT EXISTS fact_bookings (
    booking_id VARCHAR(20) PRIMARY KEY,
    property_id INT NOT NULL,
    booking_date VARCHAR(10) NOT NULL,
    check_in_date VARCHAR(10) NOT NULL,
    checkout_date VARCHAR(10) NOT NULL,
    no_guests INT NOT NULL,
    room_category VARCHAR(10) NOT NULL,
    booking_platform VARCHAR(50) NOT NULL,
    ratings_given DECIMAL(2, 1),
    booking_status VARCHAR(20) NOT NULL, -- Checked Out, Cancelled, No Show
    revenue_generated DECIMAL(10, 2) NOT NULL,
    revenue_realized DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (property_id) REFERENCES dim_hotels(property_id),
    FOREIGN KEY (room_category) REFERENCES dim_rooms(room_id),
    FOREIGN KEY (check_in_date) REFERENCES dim_date(date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bk_checkin ON fact_bookings(check_in_date);
CREATE INDEX IF NOT EXISTS idx_bk_prop ON fact_bookings(property_id);
CREATE INDEX IF NOT EXISTS idx_bk_status ON fact_bookings(booking_status);
CREATE INDEX IF NOT EXISTS idx_bk_platform ON fact_bookings(booking_platform);
