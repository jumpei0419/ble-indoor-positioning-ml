import numpy as np
from sklearn.naive_bayes import GaussianNB


def main():
    # 動作確認用のダミーデータ（受信機2台分のRSSIを想定）
    X_train = np.array([[-60, -75], [-62, -74], [-80, -55], [-79, -57]])
    y_train = np.array(["Grid_1_1", "Grid_1_1", "Grid_1_2", "Grid_1_2"])

    model = GaussianNB()import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


def build_feature_matrix(df: pd.DataFrame, mode: str = "fp_ml"):
    df = df.copy()
    df["label"] = df["grid_row"].astype(str) + "_" + df["grid_col"].astype(str)
    df["feat_name"] = df["source_type"] + "_" + df["beacon_id"] + "_" + df["receiver_id"]

    pivoted = df.pivot_table(
        index=["label", "grid_row", "grid_col", "sample_idx"],
        columns="feat_name",
        values="rssi",
        aggfunc="mean",
    )

    if mode == "fp_ml":
        cols = [c for c in pivoted.columns if c.startswith("target_")]
    elif mode == "hybrid_ml":
        cols = [c for c in pivoted.columns if c.startswith("target_") or c.startswith("dummy_")]
    else:
        raise ValueError(f"Unknown mode: {mode}")

    X = pivoted[cols].fillna(-100.0).to_numpy(dtype=float)
    y = pivoted.index.get_level_values("label").to_numpy()
    return X, y, cols


def evaluate_models(X: np.ndarray, y: np.ndarray, random_state: int = 42):
    models = {
        "DecisionTree": DecisionTreeClassifier(random_state=random_state),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=random_state),
        "GaussianNB": GaussianNB(),
        "SVM_RBF": make_pipeline(StandardScaler(), SVC(kernel="rbf", random_state=random_state)),
    }

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    results = {}

    for name, clf in models.items():
        scores = []
        for train_idx, test_idx in skf.split(X, y):
            clf.fit(X[train_idx], y[train_idx])
            preds = clf.predict(X[test_idx])
            scores.append(accuracy_score(y[test_idx], preds))
        results[name] = float(np.mean(scores)) * 100.0

    return results


def proximity_predict_grid(target_rssi_vec: np.ndarray, dummy_grid_rssi_map: dict[str, np.ndarray]) -> str:
    best_grid = None
    best_dist = float("inf")
    for grid_key, ref_vec in dummy_grid_rssi_map.items():
        dist = float(np.linalg.norm(target_rssi_vec - ref_vec))
        if dist < best_dist:
            best_dist = dist
            best_grid = grid_key
    return best_grid


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    rows = []
    grids = [(r, c) for r in range(1, 4) for c in range(1, 4)]
    rxs = ["RX_1", "RX_2", "RX_3", "RX_4"]
    dummies = [f"DUM_{i:02d}" for i in range(1, 10)]

    for r, c in grids:
        base_shift = (r * 3 + c) * -1.5
        for idx in range(1, 201):
            for rx_i, rx in enumerate(rxs):
                rows.append({
                    "grid_row": r, "grid_col": c, "sample_idx": idx,
                    "receiver_id": rx, "source_type": "target", "beacon_id": "TGT_01",
                    "rssi": -60 + base_shift + rx_i * 2 + rng.normal(0, 2.0)
                })
            for d_i, dum in enumerate(dummies):
                rows.append({
                    "grid_row": r, "grid_col": c, "sample_idx": idx,
                    "receiver_id": rxs[d_i % len(rxs)], "source_type": "dummy", "beacon_id": dum,
                    "rssi": -65 - (d_i % 5) * 2 + rng.normal(0, 3.0)
                })

    df_sim = pd.DataFrame(rows)
    for mode in ["fp_ml", "hybrid_ml"]:
        X, y, cols = build_feature_matrix(df_sim, mode=mode)
        res = evaluate_models(X, y)
        print(f"=== {mode} (features={len(cols)}) ===")
        for k, v in res.items():
            print(f"  {k}: {v:.2f}%")
    model.fit(X_train, y_train)

    pred = model.predict([[-61, -76]])
    print("推定位置:", pred[0])


if __name__ == "__main__":
    main()