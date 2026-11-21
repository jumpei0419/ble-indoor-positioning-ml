import csv
import time
from datetime import datetime
from pathlib import Path
import numpy as np


def collect_grid_samples(
    session_id: str,
    method_mode: str,
    grid_row: int,
    grid_col: int,
    scan_fn,
    samples_per_point: int = 200,
    out_csv: Path = Path("data/rssi_log.csv"),
):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    write_header = not out_csv.exists()

    with out_csv.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "timestamp", "session_id", "method_mode",
                "grid_row", "grid_col", "sample_idx",
                "receiver_id", "source_type", "beacon_id", "rssi",
            ])

        for idx in range(1, samples_per_point + 1):
            readings = scan_fn(grid_row, grid_col)
            ts = datetime.now().isoformat(timespec="milliseconds")
            for r in readings:
                writer.writerow([
                    ts, session_id, method_mode,
                    grid_row, grid_col, idx,
                    r["receiver_id"], r["source_type"], r["beacon_id"], r["rssi"],
                ])
            time.sleep(0.01)


def generate_synthetic_dataset(out_csv: Path = Path("data/rssi_log.csv"), seed: int = 42):
    if out_csv.exists():
        out_csv.unlink()

    rng = np.random.default_rng(seed)
    rxs = ["RX_1", "RX_2", "RX_3", "RX_4"]
    rx_coords = {"RX_1": (0.5, 0.5), "RX_2": (0.5, 3.5), "RX_3": (3.5, 0.5), "RX_4": (3.5, 3.5)}
    dummies = {f"DUM_{i:02d}": ((i - 1) // 3 + 1, (i - 1) % 3 + 1) for i in range(1, 10)}
    dummy_offsets = {f"DUM_{i:02d}": float(rng.uniform(-12.0, -7.0)) for i in range(1, 10)}

    def simulated_scanner(grid_row: int, grid_col: int):
        readings = []
        for rx in rxs:
            rr, rc = rx_coords[rx]
            dist = np.hypot(grid_row - rr, grid_col - rc)
            rssi = int(round(-52.0 - 12.0 * np.log10(dist + 0.5) + rng.normal(0, 2.0)))
            readings.append({
                "receiver_id": rx, "source_type": "target", "beacon_id": "TGT_01", "rssi": rssi
            })
        shielded = (grid_row, grid_col)
        for dum_id, (dr, dc) in dummies.items():
            shield_drop = -6.0 if (dr, dc) == shielded else 0.0
            for rx in rxs:
                rr, rc = rx_coords[rx]
                dist = np.hypot(dr - rr, dc - rc)
                rssi = int(round(
                    -52.0 - 12.0 * np.log10(dist + 0.5)
                    + dummy_offsets[dum_id] + shield_drop + rng.normal(0, 2.0)
                ))
                readings.append({
                    "receiver_id": rx, "source_type": "dummy", "beacon_id": dum_id, "rssi": rssi
                })
        return readings

    sid = datetime.now().strftime("sim_%Y%m%d_%H%M%S")
    for r in range(1, 4):
        for c in range(1, 4):
            collect_grid_samples(sid, "hybrid_ml", r, c, simulated_scanner, samples_per_point=200, out_csv=out_csv)
    print(f"Generated synthetic dataset at {out_csv}")


if __name__ == "__main__":
    generate_synthetic_dataset()