import csv
import math
from pathlib import Path

FIELDS = (
    "t_s", "q_ref_1_rad", "q_ref_2_rad",
    "q_obs_1_rad", "q_obs_2_rad",
)

def load_csv(path):
    times, ref, obs = [], [], []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError("CSV is missing required columns")
        for row in reader:
            line = reader.line_num
            try:
                values = [float(row[name]) for name in FIELDS]
            except (TypeError, ValueError) as exc:
                raise ValueError(f"line {line}: invalid numeric field") from exc
            if not all(math.isfinite(v) for v in values):
                raise ValueError(f"line {line}: non-finite numeric field")
            time = values[0]
            if time < 0 or (times and time <= times[-1]):
                raise ValueError(f"line {line}: invalid time order")
            times.append(time)
            ref.append(values[1:3])
            obs.append(values[3:5])
    if len(times) < 2:
        raise ValueError("at least two samples required")
    return times, ref, obs

if __name__ == "__main__":
    csv_path = Path(__file__).resolve().parent / "trajectory_lab" / "data" / "trajectory.csv"
    times, ref, obs = load_csv(csv_path)
    print("times:\n", times)
    print("ref:\n", ref)
    print("obs:\n", obs)
