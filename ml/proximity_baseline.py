import sys
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score

sys.path.append(str(Path(__file__).resolve().parents[1]))
from ml.preprocess import load_or_create_data


def evaluate_proximity_method(df):
    rxs = sorted(df["receiver_id"].unique())
    dummies = [f"DUM_{i:02d}" for i in range(1, 10)]
    grid_keys = [f"{r}_{c}" for r in range(1, 4) for c in range(1, 4)]

    pivoted = df.pivot_table(
        index=["grid_row", "grid_col", "sample_idx"],
        columns=["source_type", "beacon_id", "receiver_id"],
        values="rssi",
        aggfunc="mean",
    ).fillna(-100.0)

    y_true, y_pred = [], []
    for (r, c, _), row in pivoted.iterrows():
        target_vec = np.array([row[("target", "TGT_01", rx)] for rx in rxs], dtype=float)

        best_grid = None
        best_dist = float("inf")
        for idx, dum_id in enumerate(dummies):
            dum_vec = np.array([row[("dummy", dum_id, rx)] for rx in rxs], dtype=float)
            dist = float(np.linalg.norm(target_vec - dum_vec))
            if dist < best_dist:
                best_dist = dist
                best_grid = grid_keys[idx]

        y_true.append(f"{r}_{c}")
        y_pred.append(best_grid)

    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)
    overall_acc = float(accuracy_score(y_true_arr, y_pred_arr)) * 100.0

    per_grid = {}
    for g in grid_keys:
        mask = y_true_arr == g
        per_grid[g] = float(accuracy_score(y_true_arr[mask], y_pred_arr[mask])) * 100.0

    return overall_acc, per_grid


if __name__ == "__main__":
    df = load_or_create_data()
    overall, per_grid = evaluate_proximity_method(df)
    print(f"=== Proximity Baseline ===")
    print(f"  Overall Accuracy: {overall:.2f}%")
    for g, acc in per_grid.items():
        print(f"  Grid {g}: {acc:.2f}%")