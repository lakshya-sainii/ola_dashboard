# Business insights (all figures calculated from the cleaned July 2024 data)
Format per finding: question | metric | result | interpretation | impact | action | limitation.

**1. How much demand becomes a ride?** Success rate | 63,967 / 103,024 = 62.09%. Cancelled 28.08% (28,933), no driver found 9.83% (10,124). Impact: ~38% of demand is unfulfilled. Action: treat failed bookings as the main lever. Limit: one month; no cause data beyond labels.

**2. Who cancels?** Drivers 18,434 vs customers 10,499. Top recorded reasons: Personal & Car related issue 6,542; Customer related issue 5,413; Customer was coughing/sick 3,654 (driver side); Driver is not moving towards pickup 3,175 and Driver asked to cancel 2,670 (customer side). Interpretation: the largest customer-side reasons point back at driver behaviour (together 5,845 of 10,499). Action: audit driver-initiated cancellation handling. Limit: reasons are labels, not verified causes; no individual is implicated.

**3. Do vehicles differ?** Success rate ranges 61.39% (Prime SUV) to 63.04% (Prime Sedan); chi-square p = 0.119, not significant. Mean customer rating 3.988-4.010; ANOVA p = 0.286, not significant. Booking counts 14,552-14,877. Auto averages 10.0 km versus ~25 km for the others (structural difference). Action: do not reallocate fleet on these gaps. Limit: no supply, cost or fare-rule data.

**4. Is there a demand peak?** Hourly bookings range 4,176 (18:00) to 4,408 (12:00), a spread of 5.4% of the mean (CV 1.4%); uniformity test p = 0.74. Monday-Wednesday look busier only because July has five of each; per-day averages are 3,253-3,385 for every weekday. Action: no evidence for hour-specific driver allocation. Limit: one month; the 'peak hour' flag is a mild relative label.

**5. Payment and value.** Successful booking value 35,080,467 (62.1% of total booking value 56,534,614); Cash 54.9%, UPI 40.4%, Credit 3.7%, Debit 1.0%. Fully completed value (excluding 3,926 incomplete) 32,829,985. Booking value is not profit; no cost data. Top 10% of customers hold 35.5% of total booking value, but 92% of customers book once, so this is not loyalty evidence.

**6. Incomplete rides.** 3,926 (6.1% of successes): Customer Demand 1,601, Vehicle Breakdown 1,591, Other 734. Vehicle breakdown is operationally addressable. Limit: incomplete rides are inside Success, so Success overstates fully completed trips.

**7. Ratings.** Customer 3.998 and driver 3.997 on average; 27.6% / 27.5% of ratings are <= 3.5; customer-driver rating correlation -0.003. Interpretation: no relationship; rating means hide a large low-rating share.

**8. Anomalies.** IQR flags are statistical outliers only. Booking_Value is right-skewed (skew 2.57) and uncorrelated with distance (r = 0.002 on successful rides), so fare does not appear to follow distance in this data. Not evidence of fraud.

**Data realism warning.** Uniform hours, equal vehicle shares, uncorrelated rating pairs and fare unrelated to distance suggest this dataset may be synthetic or heavily randomised. Present conclusions as descriptive of this file, not of real OLA operations.
