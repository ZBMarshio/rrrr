# SIM-09：提示与参考答案

[返回题目](../讲义/SIM-09_域随机化与迁移.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

质量/尺寸可来自测量与机构资料，惯量需要相应模型/辨识；阻尼可用受控动态数据估计；延迟应记录命令/状态时间；观测噪声需在明确静态/动态条件下统计。猜测范围标为假设，不写成实测。

<a id="ex2"></a>

## 第 2 题

复用第四章 pid_step。只在控制 tick 重新算力矩，延迟队列长度以控制 tick 计；每次 trial 新建队列、积分和初态。

用新 XML 副本缩放本题转子的质量和惯量：

```python
import xml.etree.ElementTree as ET

def scaled_rotor_xml(xml_text, density_scale):
    if not np.isfinite(density_scale) or density_scale <= 0:
        raise ValueError("positive finite density scale required")
    root = ET.fromstring(xml_text)
    inertial = root.find("./worldbody/body[@name='rotor']/inertial")
    if inertial is None:
        raise ValueError("expected teaching rotor inertial element")
    inertia = np.asarray([float(v) for v in inertial.get("diaginertia").split()])
    inertial.set("mass", str(float(inertial.get("mass"))*density_scale))
    inertial.set("diaginertia", " ".join(str(v) for v in inertia*density_scale))
    return ET.tostring(root, encoding="unicode")
```

本函数针对指定基线 XML；更一般模型的参数更新需按结构与引擎规则处理。参考图同时给出误差与尾部判据，不能只挑一个好看的数。

<a id="ex3"></a>

## 第 3 题

```python
def sample_domain(rng, density_range=(0.8, 1.2), delay_tick_range=(0, 10)):
    lohi = np.asarray(density_range, dtype=float)
    if not isinstance(rng, np.random.Generator):
        raise ValueError("local numpy Generator required")
    if lohi.shape != (2,) or not np.isfinite(lohi).all() or lohi[0] <= 0 or lohi[0] > lohi[1]:
        raise ValueError("ordered positive density bounds required")
    if len(delay_tick_range) != 2 or any(not isinstance(v, int) or v < 0 for v in delay_tick_range):
        raise ValueError("two nonnegative integer delay bounds required")
    low, high = delay_tick_range
    if low > high:
        raise ValueError("ordered delay bounds required")
    return {"density_scale": float(rng.uniform(*lohi)),
            "delay_ticks": int(rng.integers(low, high+1))}
```

保存返回值和模型/控制配置。新 seed 和 resetData 都不自动恢复已经改过的 model 参数；把模型状态与采样器/控制器状态分开处理。

<a id="ex4"></a>

## 第 4 题

固定控制器的九格对照仅说明指定模型/延迟下的敏感性。训练方法比较还需要对应训练组、相同预算和冻结的独立测试；真机迁移需要真实平台的独立任务与误差评测。

