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

print(resolve_paths("/home/m/桌面/rrrr/学习记录/练习/W1_code/trajectory_lab/config.json"))

# 输出为(PosixPath('/home/m/桌面/rrrr/学习记录/练习/W1_code/trajectory_lab/data/trajectory.csv'), 
# PosixPath('/home/m/桌面/rrrr/学习记录/练习/W1_code/trajectory_lab/runs/baseline'))

