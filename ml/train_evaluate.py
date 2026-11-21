import sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

sys.path.append(str(Path(__file__).resolve().parents[1]))
from ml.preprocess import build_feature_matrix, load_or_create_data


def get_models(random_state: int = 42):
    return {
        "DecisionTree": DecisionTreeClassifier(random_state=random_state),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=random_state),
        "GaussianNB": GaussianNB(),
        "SVM_RBF": make_pipeline(StandardScaler(), SVC(kernel="rbf", random_state=random_state)),
    }


def evaluate_cv(X: np.ndarray, y: np.ndarray, random_state: int = 42):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    models = get_models(random_state)
    summary = {}
    grid_accuracies = {}

    labels = sorted(np.unique(y))

    for name, clf in models.items():
        y_true_all, y_pred_all = [], []
        for train_idx, test_idx in skf.split(X, y):
            clf.fit(X[train_idx], y[train_idx])
            preds = clf.predict(X[test_idx])
            y_true_all.extend(y[test_idx])
            y_pred_all.extend(preds)

        y_true_arr = np.array(y_true_all)
        y_pred_arr = np.array(y_pred_all)
        summary[name] = float(accuracy_score(y_true_arr, y_pred_arr)) * 100.0

        per_grid = {}
        for lbl in labels:
            mask = y_true_arr == lbl
            per_grid[lbl] = float(accuracy_score(y_true_arr[mask], y_pred_arr[mask])) * 100.0
        grid_accuracies[name] = per_grid

    return summary, grid_accuracies


if __name__ == "__main__":
    df = load_or_create_data()
    for mode in ["fp_ml", "hybrid_ml"]:
        X, y, cols = build_feature_matrix(df, mode=mode)
        summary, _ = evaluate_cv(X, y)
        print(f"=== {mode} (features={len(cols)}) ===")
        for model_name, acc in summary.items():
            print(f"  {model_name:<15}: {acc:.2f}%")