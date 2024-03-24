import pickle

from sklearn.linear_model import LogisticRegression


class LocalLogisticRegression:
    def __init__(self, params=None):
        self.params = params if params is not None else {}
        self.model = LogisticRegression(**self.params)

    def fit(self, X_train, y_train, X_valid=None, y_valid=None):
        if X_valid is not None and y_valid is not None:
            self.model._fit_with_valid(X_train, y_train, X_valid, y_valid)
        self.model.fit(X_train, y_train)

    def _fit_with_valid(self, X_train, y_train, X_valid, y_valid):
        # hyperparameter tuning
        best_score = 0
        best_params = {}
        for C in [0.001, 0.01, 0.1, 1, 10, 100]:
            model = LogisticRegression(C=C)
            model.fit(X_train, y_train)
            score = model.score(X_valid, y_valid)
            if score > best_score:
                best_score = score
                best_params = {"C": C}
        self.model = LogisticRegression(**best_params)

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)[:, 1]

    def save_model(self, model_file):
        with open(model_file, "wb") as f:
            pickle.dump(self.model, f)

    def load_model(self, model_file):
        with open(model_file, "rb") as f:
            self.model = pickle.load(f)
