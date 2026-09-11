import numpy as np
import pandas as pd


# Make results reproducible
np.random.seed(42)

# Number of synthetic patients
n = 1000


# Generate patient features
age = np.random.randint(18, 90, n)

gender = np.random.choice(
    ["M", "F"],
    size=n
)

temperature = np.round(
    np.random.normal(37.0, 0.7, n),
    1
)

heart_rate = np.random.randint(
    55,
    130,
    n
)

oxygen_saturation = np.round(
    np.random.normal(96, 2.5, n),
    1
)

previous_admissions = np.random.poisson(
    1.5,
    n
)

symptom_count = np.random.randint(
    0,
    8,
    n
)

chronic_condition = np.random.choice(
    [0, 1],
    size=n,
    p=[0.65, 0.35]
)


# Create a risk score
risk_score = (
    (age > 65) * 2
    + (temperature > 38.0) * 2
    + (heart_rate > 100) * 2
    + (oxygen_saturation < 94) * 3
    + (previous_admissions >= 3) * 1
    + (symptom_count >= 5) * 2
    + chronic_condition * 2
)


# Add a little randomness so the model
# doesn't get a perfectly predictable target
noise = np.random.binomial(1, 0.08, n)

high_risk = (
    ((risk_score + noise) >= 5)
    .astype(int)
)


# Create DataFrame
df = pd.DataFrame({
    "age": age,
    "gender": gender,
    "temperature": temperature,
    "heart_rate": heart_rate,
    "oxygen_saturation": oxygen_saturation,
    "previous_admissions": previous_admissions,
    "symptom_count": symptom_count,
    "chronic_condition": chronic_condition,
    "high_risk": high_risk
})


# Display information
print("Dataset shape:")
print(df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset information:")
print(df.info())

print("\nClass distribution:")
print(df["high_risk"].value_counts())

print("\nClass percentages:")
print(df["high_risk"].value_counts(normalize=True) * 100)


# Save dataset
df.to_csv(
    "hospital_risk_dataset.csv",
    index=False
)

print("\nDataset saved to hospital_risk_dataset.csv")