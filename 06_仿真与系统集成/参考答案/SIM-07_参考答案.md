# SIM-07：提示与参考答案

[返回题目](../讲义/SIM-07_复位种子与重复评测.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

复用 reset_hinge_state；外部 integral、deque、计数和旧目标由自己的控制器清空/重建。球模型的 freejoint 使用其原生默认复位，不套标量关节函数。

mj_resetData 改 data，不恢复 model 参数；模型重建或显式恢复基线参数是另一层操作。

<a id="ex2"></a>

## 第 2 题

一个局部案例生成器，不代替完整项目的数据文件：

```python
def make_trial_bank(seed, count=10):
    if not isinstance(seed, int) or seed < 0 or not isinstance(count, int) or count < 1:
        raise ValueError("nonnegative integer seed and positive case count required")
    rng = np.random.default_rng(seed)
    return [{"trial_id": f"case_{i:03d}", "q0_rad": float(rng.uniform(-0.05, 0.05)),
             "goal_rad": float(rng.uniform(0.3, 0.7))} for i in range(count)]
```

换种子不保证采样集合在所有物理维度都充分不同；正式评测还要设计覆盖范围。保存实际案例，跨版本时优先复用保存值。

<a id="ex3"></a>

## 第 3 题

```python
import hashlib
import json

def config_digest(config):
    payload = json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

键顺序不应改变摘要，参数变化应改变。NumPy/Path 等先按明确 schema 转为 JSON 类型；摘要不代替模型文件、版本与配置本身，也不证明输入正确。

<a id="ex4"></a>

## 第 4 题

成功率 2/4=0.5，有误差样本 3；以三次为分母会误报 2/3。一个汇总片段：

```python
from collections import Counter

def summarize_trials(trials):
    if not trials:
        raise ValueError("nonempty predefined trial results required")
    seen, errors, failures, successes = set(), [], Counter(), 0
    for row in trials:
        key = row.get("trial_id")
        if not isinstance(key, str) or not key or key in seen:
            raise ValueError("unique nonempty trial IDs required")
        seen.add(key)
        if not isinstance(row.get("success"), bool):
            raise ValueError("explicit boolean success required")
        reason = row.get("reason")
        if not isinstance(reason, str) or not reason:
            raise ValueError("explicit result reason required")
        successes += int(row["success"])
        if not row["success"]:
            failures[reason] += 1
        value = row.get("final_error_rad")
        if value is not None:
            value = float(value)
            if not np.isfinite(value) or value < 0:
                raise ValueError("finite nonnegative measured errors required")
            errors.append(value)
    return {"total": len(trials), "successes": successes, "success_rate": successes/len(trials),
            "error_count": len(errors), "mean_error_rad": float(np.mean(errors)) if errors else None,
            "failures_by_reason": dict(failures)}
```

该函数汇总输入结果，不负责发现“某个预定 ID 根本没有提交”；上层应与冻结的案例清单比对，明确未运行项和中断恢复规则。

