from pathlib import Path
import numpy as np
import pandas as pd


def load_or_create_data(csv_path: Path = Path("data/rssi_log.csv")) -> pd.DataFrame:
    if not csv_path.exists():
        from collector.collect_rssi import generate_synthetic_dataset
        generate_synthetic_dataset(csv_path)
    return pd.read_csv(csv_path)


def build_feature_matrix(df: pd.DataFrame, mode: str = "fp_ml"):
    """
    mode='fp_ml'    : ターゲット端末のRSSI特徴量のみ（単体手法）
    mode='hybrid_ml': ターゲットRSSI + ダミービーコンRSSI（ハイブリッド手法）
    """
    work = df.copy()
    work["label"] = work["grid_row"].astype(str) + "_" + work["grid_col"].astype(str)
    work["feat_name"] = work["source_type"] + "_" + work["beacon_id"] + "_" + work["receiver_id"]

    pivoted = work.pivot_table(
        index=["label", "grid_row", "grid_col", "sample_idx"],
        columns="feat_name",
        values="rssi",
        aggfunc="mean",
    )

    if mode == "fp_ml":
        cols = sorted([c for c in pivoted.columns if c.startswith("target_")])
    elif mode == "hybrid_ml":
        cols = sorted([c for c in pivoted.columns if c.startswith("target_") or c.startswith("dummy_")])
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    X = pivoted[cols].fillna(-100.0).to_numpy(dtype=float)
    y = pivoted.index.get_level_values("label").to_numpy()
    return X, y, cols