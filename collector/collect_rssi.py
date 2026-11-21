import csv
import time
from datetime import datetime
from pathlib import Path


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
                "receiver_id", "source_type", "beacon_id", "rssi"
            ])

        for idx in range(1, samples_per_point + 1):
            readings = scan_fn()
            ts = datetime.now().isoformat(timespec="milliseconds")
            for r in readings:
                writer.writerow([
                    ts, session_id, method_mode,
                    grid_row, grid_col, idx,
                    r["receiver_id"], r["source_type"], r["beacon_id"], r["rssi"]
                ])
            time.sleep(0.05)


if __name__ == "__main__":
    def dummy_scanner():
        return [
            {"receiver_id": "RX_1", "source_type": "target", "beacon_id": "TGT_01", "rssi": -65},
            {"receiver_id": "RX_1", "source_type": "dummy", "beacon_id": "DUM_01", "rssi": -62},
        ]

    sid = datetime.now().strftime("exp_%Y%m%d_%H%M%S")
    for r in range(1, 4):
        for c in range(1, 4):
            input(f"グリッド ({r}, {c}) の中心にターゲットを設置したらEnterを押してください...")
            collect_grid_samples(sid, "hybrid_ml", r, c, dummy_scanner, samples_per_point=200)