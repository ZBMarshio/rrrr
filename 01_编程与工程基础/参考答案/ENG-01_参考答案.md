# ENG-01：提示与参考答案

[返回题目](../讲义/ENG-01_Python模块类与异常.md) · [记录自己的理解](../练习与复盘记录.md)

先写预测再看答案。参考代码用于局部对照；尝试关掉页面，换一组输入独立再做一次。

<a id="ex1"></a>

## 第 1 题

提示：先画对象，再把变量名连到对象上。

上例输出：

```text
left_joint [0.2]
right_joint [-0.1]
```

执行 `alias = other` 后，alias 改为关联 other 所指的对象；再 add 时 other 的列表成为 `[-0.1, 0.5]`，log 仍为 `[0.2]`。

若改为类属性 `samples = []`，两个实例没有自己的同名属性时，会查到同一个类属性列表；各追加一次后，通过任一实例读出的列表都包含两次追加。这不同于原例在每次初始化中创建独立列表。

一种解释：变量是程序里用来找到对象的名字；对象是实际包含数据、类型和相应行为的实体。类属性的例子要单独重新运行，避免混入原例已有状态。

<a id="ex2"></a>

## 第 2 题

提示：默认参数表达式在定义函数时求值。需要一个表示“没有提供列表”的哨兵值。

原输出依次为 `[0.1]`、`[0.1, 0.2]`。可改为：

```python
def collect(value, buffer=None):
    if buffer is None:
        buffer = []
    buffer.append(value)
    return buffer
```

不要写 `if not buffer` 来代替：调用者显式提供的空列表也会被判为假，从而失去“累积进这份列表”的约定。

验证：不传列表的两次调用结果独立；传同一个 `shared = []` 后调用两次，shared 应同时保存两次数据。

<a id="ex3"></a>

## 第 3 题

提示：先检查数据边界，再做转换；返回新列表。

```python
import math

def validate_sample(t_s, q):
    def is_number(x):
        return (
            not isinstance(x, bool)
            and isinstance(x, (int, float))
            and math.isfinite(x)
        )

    if not is_number(t_s) or t_s < 0:
        raise ValueError("t_s must be finite and non-negative")
    if not isinstance(q, (list, tuple)) or len(q) != 2:
        raise ValueError("q must contain two joint positions")
    if not all(is_number(x) for x in q):
        raise ValueError("q must contain finite numbers")
    return float(t_s), [float(x) for x in q]
```

`validate_sample(0, [0.1, -0.2])` 返回 `(0.0, [0.1, -0.2])`。负时间、错误长度、NaN、布尔值应抛错。这里的输入范围是基础数值类型；支持 NumPy 类型时需重新声明和验证接口，不能直接声称已经兼容所有数值对象。

判断是否不改原数据：保存 `original = [0.1, -0.2]`，调用后修改返回列表，再检查 original。单纯比较两份列表的值还不足以验证是否共享对象。

<a id="ex4"></a>

## 第 4 题

`trajectory.py` 只放导入和第 3 题函数定义。`main.py` 可以这样写：

```python
from trajectory import validate_sample

def main():
    sample = validate_sample(0.0, [0.1, -0.2])
    print(sample)

if __name__ == "__main__":
    main()
```

在包含这两个文件的目录中分别运行题目里的两条命令。导入 main 也不应调用 main()；直接执行才进入条件分支。

如果导入失败，先检查工作目录、文件名和实际被导入的模块位置，接着查 ENG-06。暂时不向代码里随意追加 sys.path 来掩盖入口不清的问题。

