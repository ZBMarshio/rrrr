# EXP-02：提示与参考答案

[返回题目](../讲义/EXP-02_指标基线与消融.md) · [复盘](../练习与复盘记录.md)

<a id="ex1"></a>

## 第1题

平均有符号误差2 mm，MAE=4 mm，RMSE=√18≈4.24264 mm，最大6 mm。有符号平均存在抵消；MSE=18 mm²。

```python
import numpy as np

def scalar_error_metrics(predicted, reference):
    p,y = [np.asarray(x,dtype=np.float64) for x in (predicted,reference)]
    if p.ndim != 1 or p.shape != y.shape or p.size == 0:
        raise ValueError("paired nonempty scalar observations required")
    if not np.isfinite(p).all() or not np.isfinite(y).all():
        raise ValueError("finite complete observations required")
    error = p-y
    return {"count": int(p.size), "mean_signed": float(error.mean()),
            "mae": float(np.abs(error).mean()), "mse": float(np.mean(error**2)),
            "rmse": float(np.sqrt(np.mean(error**2))),
            "max_abs": float(np.max(np.abs(error)))}
```

函数不知道单位，输入米则误差长度量为米、mse 为 m²。位置向量、角度绕回和序列 mask 应使用相应指标，不能直接套标量定义。

<a id="ex2"></a>

## 第2题

成功2/4=50%，有效误差3条，失败分别记录 timeout/input_rejected。按3条有效误差算误差摘要可以，但成功率分母仍为全部4次已尝试任务。尚未运行的预定 ID 另外标记完成数，不冒充已测失败或成功。

<a id="ex3"></a>

## 第3题

零校正 `x_hat=r`；偏置校正 `b0=mean(r_train-x_train)`，`x_hat=r-b0`；完整校正由 fit_affine 拟合 a/b，再用 `(r-b)/a`。a 无量纲、b 为米；只有读取数据和拟合时的定义一致，反解才有意义。

参考 CSV 是已知仿射模型产生的数据，完整模型预期较合适；真实传感器可能有非线性、温漂与参考误差，需要更多独立实验。作者的比较值见[核对记录](../示例核对记录.md)，自己的实现仍须核对。

<a id="ex4"></a>

## 第4题

只能说 B 整套配置在本次条件下更好，不能把改善全部归于结构。先固定数据、划分、预处理、更新数和选模规则，比 A/B；再报告参数量、计算量、墙钟时间与调参预算。更新数一致仍不等于计算成本一致；根据问题也可另做相同时间预算比较。
