-- Data validation checks. Every query should return 0 violations unless noted.
SELECT COUNT(*) AS total_rows, COUNT(DISTINCT Booking_ID) AS distinct_ids FROM ola_bookings;
SELECT 'bad_rating' AS rule, COUNT(*) AS violations FROM ola_bookings
 WHERE Driver_Rating NOT BETWEEN 1 AND 5 OR Customer_Rating NOT BETWEEN 1 AND 5;
SELECT 'nonpositive_value' AS rule, COUNT(*) AS violations FROM ola_bookings WHERE Booking_Value <= 0;
SELECT 'success_zero_distance' AS rule, COUNT(*) AS violations FROM ola_bookings
 WHERE Booking_Status = 'Success' AND Ride_Distance = 0;
SELECT 'nonsuccess_has_distance' AS rule, COUNT(*) AS violations FROM ola_bookings
 WHERE Booking_Status <> 'Success' AND Ride_Distance > 0;
SELECT 'nonsuccess_has_rating_or_payment' AS rule, COUNT(*) AS violations FROM ola_bookings
 WHERE Booking_Status <> 'Success' AND (Driver_Rating IS NOT NULL OR Payment_Method IS NOT NULL);
SELECT 'cancel_reason_status_mismatch' AS rule, COUNT(*) AS violations FROM ola_bookings
 WHERE (Booking_Status = 'Canceled by Customer') <> (Canceled_Rides_by_Customer IS NOT NULL)
    OR (Booking_Status = 'Canceled by Driver')   <> (Canceled_Rides_by_Driver   IS NOT NULL);
SELECT MIN(Booking_Timestamp) AS first_booking, MAX(Booking_Timestamp) AS last_booking FROM ola_bookings;
SELECT Booking_Status, COUNT(*) AS n FROM ola_bookings GROUP BY Booking_Status;
SELECT Vehicle_Type,  COUNT(*) AS n FROM ola_bookings GROUP BY Vehicle_Type;
