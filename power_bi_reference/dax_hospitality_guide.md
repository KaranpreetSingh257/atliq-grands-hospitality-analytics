# Power BI DAX Guide & Hospitality KPI Metrics Reference

This guide details all key hospitality domain metrics and DAX measures developed for the **AtliQ Grands Revenue Insights & Hospitality Dashboard**.

---

## 1. Core Hospitality Business Concepts

| Metric | Full Form | Formula / Definition | Business Importance |
| :--- | :--- | :--- | :--- |
| **RevPAR** | Revenue Per Available Room | `Total Revenue / Total Capacity (DSRN)` or `ADR * Occupancy %` | Core barometer of financial health and room inventory monetization. |
| **ADR** | Average Daily Rate | `Total Realized Revenue / Utilized Rooms (URN)` | Measures average rental income per paid occupied room per day. |
| **Occupancy %** | Room Occupancy Rate | `(Booked Rooms / Total Available Capacity) * 100` | Measures capacity utilization across luxury and business properties. |
| **Realisation %** | Booking Realisation Rate | `(Checked Out Bookings / Total Bookings) * 100` | Highlights revenue loss from cancellations and no-shows. |
| **DSRN** | Daily Sellable Room Nights | `SUM(fact_aggregated_bookings[capacity])` | Total capacity available to sell per night across properties. |
| **URN** | Utilized Room Nights | `COUNTROWS(FILTER(fact_bookings, status="Checked Out"))` | Successfully occupied room nights generating full revenue. |

---

## 2. Power BI DAX Formulas

### Revenue & Capacity Measures
```dax
-- Total Capacity (DSRN)
Total Capacity = SUM(fact_aggregated_bookings[capacity])

-- Total Successful Bookings
Total Bookings = COUNT(fact_bookings[booking_id])

-- Checked Out Bookings (Utilized Room Nights - URN)
Checked Out Bookings = 
CALCULATE(
    COUNT(fact_bookings[booking_id]),
    fact_bookings[booking_status] = "Checked Out"
)

-- Cancelled Bookings
Cancelled Bookings = 
CALCULATE(
    COUNT(fact_bookings[booking_id]),
    fact_bookings[booking_status] = "Cancelled"
)

-- Total Realized Revenue
Total Realized Revenue = SUM(fact_bookings[revenue_realized])

-- Total Generated Revenue (Gross Invoiced)
Total Generated Revenue = SUM(fact_bookings[revenue_generated])
```

### Core KPI Calculations
```dax
-- Occupancy Percentage
Occupancy % = DIVIDE([Total Bookings], [Total Capacity], 0)

-- Average Daily Rate (ADR)
ADR = DIVIDE([Total Realized Revenue], [Checked Out Bookings], 0)

-- Revenue Per Available Room (RevPAR)
RevPAR = DIVIDE([Total Realized Revenue], [Total Capacity], 0)

-- Realisation Percentage
Realisation % = DIVIDE([Checked Out Bookings], [Total Bookings], 0)

-- Cancellation Percentage
Cancellation % = DIVIDE([Cancelled Bookings], [Total Bookings], 0)
```

### Time Intelligence & Dynamic Slicers
```dax
-- Weekend vs Weekday RevPAR Comparison
RevPAR Weekend = 
CALCULATE(
    [RevPAR],
    dim_date[day_type] = "weekend"
)

RevPAR Weekday = 
CALCULATE(
    [RevPAR],
    dim_date[day_type] = "weekday"
)

-- Average Customer Review Rating
Average Rating = AVERAGE(fact_bookings[ratings_given])
```
