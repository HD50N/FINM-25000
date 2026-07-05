"""HW3 settings. Change these to customize the homework."""

DEFAULT_SYMBOL = "AAPL"
DATA_YEARS = 5
TRAIN_FRACTION = 0.8
PCA_VARIANCE_THRESHOLD = 0.80
LONG_PROBABILITY_THRESHOLD = 0.6
INITIAL_CAPITAL = 100_000
ROLLING_WINDOW_DAYS = 20

# Options: logistic_regression, random_forest, gradient_boosting, svm, mlp
ML_MODEL_NAME = "random_forest"

CHARTS_DIRECTORY = "hw3/charts"
LOGS_DIRECTORY = "hw3/logs"
