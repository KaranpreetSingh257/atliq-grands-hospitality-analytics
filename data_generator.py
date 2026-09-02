"""
Operational dataset generator for AtliQ Grands Hospitality Domain.
Generates 3 months of granular operational data across luxury properties, room classes, and booking channels.
"""

import csv
import os
import random
from datetime import datetime, timedelta

random.seed(101)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Hotels
HOTELS = [
    {"property_id": 16558, "property_name": "AtliQ Grands", "category": "Luxury", "city": "Delhi"},
    {"property_id": 16559, "property_name": "AtliQ Exotica", "category": "Luxury", "city": "Mumbai"},
    {"property_id": 16560, "property_name": "AtliQ City", "category": "Business", "city": "Delhi"},
    {"property_id": 16561, "property_name": "AtliQ Blu", "category": "Luxury", "city": "Bangalore"},
    {"property_id": 16562, "property_name": "AtliQ Bay", "category": "Luxury", "city": "Hyderabad"},
    {"property_id": 16563, "property_name": "AtliQ Palace", "category": "Business", "city": "Hyderabad"},
    {"property_id": 17558, "property_name": "AtliQ Seasons", "category": "Business", "city": "Mumbai"},
    {"property_id": 17559, "property_name": "AtliQ Exotica", "category": "Luxury", "city": "Bangalore"},
]

# 2. Rooms
ROOMS = [
    {"room_id": "RT1", "room_class": "Standard", "base_price": 4500},
    {"room_id": "RT2", "room_class": "Elite", "base_price": 7500},
    {"room_id": "RT3", "room_class": "Premium", "base_price": 11000},
    {"room_id": "RT4", "room_class": "Presidential", "base_price": 18500},
]

# 3. Booking Platforms
PLATFORMS = ["MakeMyTrip", "Booking.com", "Logtrip", "Tripster", "Direct Online", "Direct Offline", "JourneyHub"]
PLATFORM_WEIGHTS = [0.30, 0.25, 0.15, 0.10, 0.08, 0.07, 0.05]

def generate_date_dimension(start_date, end_date):
    dates = []
    current = start_date
    while current <= end_date:
        is_weekend = 1 if current.weekday() in [4, 5] else 0 # Friday & Saturday treated as hospitality weekend
        dates.append({
            "date": current.strftime("%Y-%m-%d"),
            "mmm_yy": current.strftime("%b %y"),
            "week_no": f"W {current.isocalendar()[1]}",
            "day_type": "weekend" if is_weekend else "weekday",
            "day_of_week": current.strftime("%A")
        })
        current += timedelta(days=1)
    return dates

def generate_hospitality_data(start_date, end_date):
    dates = generate_date_dimension(start_date, end_date)
    
    aggregated_bookings = []
    bookings = []
    
    booking_id_counter = 100000
    
    # Capacity matrix per hotel and room class
    capacity_matrix = {
        "RT1": (25, 45),
        "RT2": (18, 35),
        "RT3": (10, 22),
        "RT4": (4, 8)
    }

    for d in dates:
        date_str = d["date"]
        is_weekend = d["day_type"] == "weekend"
        
        for hotel in HOTELS:
            prop_id = hotel["property_id"]
            
            for room in ROOMS:
                room_id = room["room_id"]
                cap_min, cap_max = capacity_matrix[room_id]
                capacity = random.randint(cap_min, cap_max)
                
                # Base occupancy rate: weekends have higher leisure demand
                # AtliQ Grands issue: Flat pricing caused revenue loss on peak weekends
                base_occ = random.uniform(0.68, 0.85) if is_weekend else random.uniform(0.48, 0.65)
                
                successful_bookings_count = min(capacity, int(capacity * base_occ))
                
                aggregated_bookings.append({
                    "property_id": prop_id,
                    "check_in_date": date_str,
                    "room_category": room_id,
                    "successful_bookings": successful_bookings_count,
                    "capacity": capacity
                })
                
                # Generate individual bookings
                for _ in range(successful_bookings_count):
                    booking_id_counter += 1
                    b_id = f"BK{booking_id_counter}"
                    
                    platform = random.choices(PLATFORMS, weights=PLATFORM_WEIGHTS)[0]
                    
                    # Room price with slight variance
                    base_price = room["base_price"]
                    
                    # Static/Flat pricing flaw of AtliQ Grands (only minor fluctuation)
                    price_variance = random.uniform(0.95, 1.05)
                    revenue_generated = round(base_price * price_variance, 2)
                    
                    # Booking outcome: Checked Out, Cancelled, No Show
                    # Higher cancellations on third-party OTAs with zero-fee cancellation policies
                    if platform in ["MakeMyTrip", "Booking.com", "Logtrip"]:
                        status_choice = random.choices(
                            ["Checked Out", "Cancelled", "No Show"],
                            weights=[0.68, 0.26, 0.06]
                        )[0]
                    else:
                        status_choice = random.choices(
                            ["Checked Out", "Cancelled", "No Show"],
                            weights=[0.82, 0.15, 0.03]
                        )[0]
                        
                    if status_choice == "Checked Out":
                        revenue_realized = revenue_generated
                        ratings = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.10, 0.20, 0.40, 0.25])[0]
                    elif status_choice == "Cancelled":
                        # Cancellation fee retention (usually 0% or small percentage)
                        revenue_realized = round(revenue_generated * 0.10, 2)
                        ratings = None
                    else: # No Show
                        revenue_realized = round(revenue_generated * 0.50, 2)
                        ratings = None
                        
                    bookings.append({
                        "booking_id": b_id,
                        "property_id": prop_id,
                        "booking_date": (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
                        "check_in_date": date_str,
                        "checkout_date": (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d"),
                        "no_guests": random.randint(1, 4),
                        "room_category": room_id,
                        "booking_platform": platform,
                        "ratings_given": ratings if ratings is not None else "",
                        "booking_status": status_choice,
                        "revenue_generated": revenue_generated,
                        "revenue_realized": revenue_realized
                    })
                    
    return dates, aggregated_bookings, bookings

def export_csv(data, filepath):
    if not data:
        return
    keys = data[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Exported {len(data)} records to {filepath}")

def generate_all_hospitality_data():
    print("Generating AtliQ Grands 3-month operational dataset...")
    start_date = datetime(2024, 5, 1)
    end_date = datetime(2024, 7, 31)
    
    dates, agg_bookings, bookings = generate_hospitality_data(start_date, end_date)
    
    export_csv(HOTELS, os.path.join(DATA_DIR, "dim_hotels.csv"))
    export_csv(ROOMS, os.path.join(DATA_DIR, "dim_rooms.csv"))
    export_csv(dates, os.path.join(DATA_DIR, "dim_date.csv"))
    export_csv(agg_bookings, os.path.join(DATA_DIR, "fact_aggregated_bookings.csv"))
    export_csv(bookings, os.path.join(DATA_DIR, "fact_bookings.csv"))
    print("Hospitality dataset generation complete.")

if __name__ == "__main__":
    generate_all_hospitality_data()
