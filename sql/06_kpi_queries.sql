-- KPI definitions (identical to src/kpi_engine.py and powerbi/DAX_Measures.md)
SELECT COUNT(*) AS total_bookings,
       SUM(Booking_Status = 'Success') AS successful_bookings,
       ROUND(100 * SUM(Booking_Status = 'Success') / COUNT(*), 2) AS success_rate_pct,
       ROUND(100 * SUM(Booking_Status IN ('Canceled by Customer','Canceled by Driver')) / COUNT(*), 2) AS cancellation_rate_pct,
       SUM(Booking_Value) AS total_booking_value,                                   -- intended value, all statuses
       SUM(CASE WHEN Booking_Status='Success' THEN Booking_Value END) AS successful_booking_value,
       SUM(CASE WHEN Booking_Status='Success' AND Incomplete_Rides='No' THEN Booking_Value END) AS fully_completed_value,
       ROUND(AVG(CASE WHEN Booking_Status='Success' THEN Ride_Distance END), 3) AS avg_ride_distance,
       ROUND(AVG(Customer_Rating), 3) AS avg_customer_rating, ROUND(AVG(Driver_Rating), 3) AS avg_driver_rating
FROM ola_bookings;
