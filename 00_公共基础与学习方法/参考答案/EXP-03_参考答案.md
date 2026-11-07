# EXP-03：提示与参考答案

[返回题目](../讲义/EXP-03_配置种子与复现.md) · [复盘](../练习与复盘记录.md)

<a id="ex1"></a>

## 第1题

配置字段可以是 experiment_id、data_file/hash、split、unit、model、solver/rcond、metrics、software、run_command、output_dir。生成真值 a=1.08/b=.015 是作者检查条件；拟合输入只用 train 的参考值和读数，不把真值当估计结果。

run_command 填自己实际执行成功的命令；没有提供训练脚本时，不把一个虚构入口写成“可复现命令”。

<a id="ex2"></a>

## 第2题

```python
import hashlib
import json
from pathlib import Path

def config_digest(config):
    payload = json.dumps(config,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
```

小数据文件可直接读；大文件再流式分块。config 使用明确 schema 的 JSON 基本类型；摘要依赖序列化约定，例如 1 和 1.0 在此约定下可能不同。摘要只比内容，错误单位或错误标签也能稳定地产生摘要。

<a id="ex3"></a>

## 第3题

第一个生成器取的是序列第2—4项，另一个取第1—3项。局部 RNG 避免被其他模块随意消耗，但自己的调用顺序仍要固定。保存实际输入后，可先核对输入完全相同，再讨论计算容差、版本与后端。

<a id="ex4"></a>

## 第4题

```python
import copy
import numpy as np

def snapshot_generator(rng):
    if not isinstance(rng.bit_generator,np.random.PCG64):
        raise ValueError("this reference uses PCG64")
    return copy.deepcopy(rng.bit_generator.state)

def resume_generator(state):
    if state.get("bit_generator") != "PCG64":
        raise ValueError("PCG64 state required")
    bit_generator = np.random.PCG64()
    bit_generator.state = copy.deepcopy(state)
    return np.random.Generator(bit_generator)
```

本例 PCG64 state 可按 JSON 基本类型保存，实际核对版本为 NumPy 1.26.4。其他 bit generator 可能有不同状态表示；不把此函数当通用兼容器。网络还需要模型/优化器、数据顺序、其他 RNG、scaler 等，第七章提供相应验证。
