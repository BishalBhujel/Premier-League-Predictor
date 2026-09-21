from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV


def tune_logistic_regression(X_train, y_train):

    model = LogisticRegression(
        max_iter=1000
    )

    param_grid = {
        "C": [0.01, 0.1, 1, 10, 100],
        "solver": ["lbfgs", "liblinear"],
        "class_weight": [None, "balanced"]
    }

    search = RandomizedSearchCV(
        estimator=model,
        param_distributions=param_grid,
        n_iter=10,
        cv=5,
        scoring="f1_weighted",
        random_state=42,
        n_jobs=-1
    )

    search.fit(X_train, y_train)

    return search