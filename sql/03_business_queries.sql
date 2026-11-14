-- The 10 business questions from the project brief. Portable ANSI SQL (MySQL 8 + SQLite).
-- Q1  Retrieve all successful bookings
SELECT * FROM ola_bookings WHERE Booking_Status = 'Success';
-- Q2  Average ride distance per vehicle type (successful rides; non-success rows carry 0 km by design)
SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS avg_ride_distance
FROM ola_bookings WHERE Booking_Status = 'Success' GROUP BY Vehicle_Type ORDER BY avg_ride_distance DESC;
-- Q3  Total rides cancelled by customers
SELECT COUNT(*) AS cancelled_by_customers FROM ola_bookings WHERE Booking_Status = 'Canceled by Customer';
-- Q4  Top 5 customers by number of rides (all bookings; ties broken by Customer_ID for determinism)
SELECT Customer_ID, COUNT(*) AS total_bookings FROM ola_bookings
GROUP BY Customer_ID ORDER BY total_bookings DESC, Customer_ID LIMIT 5;
-- Q5  Rides cancelled by drivers for personal and car-related issues
SELECT COUNT(*) AS driver_cancel_personal_car FROM ola_bookings
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';
-- Q6  Max and min driver rating for Prime Sedan
SELECT MAX(Driver_Rating) AS max_rating, MIN(Driver_Rating) AS min_rating
FROM ola_bookings WHERE Vehicle_Type = 'Prime Sedan' AND Driver_Rating IS NOT NULL;
-- Q7  All rides paid with UPI
SELECT * FROM ola_bookings WHERE Payment_Method = 'UPI';
-- Q8  Average customer rating per vehicle type
SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 3) AS avg_customer_rating
FROM ola_bookings WHERE Customer_Rating IS NOT NULL GROUP BY Vehicle_Type ORDER BY avg_customer_rating DESC;
-- Q9  Total booking value of successfully completed rides
--     ('Success' status; includes rides later flagged Incomplete = 'Yes'. See 06 for the stricter variant.)
SELECT SUM(Booking_Value) AS total_successful_booking_value FROM ola_bookings WHERE Booking_Status = 'Success';
-- Q10 Incomplete rides with reasons
SELECT Booking_ID, Customer_ID, Vehicle_Type, Booking_Value, Incomplete_Rides_Reason
FROM ola_bookings WHERE Incomplete_Rides = 'Yes';
