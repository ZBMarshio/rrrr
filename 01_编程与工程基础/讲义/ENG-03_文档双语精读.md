# ENG-03 配套：Python 文档双语精读（路径、CSV、画图）

[返回 ENG-03 讲义](ENG-03_文件配置日志与结果.md) · 为第 1、2、4 题准备的原文、译文与实例

> 用法：ENG-03 讲义“目标与资料”列了 pathlib、csv、输入输出教程、Logging HOWTO 和 Matplotlib 五份英文资料。这份文件把明天要用的四份里最相关的段落摘出来，配译文和可运行的实例。每节先遮住译文自己读一遍原文，再对照；节末“自查”不给答案。
>
> 引用约定：正文的 `[1]`—`[4]` 对应文末“出处”。原文只摘写题会用到的句子，完整上下文按链接回原文。文档版本 Python 3.12、Matplotlib stable，访问日期 2026-11-18。例子均在本机 `robot0` 环境跑过。

## 1. pathlib：路径是一个对象（对应第 1 题）

### 1.1 为什么不直接拼字符串

**原文**（[1] 概述）：

> The pathlib module offers classes representing filesystem paths with semantics appropriate for different operating systems.

**译文**：pathlib 提供用类表示文件系统路径的写法，让“目录、文件名、后缀、父子关系”成为对象上的操作，而不是字符串拼接。

**实例**：字符串拼接在 Windows 上要用反斜杠，还要自己处理末尾分隔符；`Path` 用 `/` 运算符。

```python
from pathlib import Path

root = Path("/tmp/trajectory_lab")
p1 = root / "data" / "trajectory.csv"   # 自动处理分隔符
p2 = Path("/tmp/trajectory_lab") / "data/trajectory.csv"
p1 == p2                                 # True
```

第 1 题里“配置中的相对路径相对 config.json 所在目录”，就是先拿到 `config_path.parent`，再 `/ config["input"]`。

### 1.2 cwd、resolve、parent

**原文**（[1] Basic use 与 API）：

> `Path.cwd()`：Return a new path object representing the current directory.

> `Path.resolve(strict=False)`：Make the path absolute, resolving any symlinks.

> `parent`：The logical parent of the path.

**译文**：

- `cwd()` 返回一个表示**当前工作目录**的路径对象；
- `resolve()` 把路径变成绝对路径，并解开符号链接；`strict=False` 表示路径不存在也不报错；
- `parent` 是路径的上一级目录。

**实例**：第 1 题的解析函数，与参考答案同一思路。

```python
import json
from pathlib import Path

def resolve_paths(config_path):
    config_path = Path(config_path).resolve()
    with config_path.open(encoding="utf-8") as f:
        config = json.load(f)
    root = config_path.parent
    input_path = (root / config["input"]).resolve()
    output_dir = (root / config["output_dir"]).resolve()
    return input_path, output_dir
```

在 `/tmp` 下执行 `resolve_paths("/tmp/trajectory_lab/config.json")`，得到：

```text
(PosixPath('/tmp/trajectory_lab/data/trajectory.csv'),
 PosixPath('/tmp/trajectory_lab/runs/baseline'))
```

再从 `/` 下传同一个配置绝对路径，结果完全相同——因为解析的基准是 `config_path.parent`，不是 `Path.cwd()`。

**自查**：如果配置里 `input` 写的是 `/data/trajectory.csv`（绝对路径），`root / config["input"]` 会得到什么？为什么？

（提示：右侧是绝对路径时，`/` 运算符会丢弃左边的部分；这既是坑，也是“允许显式绝对路径”的实现方式。）

### 1.3 mkdir 与 open

**原文**（[1] 方法说明）：

> `Path.mkdir(mode=0o777, parents=False, exist_ok=False)`

> If parents is true, any missing parents of this path are created as needed.

> If exist_ok is true, FileExistsError will not be raised unless the given path already exists and is not a directory.

**译文**：`mkdir()` 默认只建最后一级、目录已存在会报 `FileExistsError`；`parents=True` 会连缺失的上级一起建；`exist_ok=True` 表示目录已存在也不报错（但它仍不是文件）。

**实例**：画图前先保证输出目录存在。

```python
out_dir = Path("/tmp/trajectory_lab/runs/baseline")
out_dir.mkdir(parents=True, exist_ok=True)
```

