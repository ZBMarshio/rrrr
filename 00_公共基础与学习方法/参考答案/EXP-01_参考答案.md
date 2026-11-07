# EXP-01：提示与参考答案

[返回题目](../讲义/EXP-01_数据划分与泄漏.md) · [复盘](../练习与复盘记录.md)

<a id="ex1"></a>

## 第1题

未见物体问题需要隔离物体身份；同物体不同回合仍共享外形/材质。测试同物体的新回合可以按 episode 分，但要说明场景、采集日、操作人是否共享。划分越严格不等于越适合当前问题，先写目标再选分组。

<a id="ex2"></a>

## 第2题

train 均值2、总体标准差1，标准化后 train=[-1,1]，val=[99,101]。val 单独算均值102、尺度1后也变成[-1,1]，偏移被处理掉了。

```python
import numpy as np

def fit_train_scaling(x_train):
    x = np.asarray(x_train,dtype=np.float64)
    if x.ndim != 2 or len(x) < 2 or x.shape[1] == 0 or not np.isfinite(x).all():
        raise ValueError("finite training matrix required")
    mean, scale = x.mean(axis=0), x.std(axis=0,ddof=0)
    if np.any(scale == 0):
        raise ValueError("constant feature: choose and record a handling rule")
    return mean, scale
```

这个入门接口对常量特征报错，让你明确选择删除、固定尺度或其他规则；第七章的 clamp_min 是另一种显式约定。实际评测必须复用训练时的处理方式。

<a id="ex3"></a>

## 第3题

```python
def assert_group_splits(train, val, test):
    a,b,c = set(train),set(val),set(test)
    if not a or not b or not c:
        raise ValueError("nonempty source groups required")
    if a & b or a & c or b & c:
        raise ValueError("source group overlap")
    return True
```

应传原始来源的稳定 ID，不能用复制后新起的文件名代替。函数只证明输入集合没有交叉，无法发现你把同一物体误标为两个 ID。

<a id="ex4"></a>

## 第4题

两个窗口共享帧2。先按回合/来源组分再切窗，必要时在时间边界留间隔并检查完整 frame_id 集合。未来观测进入当前输入则是时序因果泄漏，即使整个 episode 只属于一个 split 也会发生；要核对时间戳和输入窗口定义。
