# MATH-03：提示与参考答案

[返回题目](../讲义/MATH-03_概率统计与不确定性.md) · [复盘](../练习与复盘记录.md)

<a id="ex1"></a>

## 第1题

均值0，MAE=RMSE=总体标准差=3 mm；总体方差9 mm²，样本方差18 mm²，样本标准差√18≈4.24264 mm。正负误差抵消，平方/绝对值不会抵消。

```python
import numpy as np

def descriptive_stats(values):
    x = np.asarray(values, dtype=np.float64)
    if x.ndim != 1 or x.size < 2 or not np.isfinite(x).all():
        raise ValueError("at least two finite observations required")
    return {"count": int(x.size), "mean": float(x.mean()),
            "std_population": float(x.std(ddof=0)),
            "std_sample": float(x.std(ddof=1))}
```

函数不推断单位、独立性或置信区间，输入来自什么试验由上层说明。

<a id="ex2"></a>

## 第2题

均值0.7，样本标准差0.1。可以报告三个 seed 各自结果与“0.7±0.1，样本标准差”；不能把它写成置信区间。60次任务嵌套在3个已训练模型下，共享模型参数；训练随机性的独立重复仍只有3组。

<a id="ex3"></a>

## 第3题

等长且指标为线性平均时，两种平均可一致；不同长度时，按帧平均让长回合权重更大。成功率若按回合定义，更不能用帧误差的平均代替。重复一个场景主要检查该条件重复性，未测场景应另留分组。

<a id="ex4"></a>

## 第4题

召回=90/100=90%；检测阳性180张，其中真正有目标的比例90/180=50%。分母分别是“所有真实目标”和“所有阳性检测”。它们也不直接等于机器人闭环任务成功率。
