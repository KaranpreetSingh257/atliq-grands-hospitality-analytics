# AtliQ Grands: Revenue Insights in Hospitality Domain

A strategic Hospitality Business Analytics & Revenue Optimization project analyzing operational data for AtliQ Grands luxury hotels to diagnose declining market share, plug revenue leaks, and formulate data-driven dynamic pricing strategies.

---

## 📌 Business Problem & Context
AtliQ Grands operates multiple luxury & business hotel properties across 4 metropolitan cities (Mumbai, Delhi, Bangalore, Hyderabad). Despite healthy market tourism, AtliQ Grands experienced a decline in market share and revenue leaks.

### Root Causes Diagnosed:
1. **Ineffective Flat Pricing Strategy**: Maintained fixed room rates across weekdays and weekends, missing out on 25-40% weekend leisure surge demand captured by competitors.
2. **High Third-Party OTA Cancellation Rates**: Platforms like MakeMyTrip and Booking.com suffered from a 25.8% cancellation rate with zero penalty friction, leaving inventory unmonetized.
3. **Sub-optimal Direct Booking Realization**: Heavy reliance on OTAs reduced net realizations due to high commission fees.

---

## 📊 Core Hospitality KPIs & Metrics Defined
- **RevPAR (Revenue Per Available Room)**: `Total Realized Revenue / Total Sellable Room Nights (DSRN)`
- **ADR (Average Daily Rate)**: `Total Realized Revenue / Utilized Room Nights (URN)`
- **Occupancy %**: `(Total Bookings / Total Capacity) * 100`
- **Realisation %**: `(Checked-out Bookings / Total Bookings) * 100`
- **DSRN (Daily Sellable Room Nights)**: Available daily inventory capacity across properties.
- **URN (Utilized Room Nights)**: Successfully checked-out guests generating full revenue.

---

## 💡 Dynamic Pricing & Revenue Recovery Strategy
Implemented an interactive simulation model demonstrating projected **+20% Revenue / Market Share Recovery**:
1. **Dynamic Weekend Surge (+25%)**: Increasing rates dynamically on Friday/Saturday when occupancy exceeds 75%.
2. **OTA Cancellation Policy Overhaul & Direct Loyalty Incentives**: Partial non-refundable deposit on OTA channels recovering ~15% of cancelled revenue.
3. **Room Tier Upselling Optimization**: Targeted upgrades from Standard (RT1) to Elite/Premium suites.

---

## 🚀 Quickstart & Execution

### 1. Generate Operational Dataset & Build Database
```bash
# Generate 3 months of operational data
python data_generator.py

# Populate SQLite relational database and compute executive KPIs
python metrics_engine.py
```

### 2. Run Diagnostics & Dynamic Pricing Simulation
```bash
python revenue_leak_diagnostics.py
```

### 3. Run Automated Metric Tests
```bash
python -m unittest tests/test_hospitality_metrics.py
```

### 4. Launch Interactive Executive Dashboard
Open `dashboard/index.html` in your browser or run:
```bash
python -m http.server 8001 --directory dashboard
```

---

## 📂 Project Structure
```
atliq-grands-hospitality-analytics/
├── data/
│   ├── dim_hotels.csv
│   ├── dim_rooms.csv
│   ├── dim_date.csv
│   ├── fact_aggregated_bookings.csv
│   └── fact_bookings.csv
├── power_bi_reference/
│   └── dax_hospitality_guide.md      # Power BI DAX formula reference
├── dashboard/
│   └── index.html                    # Interactive Hospitality Dashboard
├── tests/
│   └── test_hospitality_metrics.py   # Mathematical integrity unit tests
├── schema.sql                        # Relational schema DDL
├── data_generator.py                 # 3-Month operational data generator
├── metrics_engine.py                 # Hospitality KPI computation engine
├── revenue_leak_diagnostics.py       # Revenue leak diagnosis & 20% recovery
└── README.md
```
