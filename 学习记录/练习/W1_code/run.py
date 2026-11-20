"""W01 交付物：CSV → RMSE → 曲线图 → summary.json 的可复跑管道。

用法：
    python run.py                      # 用 trajectory_lab/config.json
    python run.py other/config.json    # 换一份配置（例如故意写坏，看失败在哪一步）
"""
import json
import logging
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from eng02_2_rmse import rmse_per_joint
from eng03_1_paths import resolve_paths
from eng03_2_csv import load_csv

HERE = Path(__file__).resolve().parent
log = logging.getLogger("run")  # 创建日志记录器


def git_version() -> str:
    """当前提交号；不在 git 仓库里时返回 unknown。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=HERE, capture_output=True, text=True, check=True,
        )   # 启动一个外部终端来执行函数内的内容并把输出内容返回
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def draw(t, ref, obs, out_path):
    """上排参考 vs 观测，下排误差 q_obs - q_ref，左关节 1 右关节 2。"""
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), sharex=True)
    for j, name in enumerate(("joint 1", "joint 2")):
        ax = axes[0, j]
        ax.plot(t, ref[:, j], label="reference q_ref")
        ax.plot(t, obs[:, j], "--", label="observed q_obs")
        ax.set_title(name)
        ax.set_ylabel("angle [rad]")
        ax.legend(loc="best")
        ax.grid(alpha=0.3)

        ax = axes[1, j]
        ax.plot(t, obs[:, j] - ref[:, j], color="tab:red", label="q_obs - q_ref")
        ax.set_xlabel("time [s]")
        ax.set_ylabel("error [rad]")
        ax.legend(loc="best")
        ax.grid(alpha=0.3)
    fig.suptitle("Joint trajectory: reference vs observed")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def run(config_path: Path) -> int:  # config_path: Path规定了输入数据的格式， -> int表明了预期返回参数
    stage = "config"
    try:
        with Path(config_path).open(encoding="utf-8") as f:
            cfg = json.load(f)
        angle_unit = cfg.get("angle_unit", "rad")
        log.info("stage=%s config=%s", stage, config_path)

        stage = "resolve"
        input_path, out_dir = resolve_paths(config_path)
        log.info("stage=%s input=%s out=%s", stage, input_path, out_dir)

        stage = "load"
        times, ref, obs = load_csv(input_path)
        log.info("stage=%s n=%d", stage, len(times))

        stage = "compute"
        t = np.asarray(times, dtype=np.float64)
        ref = np.asarray(ref, dtype=np.float64)
        obs = np.asarray(obs, dtype=np.float64)
        rmse = rmse_per_joint(ref, obs)
        log.info("stage=%s rmse_per_joint=%s", stage, rmse.tolist())

        stage = "write"
        out_dir.mkdir(parents=True, exist_ok=True)
        curve_path = out_dir / "curve.png"
        summary_path = out_dir / "summary.json"
        draw(t, ref, obs, curve_path)

        summary = {
            "data_source": "synthetic",
            "input": str(input_path),
            "n_samples": len(times),
            "time_unit": "s",
            "angle_unit": angle_unit,
            "error_definition": "q_obs - q_ref",
            "rmse_per_joint_rad": rmse.tolist(),
            "config": str(Path(config_path).resolve()),
            "code_version": git_version(),
            "outputs": [curve_path.name, summary_path.name],
        }
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False)
            + "\n", encoding="utf-8",
        )
        log.info("stage=%s wrote %s and %s", stage, curve_path, summary_path)
        return 0
    except (FileNotFoundError, KeyError, ValueError) as exc:
        log.error("stage=%s failed: %s", stage, exc)
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,                     # 日志等级，只记录正常信息
                        format="%(levelname)s %(message)s")     # 日志格式
    cfg = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "trajectory_lab" / "config.json"
    sys.exit(run(cfg))