`Path.open()` 的参数与内置 `open()` 相同，所以能直接写 `config_path.open(encoding="utf-8")`；第 2 题读 CSV 时还要加 `newline=""`。

## 2. csv：按字段名读表（对应第 2 题）

### 2.1 打开方式：newline="" 与 utf-8-sig

**原文**（[2] 模块说明）：

> If csvfile is a file object, it should be opened with `newline=''`.

**译文**：把文件对象交给 `csv.reader` / `csv.DictReader` 时，必须以 `newline=""` 打开；否则在 Windows 或带 BOM 的文件上，可能出现空行、行列错位或表头带不可见字符。

**实例**：

```python
with open(path, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
```

- `utf-8-sig` 会自动吃掉文件开头的 BOM；没有 BOM 时与 `utf-8` 等价；
- 不要用 `errors="ignore"` 把坏字节吞掉——坏数据应该报错，而不是悄悄变成另一个值。

### 2.2 DictReader：一行变成一个 dict

**原文**（[2] `csv.DictReader`）：

> Create an object that operates like a regular reader but maps the information in each row to a dict whose keys are given by the optional fieldnames parameter.

> If the fieldnames parameter is omitted, the values in the first row of the file will be used as the fieldnames.

**译文**：`DictReader` 像普通 reader 一样逐行读，但每一行变成 `dict`；键由 `fieldnames` 给出，省略时用文件第一行作表头。

**实例**：第 2 题的读入函数，返回 `t`、`q_ref`、`q_obs` 三份数据，并做四类检查。

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

在学习指南的四行样例上，转成数组后形状分别为 `(4,)`、`(4,2)`、`(4,2)`，RMSE 是 `[0.15811388, 0.2]`。

### 2.3 line_num：报错时指哪一行

**原文**（[2] `csv.reader.line_num`）：

> The number of lines read from the source iterator.

**译文**：`line_num` 是“从源迭代器读过的行数”，不是“当前数据行号”。表头也算一行，所以第一行数据的 `line_num` 是 2。

**实例**：第 2 题要求“坏数据报告行号”，靠的就是这个值。三种坏数据在参考实现里的行为：

```text
缺一列      → 表头检查失败：CSV is missing required columns
填一个 NaN  → 该数据行报错：line 3: non-finite numeric field
重复时间    → 第二次出现处报错：line 5: invalid time order
```

**自查**：如果 CSV 里有一行 `t_s` 是 `0.4`，但上一行是 `0.5`，会在哪一行报错？如果文件只有一行数据，报错文本是什么？

## 3. matplotlib：把数组画成图（对应第 4 题）

### 3.1 figure 与 axes

**原文**（[4] Pyplot tutorial）：

> matplotlib.pyplot is a collection of functions that make matplotlib work like MATLAB. Each pyplot function makes some change to a figure: e.g., creates a figure, creates a plotting area in a figure, plots some lines in a plotting area, decorates the plot with labels, etc.

**译文**：`pyplot` 是一组“像 MATLAB 那样”直接操作的函数：建图、建绘图区、画线、加标签。多子图时用 `subplots()` 一次拿到 figure 和 axes 数组，比反复 `plt.subplot()` 清楚。

**实例**：两行共享横轴——上面画参考/观测，下面画误差。

```python
import matplotlib
matplotlib.use("Agg")          # 无显示器也能保存图片
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
fig.savefig(out_dir / "curve.png")
plt.close(fig)
```

绘图顺序：先 `plot`，再 `set_*label` 与 `legend`，最后 `savefig`。`tight_layout()` 防止标签被裁掉。

### 3.2 单位、图例、误差定义

图能被别人读懂，靠三样东西：

1. 横轴写 `time [s]`，纵轴写 `joint 1 [rad]`——单位写在标签里；
2. 图例区分 `reference` 与 `synthetic observation`；
3. 误差面板的标题或纵轴写清 `error = obs - ref`，符号方向不能靠猜。

**实例**：第二关节把 `[:, 0]` 换成 `[:, 1]` 即可。四幅图（两关节 × 参考/误差）都可以放进同一个 `subplots(2, 2)`。

### 3.3 保存与复跑

**原文**（[4] 保存图片的写法）：

> `fig.savefig(fname)`

**译文**：把**当前这个 figure**（而不是“屏幕上显示的窗口”）保存到文件。

**实例**：保存后检查文件真的存在：

```python
out_dir.mkdir(parents=True, exist_ok=True)
fig.savefig(out_dir / "curve.png")
assert (out_dir / "curve.png").stat().st_size > 0
```

