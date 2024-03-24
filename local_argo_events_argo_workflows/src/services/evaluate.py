from sklearn.metrics import accuracy_score, log_loss, precision_score, recall_score, roc_auc_score


def evaluate_model(y_pred, y_proba, y):
    logloss = log_loss(y, y_proba)
    accuracy = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred)
    recall = recall_score(y, y_pred)
    auc = roc_auc_score(y, y_proba)
    return logloss, accuracy, precision, recall, auc
