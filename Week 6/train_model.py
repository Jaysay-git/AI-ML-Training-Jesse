import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# Load dataset
df = pd.read_csv("hospital_risk_dataset.csv")

print("Dataset loaded:", df.shape)


# Separate features and target
X = df.drop("high_risk", axis=1)
y = df["high_risk"]


# Identify categorical and numerical columns
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


# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


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


# Create machine-learning pipeline
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


# Train model
model.fit(X_train, y_train)


# Make predictions
y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]


# Calculate evaluation metrics
accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
)

recall = recall_score(
    y_test,
    y_pred,
)

f1 = f1_score(
    y_test,
    y_pred,
)

auc = roc_auc_score(
    y_test,
    y_probability,
)


# Display results
print("\n--- Model Evaluation ---")

print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"AUC:       {auc:.4f}")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred
    )
)


# Save model
joblib.dump(
    model,
    "hospital_risk_model.joblib"
)

print(
    "\nModel saved to "
    "hospital_risk_model.joblib"
)