import lightgbm as lgb


class LocalLGBM:
    def __init__(
        self,
        params: dict = {
            "objective": "binary",
            "num_leaves": 31,
            "learning_rate": 0.1,
            "max_depth": -1,
            "random_state": 42,
            "n_jobs": -1,
            "silent": True,
            "importance_type": "split",
        },
    ):
        self.params = params
        self.model = None

    def fit(self, X_train, y_train, X_valid=None, y_valid=None):
        if X_valid is not None and y_valid is not None:
            self.model._fit_with_valid(X_train, y_train, X_valid, y_valid)
        train_set = lgb.Dataset(X_train, label=y_train)
        self.model = lgb.train(self.params, train_set)

    def _fit_with_valid(self, X_train, y_train, X_valid, y_valid):
        # hyperparameter tuning
        best_score = 0
        best_params = {}
        for num_leaves in [10, 20, 30, 40, 50]:
            for max_depth in [3, 5, 7, 9, 11]:
                params = {
                    "num_leaves": num_leaves,
                    "max_depth": max_depth,
                    "objective": "binary",
                    "learning_rate": 0.1,
                    "random_state": 42,
                    "n_jobs": -1,
                    "silent": True,
                    "importance_type": "split",
                }
                model = lgb.train(params, lgb.Dataset(X_train, label=y_train))
                score = model.score(X_valid, y_valid)
                if score > best_score:
                    best_score = score
                    best_params = params
        self.model = lgb.train(best_params, lgb.Dataset(X_train, label=y_train))

    def predict(self, X):
        proba = self.model.predict(X)
        return [1 if p >= 0.5 else 0 for p in proba]

    def predict_proba(self, X):
        return self.model.predict(X)

    def save_model(self, model_file):
        self.model.save_model(model_file)

    def load_model(self, model_file):
        self.model = lgb.Booster(model_file=model_file)
