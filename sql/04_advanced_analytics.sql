-- Advanced analytics. Dialect: MySQL 8.0 (HOUR, DAYNAME, DATE). sql/validate_sql.py runs a SQLite translation.
-- A1 Hourly demand and success conversion
SELECT HOUR(Booking_Timestamp) AS booking_hour, COUNT(*) AS bookings,
       SUM(Booking_Status = 'Success') AS successful,
       ROUND(100 * SUM(Booking_Status = 'Success') / COUNT(*), 2) AS success_pct
FROM ola_bookings GROUP BY booking_hour ORDER BY bookings DESC;
-- A2 Daily trend with 7-day moving average (window function)
WITH daily AS (SELECT DATE(Booking_Timestamp) AS d, COUNT(*) AS bookings FROM ola_bookings GROUP BY d)
SELECT d, bookings, ROUND(AVG(bookings) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS ma7 FROM daily;
-- A3 Vehicle ranking by successful booking value with revenue share
WITH v AS (SELECT Vehicle_Type, SUM(Booking_Value) AS success_value FROM ola_bookings
           WHERE Booking_Status = 'Success' GROUP BY Vehicle_Type)
SELECT Vehicle_Type, success_value, RANK() OVER (ORDER BY success_value DESC) AS value_rank,
       ROUND(100 * success_value / SUM(success_value) OVER (), 2) AS share_pct FROM v;
-- A4 Payment-method distribution (successful rides only; non-success have no payment)
SELECT Payment_Method, COUNT(*) AS rides, SUM(Booking_Value) AS value,
       ROUND(100 * SUM(Booking_Value) / SUM(SUM(Booking_Value)) OVER (), 2) AS value_share_pct
FROM ola_bookings WHERE Booking_Status = 'Success' GROUP BY Payment_Method ORDER BY value DESC;
-- A5 Cancellation reasons Pareto (cumulative share)
WITH r AS (SELECT COALESCE(Canceled_Rides_by_Customer, Canceled_Rides_by_Driver) AS reason, COUNT(*) AS n
           FROM ola_bookings WHERE Booking_Status IN ('Canceled by Customer','Canceled by Driver') GROUP BY reason)
SELECT reason, n, ROUND(100 * SUM(n) OVER (ORDER BY n DESC) / SUM(n) OVER (), 2) AS cum_pct FROM r ORDER BY n DESC;
-- A6 Vehicle cancellation rate by conditional aggregation
SELECT Vehicle_Type, COUNT(*) AS bookings,
       ROUND(100 * SUM(Booking_Status IN ('Canceled by Customer','Canceled by Driver')) / COUNT(*), 2) AS cancel_pct,
       ROUND(100 * SUM(Booking_Status = 'Driver Not Found') / COUNT(*), 2) AS no_driver_pct
FROM ola_bookings GROUP BY Vehicle_Type ORDER BY cancel_pct DESC;
-- A7 Repeat behaviour: how many customers booked more than once (measurable here)
WITH c AS (SELECT Customer_ID, COUNT(*) AS n FROM ola_bookings GROUP BY Customer_ID)
SELECT n AS bookings_per_customer, COUNT(*) AS customers FROM c GROUP BY n ORDER BY n;
-- A8 Anomaly candidates: booking values above Q3 + 1.5*IQR within vehicle type (approximation using ranked percentiles)
WITH ranked AS (SELECT Booking_ID, Vehicle_Type, Booking_Value,
       PERCENT_RANK() OVER (PARTITION BY Vehicle_Type ORDER BY Booking_Value) AS pr FROM ola_bookings)
SELECT Vehicle_Type, COUNT(*) AS top_1pct_rows, MIN(Booking_Value) AS threshold_value FROM ranked WHERE pr >= 0.99 GROUP BY Vehicle_Type;
-- A9 Fare per km (successful rides) by vehicle
SELECT Vehicle_Type, ROUND(SUM(Booking_Value) / SUM(Ride_Distance), 2) AS value_per_km
FROM ola_bookings WHERE Booking_Status = 'Success' GROUP BY Vehicle_Type ORDER BY value_per_km DESC;
-- A10 Operational efficiency: average vehicle/customer turnaround (V_TAT, C_TAT) by vehicle
SELECT Vehicle_Type, ROUND(AVG(V_TAT),1) AS avg_v_tat, ROUND(AVG(C_TAT),1) AS avg_c_tat FROM ola_bookings
WHERE Booking_Status = 'Success' GROUP BY Vehicle_Type;
