"""Train one machine learning model."""

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

from hw3.config import ML_MODEL_NAME


def build_machine_learning_model(model_name: str = ML_MODEL_NAME):
    if model_name == "logistic_regression":
        return LogisticRegression(max_iter=1000)
    if model_name == "random_forest":
        return RandomForestClassifier(n_estimators=100, random_state=42)
    if model_name == "gradient_boosting":
        return GradientBoostingClassifier(random_state=42)
    if model_name == "svm":
        return SVC(probability=True, random_state=42)
    if model_name == "mlp":
        return MLPClassifier(max_iter=1000, random_state=42)
    raise ValueError(
        f"Unknown model: {model_name}. "
        "Use logistic_regression, random_forest, gradient_boosting, svm, or mlp."
    )


def train_model(pca_components: np.ndarray, target_labels: np.ndarray, model_name: str = ML_MODEL_NAME):
    model = build_machine_learning_model(model_name)
    model.fit(pca_components, target_labels)
    return model


def predict_long_probabilities(model, pca_components: np.ndarray) -> np.ndarray:
    probability_matrix = model.predict_proba(pca_components)
    positive_class_index = list(model.classes_).index(1)
    return probability_matrix[:, positive_class_index]
