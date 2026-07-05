"""Standardize features and apply PCA."""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from hw3.config import PCA_VARIANCE_THRESHOLD


def fit_pca_on_training_features(training_features: pd.DataFrame) -> dict:
    feature_scaler = StandardScaler()
    scaled_training_features = feature_scaler.fit_transform(training_features)

    full_pca = PCA()
    full_pca.fit(scaled_training_features)
    cumulative_variance_ratio = np.cumsum(full_pca.explained_variance_ratio_)
    component_count = int(np.searchsorted(cumulative_variance_ratio, PCA_VARIANCE_THRESHOLD) + 1)

    pca_model = PCA(n_components=component_count)
    pca_training_components = pca_model.fit_transform(scaled_training_features)

    return {
        "feature_scaler": feature_scaler,
        "pca_model": pca_model,
        "component_count": component_count,
        "explained_variance_ratio": pca_model.explained_variance_ratio_,
        "cumulative_variance_ratio": np.cumsum(pca_model.explained_variance_ratio_),
        "pca_training_components": pca_training_components,
    }


def transform_features_with_pca(feature_matrix: pd.DataFrame, pca_bundle: dict) -> np.ndarray:
    scaled_features = pca_bundle["feature_scaler"].transform(feature_matrix)
    return pca_bundle["pca_model"].transform(scaled_features)
