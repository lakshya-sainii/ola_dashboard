# Data dictionary (sheet `July`, 103,024 rows, 2024-07-01 to 2024-07-31)
| Column | Meaning | Null rule |
|---|---|---|
| Date / Time | Booking timestamp (Date holds date+time; Time duplicates the time part, 0 mismatches) | never null |
| Booking_ID | Unique booking key (0 duplicates) | never null |
| Booking_Status | Success 63,967 / Canceled by Driver 18,434 / Canceled by Customer 10,499 / Driver Not Found 10,124 | never null |
| Customer_ID | 94,544 distinct customers; max 5 bookings each | never null |
| Vehicle_Type | Prime Sedan, Prime SUV, Prime Plus, Mini, Auto, Bike, eBike (shown as E-Bike) | never null |
| Pickup_Location, Drop_Location | Place names | never null |
| V_TAT, C_TAT | Turnaround times (units not documented in source) | null unless Success |
| Canceled_Rides_by_Customer / _by_Driver | Recorded reason | null unless that cancellation |
| Incomplete_Rides, _Reason | Yes (3,926) / No (60,041) flag inside Success bookings | null unless Success |
| Booking_Value | Quoted value for every booking; revenue only when Success | never null, 100-2,999 |
| Payment_Method | Cash, UPI, Credit Card, Debit Card | null unless Success |
| Ride_Distance | km; 0 for every non-success booking | never null |
| Driver_Ratings, Customer_Rating | 3.0-5.0 | null unless Success |
| Vehicle Images | Icon URL, dropped | - |

Engineered: Timestamp, Booking_Date, Booking_Hour, Day, Day_Name, Day_Of_Week, Week, Is_Weekend, Is_Peak_Hour (top-quartile hours, data-derived), Time_Of_Day, Status_Category, Is_Success/Is_Incomplete/Is_Completed_Ride, Cancellation_Category/Reason, Revenue/Distance/Rating groups.
