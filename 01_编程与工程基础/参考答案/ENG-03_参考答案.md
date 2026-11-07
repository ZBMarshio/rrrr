# ENG-03：提示与参考答案

[返回题目](../讲义/ENG-03_文件配置日志与结果.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

输入为 `/tmp/trajectory_lab/data/trajectory.csv`，输出目录为 `/tmp/trajectory_lab/runs/baseline`。一种路径解析写法：

```python
import json
from pathlib import Path

def resolve_paths(config_path):
    config_path = Path(config_path).resolve()
    with config_path.open(encoding="utf-8") as f:
        config = json.load(f)
    if config["angle_unit"] != "rad":
        raise ValueError("this exercise expects radians")
    root = config_path.parent
    input_path = (root / config["input"]).resolve()
    output_dir = (root / config["output_dir"]).resolve()
    return input_path, output_dir
```

Path 与绝对路径拼接时，绝对的右侧路径会决定结果；本题也允许显式绝对路径。验证时打印 resolve 后的结果，并在两个不同当前目录中传同一个配置绝对路径。缺少配置键的友好提示可再补，不要把 KeyError 伪装成成功。

<a id="ex2"></a>

## 第 2 题

提示：表头检查一次；逐行转换时带上行号；先验证再累积。

```python
import csv
import math

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
```

这是声明的五列格式的参考实现，允许额外命名列；格式复杂时还可检查重复表头与多余字段，勿直接声称已经处理任意 CSV。按字段名取数意味着交换列顺序仍应正确。

在学习指南样例上，转数组后形状应为 `(4,)`、`(4,2)`、`(4,2)`，RMSE 对照 ENG-02。失败样例的期望分别为：缺字段在表头处拒绝；NaN 在所属数据行拒绝；重复时间在第二次出现处拒绝。

<a id="ex3"></a>

## 第 3 题

一种摘要结构如下，路径和版本字段应由实际运行填写，不要原样当成实验事实：

```json
{
  "data_source": "synthetic",
  "input": "实际解析后的输入路径",
  "n_samples": 4,
  "time_unit": "s",
  "angle_unit": "rad",
  "error_definition": "q_obs - q_ref",
  "rmse_per_joint_rad": [0.158113883, 0.2],
  "config": "实际参数或配置副本",
  "code_version": "实际提交号；未提交修改另注明"
}
```

日志可以是“读取哪个文件”“通过验证：4 行/2 关节”“结果写入哪里”。入口捕获预期输入异常时可补日志后 `raise SystemExit(1)`；保留开发阶段 traceback 有助定位。未预期的异常不要一律吞掉。

图中优先放物理量、单位、图例；摘要保存指标与来源；日志记录运行过程。保存 JSON 时 `json.dump(..., allow_nan=False)` 能拒绝非标准的非有限数表示。

<a id="ex4"></a>

## 第 4 题

你已经有 t、ref、obs 浮点数组后，单个关节的绘图片段可以是：

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 1, sharex=True)
axes[0].plot(t, ref[:, 0], label="reference")
axes[0].plot(t, obs[:, 0], label="synthetic observation")
axes[0].set_ylabel("joint 1 [rad]")
axes[0].legend()
axes[1].plot(t, obs[:, 0] - ref[:, 0], label="obs - ref")
axes[1].set_xlabel("time [s]")
axes[1].set_ylabel("error [rad]")
axes[1].legend()
fig.tight_layout()
fig.savefig(output_path)
plt.close(fig)
```

这是计算后的局部片段，需要你先提供数组和 output_path，并创建输出父目录。第二关节由你扩展；不用为了漂亮的页面先做交互界面。

验收重点：读回的数值与原数据一致；图来自读回的数据；单位、符号和图例准确；命令说明当前目录/配置位置；修改偏差后图和 RMSE 同时更新。展示窗口未出现不等于保存失败，先检查输出路径和文件。

