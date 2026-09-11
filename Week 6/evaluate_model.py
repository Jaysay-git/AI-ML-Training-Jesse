import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import accuracy_score


# Load dataset
df = pd.read_csv("hospital_risk_dataset.csv")

X = df.drop("high_risk", axis=1)
y = df["high_risk"]


# Features
categorical_features = ["gender"]

numerical_features = [
    "age",
    "temperature",
    "heart_rate",
    "oxygen_saturation",
    "previous_admissions",
    "symptom_count",
    "chronic_condition",
]


# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
        (
            "numerical",
            StandardScaler(),
            numerical_features,
        ),
    ]
)


# Model
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
            ),
        ),
    ]
)


# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


# Train model
model.fit(X_train, y_train)


# Training accuracy
train_predictions = model.predict(X_train)

train_accuracy = accuracy_score(
    y_train,
    train_predictions
)


# Test accuracy
test_predictions = model.predict(X_test)

test_accuracy = accuracy_score(
    y_test,
    test_predictions
)


# Cross-validation
cv_scores = cross_val_score(
    model,
    X,
    y,
    cv=5,
    scoring="accuracy"
)


print("\n--- Overfitting Check ---")

print(f"Training Accuracy: {train_accuracy:.4f}")
print(f"Testing Accuracy:  {test_accuracy:.4f}")

print("\n--- 5-Fold Cross Validation ---")

print("CV Scores:")

for score in cv_scores:
    print(f"{score:.4f}")

print(f"\nMean CV Accuracy: {cv_scores.mean():.4f}")
print(f"CV Standard Deviation: {cv_scores.std():.4f}")