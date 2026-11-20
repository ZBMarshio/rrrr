import json
from pathlib import Path

def resolve_paths(config_path):
    config_path = Path(config_path)
    with config_path.open(encoding= "utf-8") as f:
        config = json.load(f)
    root = config_path.parent
    input_path = (root / config["input"]).resolve()
    output_dir = (root / config["output_dir"]).resolve()
    return input_path, output_dir

if __name__ == "__main__":
    config = Path(__file__).resolve().parent / "trajectory_lab" / "config.json"
    print(resolve_paths(config))

