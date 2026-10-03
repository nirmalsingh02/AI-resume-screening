import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)


# ============================================================
# 1. LOAD DATASET
# ============================================================

data = pd.read_csv("data/ml_training_data.csv")

print("\n===== DATASET =====")
print(data)


# ============================================================
# 2. SEPARATE FEATURES (X) AND TARGET (y)
# ============================================================

X = data[
    [
        "skill_match",
        "text_similarity",
        "experience"
    ]
]

y = data["result"]


# ============================================================
# 3. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# 4. CREATE ML MODEL
# ============================================================

model = LogisticRegression()


# ============================================================
# 5. TRAIN MODEL
# ============================================================

model.fit(X_train, y_train)

print("\nModel trained successfully!")


# ============================================================
# 6. SAVE TRAINED MODEL
# ============================================================

joblib.dump(
    model,
    "models/resume_classifier.pkl"
)

print("Model saved successfully!")
print("Location: models/resume_classifier.pkl")


# ============================================================
# 7. MAKE PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 8. ACCURACY
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n===== MODEL RESULTS =====")

print(f"Accuracy: {accuracy:.2f}")


# ============================================================
# 9. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)


# ============================================================
# 10. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\nConfusion Matrix:")
print(cm)


# ============================================================
# 11. DISPLAY CONFUSION MATRIX
# ============================================================

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=[
        "Not Suitable",
        "Suitable"
    ]
)

disp.plot()

plt.title(
    "AI Resume Screening - Confusion Matrix"
)

plt.tight_layout()

plt.savefig(
    "outputs/confusion_matrix.png"
)

plt.show()


# ============================================================
# 12. MODEL INFORMATION
# ============================================================

print("\n===== MODEL INFORMATION =====")

print("Algorithm: Logistic Regression")

print(
    "Features:",
    list(X.columns)
)

print(
    "Classes:",
    list(model.classes_)
)

print("\nTraining completed successfully! 🚀")