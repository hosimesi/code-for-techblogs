import pickle

import pandas as pd
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def main():

    iris = load_iris()

    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["target"] = iris.target

    # データの分割
    X_train_valid, X_test, y_train_valid, y_test = train_test_split(df.drop(["target"], axis=1), df["target"], test_size=0.1, random_state=42)
    X_train, X_valid, y_train, y_valid = train_test_split(X_train_valid, y_train_valid, test_size=0.25, random_state=42)

    # モデルの学習
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)

    # モデルの評価
    print("Train score: ", model.score(X_train, y_train))
    print("Valid score: ", model.score(X_valid, y_valid))
    print("Test score: ", model.score(X_test, y_test))

    # モデルの保存
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

if __name__ == '__main__':
    main()
