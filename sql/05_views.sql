CREATE OR REPLACE VIEW v_successful_rides AS SELECT * FROM ola_bookings WHERE Booking_Status = 'Success';
CREATE OR REPLACE VIEW v_vehicle_scorecard AS
SELECT Vehicle_Type, COUNT(*) AS bookings, SUM(Booking_Status = 'Success') AS successful,
       SUM(Booking_Value) AS total_booking_value,
       SUM(CASE WHEN Booking_Status = 'Success' THEN Booking_Value ELSE 0 END) AS successful_booking_value,
       AVG(CASE WHEN Booking_Status = 'Success' THEN Ride_Distance END) AS avg_distance,
       AVG(Customer_Rating) AS avg_customer_rating, AVG(Driver_Rating) AS avg_driver_rating
FROM ola_bookings GROUP BY Vehicle_Type;
CREATE OR REPLACE VIEW v_cancellations AS
SELECT Booking_ID, Vehicle_Type, Booking_Status, Booking_Timestamp,
       COALESCE(Canceled_Rides_by_Customer, Canceled_Rides_by_Driver) AS reason
FROM ola_bookings WHERE Booking_Status IN ('Canceled by Customer','Canceled by Driver');
CREATE OR REPLACE VIEW v_incomplete_rides AS
SELECT Booking_ID, Vehicle_Type, Booking_Value, Incomplete_Rides_Reason FROM ola_bookings WHERE Incomplete_Rides = 'Yes';
