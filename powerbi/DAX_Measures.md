# DAX measures (table `Bookings`, loaded from data/processed/ola_clean.csv)
```
Total Bookings = COUNTROWS(Bookings)
Successful Bookings = CALCULATE([Total Bookings], Bookings[Booking_Status] = "Success")
Customer Cancellations = CALCULATE([Total Bookings], Bookings[Booking_Status] = "Canceled by Customer")
Driver Cancellations = CALCULATE([Total Bookings], Bookings[Booking_Status] = "Canceled by Driver")
Driver Not Found = CALCULATE([Total Bookings], Bookings[Booking_Status] = "Driver Not Found")
Incomplete Rides = CALCULATE([Total Bookings], Bookings[Incomplete_Rides] = "Yes")
Success Rate = DIVIDE([Successful Bookings], [Total Bookings])
Cancellation Rate = DIVIDE([Customer Cancellations] + [Driver Cancellations], [Total Bookings])
Total Booking Value = SUM(Bookings[Booking_Value])                       -- intended value, all statuses
Successful Booking Value = CALCULATE(SUM(Bookings[Booking_Value]), Bookings[Booking_Status] = "Success")
Fully Completed Value = CALCULATE(SUM(Bookings[Booking_Value]), Bookings[Booking_Status] = "Success", Bookings[Incomplete_Rides] = "No")
Avg Ride Distance = CALCULATE(AVERAGE(Bookings[Ride_Distance]), Bookings[Booking_Status] = "Success")
Total Ride Distance = CALCULATE(SUM(Bookings[Ride_Distance]), Bookings[Booking_Status] = "Success")
Avg Customer Rating = AVERAGE(Bookings[Customer_Rating])               -- blanks ignored
Avg Driver Rating = AVERAGE(Bookings[Driver_Rating])
Dynamic Title = "Bookings: " & FORMAT([Total Bookings], "#,0") & " | Success " & FORMAT([Success Rate], "0.0%")
```
Expected values (validated in Python/SQL): Total 103,024 | Successful 63,967 | Success rate 62.09% | Cancellation rate 28.08% | Total value 56,534,614 | Successful value 35,080,467 | Fully completed 32,829,985 | Avg distance 22.854 | Avg ratings 3.998 / 3.997.
Note: in Power Query keep Driver_Rating blank (null) for non-success rows; do not replace with 0.
