"""
Hospitality Metrics Engine for AtliQ Grands.
Loads operational data, populates SQLite DB, and computes industry-standard hospitality KPIs:
RevPAR, ADR, Occupancy %, Realisation %, DSRN, URN, Cancellation %, etc.
"""

import csv
import logging
import os
import sqlite3
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("HospitalityMetricsEngine")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "atliq_grands.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

class HospitalityMetricsEngine:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None

    def init_db(self):
        logger.info(f"Initializing Hospitality Database at {self.db_path}...")
        self.conn = sqlite3.connect(self.db_path)
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    def load_data(self):
        logger.info("Loading CSV data into relational database...")
        cursor = self.conn.cursor()

        # Load Hotels
        with open(os.path.join(DATA_DIR, "dim_hotels.csv"), "r", encoding="utf-8") as f:
            cursor.executemany("INSERT OR REPLACE INTO dim_hotels VALUES (:property_id, :property_name, :category, :city)", csv.DictReader(f))

        # Load Rooms
        with open(os.path.join(DATA_DIR, "dim_rooms.csv"), "r", encoding="utf-8") as f:
            cursor.executemany("INSERT OR REPLACE INTO dim_rooms VALUES (:room_id, :room_class, :base_price)", csv.DictReader(f))

        # Load Dates
        with open(os.path.join(DATA_DIR, "dim_date.csv"), "r", encoding="utf-8") as f:
            cursor.executemany("INSERT OR REPLACE INTO dim_date VALUES (:date, :mmm_yy, :week_no, :day_type, :day_of_week)", csv.DictReader(f))

        # Load Aggregated Bookings
        with open(os.path.join(DATA_DIR, "fact_aggregated_bookings.csv"), "r", encoding="utf-8") as f:
            cursor.executemany("INSERT OR REPLACE INTO fact_aggregated_bookings VALUES (:property_id, :check_in_date, :room_category, :successful_bookings, :capacity)", csv.DictReader(f))

        # Load Fact Bookings
        with open(os.path.join(DATA_DIR, "fact_bookings.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            formatted = []
            for r in reader:
                formatted.append({
                    "booking_id": r["booking_id"],
                    "property_id": int(r["property_id"]),
                    "booking_date": r["booking_date"],
                    "check_in_date": r["check_in_date"],
                    "checkout_date": r["checkout_date"],
                    "no_guests": int(r["no_guests"]),
                    "room_category": r["room_category"],
                    "booking_platform": r["booking_platform"],
                    "ratings_given": float(r["ratings_given"]) if r["ratings_given"] else None,
                    "booking_status": r["booking_status"],
                    "revenue_generated": float(r["revenue_generated"]),
                    "revenue_realized": float(r["revenue_realized"])
                })
            cursor.executemany("""
                INSERT OR REPLACE INTO fact_bookings VALUES (
                    :booking_id, :property_id, :booking_date, :check_in_date, :checkout_date,
                    :no_guests, :room_category, :booking_platform, :ratings_given,
                    :booking_status, :revenue_generated, :revenue_realized
                )
            """, formatted)

        self.conn.commit()
        logger.info("All tables populated successfully.")

    def compute_executive_kpis(self):
        """
        Computes overall high-level hospitality KPIs across all properties.
        """
        cursor = self.conn.cursor()

        # Total Capacity (Total Sellable Room Nights - DSRN Total)
        cursor.execute("SELECT SUM(capacity) FROM fact_aggregated_bookings")
        total_capacity = cursor.fetchone()[0] or 0

        # Total Bookings & Successful bookings
        cursor.execute("SELECT COUNT(*), SUM(CASE WHEN booking_status = 'Checked Out' THEN 1 ELSE 0 END), SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END), SUM(CASE WHEN booking_status = 'No Show' THEN 1 ELSE 0 END) FROM fact_bookings")
        total_bookings, checked_out, cancelled, no_show = cursor.fetchone()

        # Revenue
        cursor.execute("SELECT SUM(revenue_generated), SUM(revenue_realized) FROM fact_bookings")
        rev_gen, rev_real = cursor.fetchone()

        # Average Rating
        cursor.execute("SELECT AVG(ratings_given) FROM fact_bookings WHERE ratings_given IS NOT NULL")
        avg_rating = cursor.fetchone()[0] or 0.0

        # Hospitality Calculations
        # 1. Occupancy % = Total Bookings / Total Capacity
        occupancy_pct = round((total_bookings / total_capacity) * 100, 2) if total_capacity > 0 else 0
        
        # 2. ADR (Average Daily Rate) = Total Revenue Realized / Checked-out (or Total Sold)
        adr = round(rev_real / checked_out, 2) if checked_out > 0 else 0
        
        # 3. RevPAR (Revenue Per Available Room) = Total Revenue Realized / Total Capacity
        revpar = round(rev_real / total_capacity, 2) if total_capacity > 0 else 0
        
        # 4. Realisation % = Checked-out / Total Bookings
        realisation_pct = round((checked_out / total_bookings) * 100, 2) if total_bookings > 0 else 0
        
        # 5. Cancellation %
        cancellation_pct = round((cancelled / total_bookings) * 100, 2) if total_bookings > 0 else 0

        kpis = {
            "Total Capacity (DSRN)": total_capacity,
            "Total Bookings": total_bookings,
            "Checked Out (URN)": checked_out,
            "Cancelled": cancelled,
            "No Show": no_show,
            "Total Revenue Generated (INR)": round(rev_gen, 2),
            "Total Revenue Realized (INR)": round(rev_real, 2),
            "Occupancy %": occupancy_pct,
            "ADR (Average Daily Rate)": adr,
            "RevPAR (Revenue Per Available Room)": revpar,
            "Realisation %": realisation_pct,
            "Cancellation %": cancellation_pct,
            "Average Customer Rating": round(avg_rating, 2)
        }
        return kpis

if __name__ == "__main__":
    engine = HospitalityMetricsEngine()
    engine.init_db()
    engine.load_data()
    kpis = engine.compute_executive_kpis()
    print("\n=== AtliQ Grands Executive KPIs ===")
    for k, v in kpis.items():
        print(f"• {k}: {v}")
