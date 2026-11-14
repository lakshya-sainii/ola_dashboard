# Power BI build guide
**Status: no .pbix is shipped.** Power BI Desktop cannot run in the build environment, and a fake .pbix would be dishonest. Everything needed to build it in about an hour is here.

1. Get Data > Text/CSV > `data/processed/ola_clean.csv`. Keep Driver_Rating / Customer_Rating blank for non-success rows. Set Timestamp to Date/Time.
2. Model: single fact table is sufficient. Optional star schema: `DimVehicle` (Vehicle_Type), `DimDate` (CALENDAR of 1-31 Jul 2024), `DimPayment`, related 1:* to Bookings. Mark DimDate as the date table.
3. View > Themes > Browse for themes > `OLA_Theme.json`. Add measures from `DAX_Measures.md`.
4. Pages (match the brief): (1) Overview: KPI cards, line (Booking_Date), donut (Booking_Status). (2) Vehicle Type: clustered bar, matrix with conditional formatting, bubble scatter (Avg Ride Distance vs Success Rate). (3) Revenue: Successful Booking Value by Payment_Method, top-5 customers (Top N filter), waterfall. (4) Cancellation: reasons bar split by Cancellation_Category, decomposition tree, heat-style matrix Hour x Day_Name. (5) Ratings: histograms, average by vehicle, scatter Customer vs Driver rating.
5. Add navigation buttons, a drill-through page on Vehicle_Type, bookmarks per page, and Dynamic Title on card headers.
6. Reconcile every card against the expected values at the bottom of `DAX_Measures.md`.
Top-5 vehicle by distance: five vehicles tie near 25 km average, Auto is ~10 km; rank by Total Ride Distance instead.
