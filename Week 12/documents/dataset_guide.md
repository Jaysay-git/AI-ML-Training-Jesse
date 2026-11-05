# Naija Cost of Living Intelligence

## Dataset Overview

This project uses a simulated dataset of essential food commodity prices
across three Nigerian locations.

## Coverage

- Period: January 2025 to December 2025
- Locations: Lagos, Ibadan, Abuja
- Commodities: 12
- Expected records: 432
- Currency: Nigerian Naira (NGN)

## Commodities

1. Rice - 1 kg
2. Beans - 1 kg
3. Maize - 1 kg
4. Garri - 1 kg
5. Eggs - 1 crate (30 eggs)
6. Chicken - 1 kg
7. Beef - 1 kg
8. Fish - 1 kg
9. Palm oil - 1 litre
10. Vegetable oil - 1 litre
11. Tomatoes - 1 kg
12. Yam - 1 tuber

## Data Source and Limitations

All initial prices are simulated for educational and demonstration purposes.

They are not verified market prices and must not be interpreted as official
Nigerian cost-of-living statistics.

The dataset is intended for demonstrating data processing, CRUD operations,
analytics, visualization, and AI-assisted querying.

## CSV Schema

- commodity
- category
- location
- state
- unit
- price
- recorded_at
- data_source

## Data Integrity

- Prices must be greater than zero.
- Each commodity-location-month combination must be unique.
- Every record must have a data_source value of SIMULATED.
- Dates must fall between January and December 2025.