**自查**：用 `Agg` 后端时没有窗口弹出，这算失败吗？判断依据应该看什么？

（提示：验收看的是输出路径上有没有文件、文件能不能打开，不是有没有窗口。）

## 4. JSON 配置与摘要（第 1、3 题会碰）

### 4.1 读配置

**原文**（[3] JSON 一节）：

> The json module makes it easy to parse JSON strings and files containing JSON object.

> `json.load(fp)`：Deserialize fp to a Python object using this conversion table.

**译文**：`json.load()` 从文件对象读出 Python 对象；路径、样本数、单位这些配置就放这里，不要散落在脚本里。

**实例**：

```python
import json
from pathlib import Path

config_path = Path("config.json").resolve()
with config_path.open(encoding="utf-8") as f:
    config = json.load(f)

config["input"]        # "data/trajectory.csv"
config["output_dir"]   # "runs/baseline"
```

### 4.2 写摘要时 allow_nan=False

**原文**（[3] `json.dump` 参数说明）：

> If allow_nan is false, then it will be a ValueError to serialize out of range float values (nan, inf, -inf) in strict compliance of the JSON specification.

**译文**：JSON 标准里没有 `NaN`/`Infinity`；Python 默认允许写，但这样写出的文件别的工具读不了。设置 `allow_nan=False`，遇到非有限数直接报错，把问题挡在保存之前。

**实例**：

```python
summary = {
    "input": str(input_path),
    "n_samples": len(t),
    "time_unit": "s",
    "angle_unit": "rad",
    "rmse_per_joint_rad": rmse.tolist(),
}
with (out_dir / "summary.json").open("w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2, allow_nan=False)
```

**自查**：RMSE 里出现 `nan` 时，`allow_nan=False` 会在哪一步报错——计算时、`json.dump` 时，还是读取摘要的别的工具里？

## 5. 第 1、2、4 题与这份文件的对应

| 题目 | 先读 | 产出 |
|---|---|---|
| 第 1 题 路径解析 | §1.2、§4.1 | `resolve_paths()`，两个 cwd 打印结果一致 |
| 第 2 题 读五列 CSV | §2.1—§2.3 | `load_csv()` + 三种坏数据各报一次错 |
| 第 3 题 摘要与日志 | §4.2（先做摘要） | `summary.json`（日志留到 11-20） |
| 第 4 题 画图 | §3 | `curve.png` + 一条复跑命令 |

## 6. 明天（11-19）的路线

| 时段 | 做什么 | 参考 |
|---|---|---|
| 0—15min | 第 1 题：建 `config.json`，写 `resolve_paths()`，在两个目录各跑一次 | §1 |
| 15—50min | 第 2 题：`load_csv()` + 正常数据 + 三种坏数据 | §2 |
| 50—110min | 第 4 题：读回 CSV，画两关节参考/观测/误差图，存 `curve.png` | §3 |
| 110—120min | 换新终端用同一条命令复跑，确认输出一致 | §3.3、讲义“验收” |

第 3 题的日志部分可以放到 11-20，不在明天卡住。

## 7. 术语表

| 词 | 一句话 |
|---|---|
| cwd | 当前工作目录，相对路径的出发点 |
| resolve | 把路径变绝对、解符号链接 |
| parent | 上一级目录 |
| DictReader | 把每行读成以表头为键的 dict |
| line_num | reader 已读过的行数（含表头） |
| newline="" | 交给 csv 模块时的正确打开方式 |
| utf-8-sig | 自动跳过 BOM 的 UTF-8 |
| finite | 不是 NaN、也不是 ±inf |
| legend | 图例 |
| savefig | 保存当前 figure 到文件 |
| Agg | 无窗口的绘图后端，适合存图 |
| allow_nan=False | 让 JSON 拒绝 NaN/Infinity |

## 8. 出处

- [1] pathlib — https://docs.python.org/3.12/library/pathlib.html（访问日期 2026-11-18）
- [2] csv — https://docs.python.org/3.12/library/csv.html（访问日期 2026-11-18）
- [3] Python 输入输出教程 — https://docs.python.org/3.12/tutorial/inputoutput.html（访问日期 2026-11-18）
- [4] Matplotlib Pyplot tutorial — https://matplotlib.org/stable/tutorials/pyplot.html（访问日期 2026-11-18）
