import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))
from ml.preprocess import build_feature_matrix, load_or_create_data
from ml.train_evaluate import evaluate_cv


def plot_accuracy_grid(grid_acc: dict[str, float], title: str, out_path: Path):
    mat = np.zeros((3, 3))
    for r in range(1, 4):
        for c in range(1, 4):
            mat[r - 1, c - 1] = grid_acc.get(f"{r}_{c}", 0.0)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(mat, cmap="Blues", vmin=0, vmax=100)

    for r in range(3):
        for c in range(3):
            ax.text(c, r, f"{mat[r, c]:.1f}%", ha="center", va="center", fontsize=14, fontweight="bold")

    ax.set_xticks([0, 1, 2], labels=["Col 1", "Col 2", "Col 3"])
    ax.set_yticks([0, 1, 2], labels=["Row 1", "Row 2", "Row 3"])
    ax.set_title(title)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_rssi_deviation_boxplot(df, out_path: Path):
    pivoted = df.pivot_table(
        index=["grid_row", "grid_col", "sample_idx", "receiver_id"],
        columns=["source_type", "beacon_id"],
        values="rssi",
        aggfunc="mean",
    )

    box_data = []
    labels = []
    for r in range(1, 4):
        for c in range(1, 4):
            dum_idx = (r - 1) * 3 + c
            dum_id = f"DUM_{dum_idx:02d}"
            sub = pivoted.loc[(r, c)]
            diff = np.abs(sub[("target", "TGT_01")] - sub[("dummy", dum_id)]).dropna().to_numpy()
            box_data.append(diff)
            labels.append(f"{r},{c}")

    overall_mean = float(np.mean(np.concatenate(box_data)))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.boxplot(box_data, tick_labels=labels)
    ax.axhline(overall_mean, color="red", linestyle="--", label=f"Overall Average: {overall_mean:.1f} dBm")
    ax.set_xlabel("Grid Location")
    ax.set_ylabel("RSSI Absolute Difference (dBm)")
    ax.set_title("RSSI Deviation between Target and Dummy Beacon at Same Location")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    df = load_or_create_data()
    X_hyb, y_hyb, _ = build_feature_matrix(df, mode="hybrid_ml")
    _, grid_accs = evaluate_cv(X_hyb, y_hyb)

    plot_accuracy_grid(
        grid_accs["RandomForest"],
        "Hybrid Method Accuracy Map (Random Forest)",
        Path("data/accuracy_map_hybrid_rf.png"),
    )
    plot_rssi_deviation_boxplot(df, Path("data/rssi_deviation_boxplot.png"))
    print("Saved plots to data/ directory.")