import random
from pathlib import Path

import pandas as pd


random.seed(42)

commodities = [
    {
        "commodity": "Rice",
        "category": "Grains",
        "unit": "1 kg",
        "prices": {"Lagos": 1800, "Ibadan": 1650, "Abuja": 1750},
    },
    {
        "commodity": "Beans",
        "category": "Grains",
        "unit": "1 kg",
        "prices": {"Lagos": 2200, "Ibadan": 2000, "Abuja": 2150},
    },
    {
        "commodity": "Maize",
        "category": "Grains",
        "unit": "1 kg",
        "prices": {"Lagos": 1200, "Ibadan": 1050, "Abuja": 1150},
    },
    {
        "commodity": "Garri",
        "category": "Grains",
        "unit": "1 kg",
        "prices": {"Lagos": 1100, "Ibadan": 950, "Abuja": 1050},
    },
    {
        "commodity": "Eggs",
        "category": "Protein",
        "unit": "1 crate (30 eggs)",
        "prices": {"Lagos": 5500, "Ibadan": 5000, "Abuja": 5300},
    },
    {
        "commodity": "Chicken",
        "category": "Protein",
        "unit": "1 kg",
        "prices": {"Lagos": 6500, "Ibadan": 6000, "Abuja": 6300},
    },
    {
        "commodity": "Beef",
        "category": "Protein",
        "unit": "1 kg",
        "prices": {"Lagos": 7500, "Ibadan": 7000, "Abuja": 7300},
    },
    {
        "commodity": "Fish",
        "category": "Protein",
        "unit": "1 kg",
        "prices": {"Lagos": 5000, "Ibadan": 4600, "Abuja": 4800},
    },
    {
        "commodity": "Palm oil",
        "category": "Cooking essentials",
        "unit": "1 litre",
        "prices": {"Lagos": 2800, "Ibadan": 2600, "Abuja": 2700},
    },
    {
        "commodity": "Vegetable oil",
        "category": "Cooking essentials",
        "unit": "1 litre",
        "prices": {"Lagos": 3500, "Ibadan": 3300, "Abuja": 3400},
    },
    {
        "commodity": "Tomatoes",
        "category": "Vegetables",
        "unit": "1 kg",
        "prices": {"Lagos": 2500, "Ibadan": 2200, "Abuja": 2400},
    },
    {
        "commodity": "Yam",
        "category": "Tubers",
        "unit": "1 tuber",
        "prices": {"Lagos": 3000, "Ibadan": 2700, "Abuja": 2900},
    },
]

locations = {
    "Lagos": "Lagos State",
    "Ibadan": "Oyo State",
    "Abuja": "Federal Capital Territory",
}

months = pd.date_range(
    start="2025-01-01",
    end="2025-12-01",
    freq="MS",
)

records = []

for item in commodities:
    for location, state in locations.items():
        base_price = item["prices"][location]

        for month_index, date in enumerate(months):
            monthly_trend = 1 + (0.025 * month_index)
            random_variation = random.uniform(-0.04, 0.04)

            price = base_price * monthly_trend * (1 + random_variation)

            records.append({
                "commodity": item["commodity"],
                "category": item["category"],
                "location": location,
                "state": state,
                "unit": item["unit"],
                "price": round(price, 2),
                "recorded_at": date.strftime("%Y-%m-%d"),
                "data_source": "SIMULATED",
            })

df = pd.DataFrame(records)

output_path = Path("data/raw/commodity_prices.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

print("Dataset generated successfully.")
print(f"Output file: {output_path}")
print(f"Total records: {len(df)}")
print(f"Unique commodities: {df['commodity'].nunique()}")
print(f"Unique locations: {df['location'].nunique()}")
print(f"Date range: {df['recorded_at'].min()} to {df['recorded_at'].max()}")
print(f"Data sources: {df['data_source'].unique().tolist()}")

print("\nFirst 5 records:")
print(df.head().to_string(index=False))
