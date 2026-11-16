# ENG-02 配套：NumPy 官方文档双语精读

[返回 ENG-02 讲义](ENG-02_NumPy形状广播与计算.md) · 为第 1—4 题准备的原文、译文与实例

> 用法：讲义把“要读哪几节”指了出来，这份文件把那几节的英文原文逐段摘出，配上译文和我加的实例，省去在长文档里找段落的时间。每节先遮住译文自己翻一遍，再对照；节末的“自查”不给答案，是留给你动手的。
>
> 引用约定：正文里的 `[1]`—`[4]` 对应文末“出处”。原文只摘与 ENG-02 直接相关的句子，完整上下文请按链接回原文。文档版本 NumPy v2.5，访问日期 2026-11-16。

## 1. 形状、维度和轴（对应第 1、2 题）

### 1.1 shape、ndim、size

**原文**（[3] §Array attributes）：

> The number of dimensions of an array is contained in the `ndim` attribute.
>
> The shape of an array is a tuple of non-negative integers that specify the number of elements along each dimension.
>
> The fixed, total number of elements in array is contained in the `size` attribute.

**译文**：

- 数组的维数记录在 `ndim` 属性里。
- `shape` 是一个由非负整数组成的元组，依次给出每一维上有多少个元素。
- 数组元素的总数记录在 `size` 属性里。

**实例**：先把第 1 题的 `q` 建出来。

```python
import numpy as np

q = np.array([[0., 1.], [0.1, 0.9], [0.2, 0.8], [0.3, 0.7]])
q.ndim    # 2：两个轴
q.shape   # (4, 2)：4 行、2 列
q.size    # 8：一共 8 个数
```

把 `(4, 2)` 读成一句话：**4 个时刻，每个时刻 2 个关节**。行是时间，列是关节。

### 1.2 “轴”这个叫法

**原文**（[3] §Array fundamentals）：

> In NumPy, a dimension of an array is sometimes referred to as an “axis”. This terminology may be useful to disambiguate between the dimensionality of an array and the dimensionality of the data represented by the array.

**译文**：在 NumPy 里，数组的一“维”有时也叫一个“轴”。用“轴”这个词，是为了把**数组本身的维数**和**数据所表示的维数**分开说。

**实例**：`q` 有两个轴，但它描述的是一组二维平面上的点。说“第 0 轴”指行（时间），说“第 1 轴”指列（关节）。

**原文**（[3] 同节 Note）：

> a better mental model is to think of the column index as coming last and the row index as second to last.

**译文**：理解多维数组时，把“列的索引”想成最后一维、“行的索引”想成倒数第二维，比“先行后列”更容易推广到更多维。

### 1.3 切片返回视图

**原文**（[3] §Array fundamentals）：

> One major difference is that slice indexing of a list copies the elements into a new list, but slicing an array returns a *view*: an object that refers to the data in the original array. The original array can be mutated using the view.

**译文**：一个关键区别是：对列表做切片会把元素复制进新列表，而对数组做切片返回的是**视图**——一个指向原数组数据的对象。通过视图可以改到原数组。

**实例**：

```python
part = q[:2]        # 形状 (2, 2)，与 q 共享数据
part[0, 0] = 99.0
print(q[0, 0])      # 99.0
```

**自查**：`q[:2]` 的形状是什么？`q[:, 0]` 和 `q[:, 0:1]` 差在哪一维？

## 2. 广播规则（对应第 1、4 题）

### 2.1 规则原文

**原文**（[1] §General broadcasting rules）：

> When operating on two arrays, NumPy compares their shapes element-wise. It starts with the trailing (i.e. rightmost) dimension and works its way left. Two dimensions are compatible when
>
> 1. they are equal, or
> 2. one of them is 1.
>
> If these conditions are not met, a `ValueError: operands could not be broadcast together` exception is thrown, indicating that the arrays have incompatible shapes.

**译文**：两个数组做运算时，NumPy 逐个比较它们的形状，从**最后一维（最右边）**开始，往左走。两个维度兼容的条件是：① 相等；② 其中一个是 1。都不满足就抛出 `ValueError: operands could not be broadcast together`，说明形状不兼容。

**原文**（[1] 同节）：

> Input arrays do not need to have the same *number* of dimensions. … Note that missing dimensions are assumed to have size one.

**译文**：两个数组的维数可以不同，缺少的维按大小 1 处理。

### 2.2 合法广播的例子

**实例**：把偏置加到每个时刻。

```python
a = np.zeros((4, 2))
b = np.array([0.1, -0.2])   # (2,)
a + b                       # (4, 2)
```

从右往左比：`2` 对 `2` 相等 ✓；再往左，`4` 对缺省的 `1` ✓，所以合法。结果是每一行都加上同一组 `[0.1, -0.2]`。

### 2.3 不合法的例子（第 1 题第 2 小问）

```python
b2 = b[:, None]   # 形状 (2, 1)
a + b2            # ValueError
```

从右往左：`2` 对 `1` ✓（其中一个是 1）；再往左，`4` 对 `2` ✗——既不相等，也没有一个是 1，所以失败。

**自查**：

- `(4, 2) + (2,)` 的结果形状是？
- `(4, 2) + (2, 1)` 为什么失败？
- `(3, 2) / (2,)` 的结果形状是？每一列除以的是哪个数？

## 3. 聚合与 axis（对应第 2 题）

**原文**（[3] §Basic array operations）：

> To add the rows or the columns in a 2D array, you would specify the axis.

**译文**：在二维数组里，要按行还是按列求和，由 `axis` 指定。

**原文**（[3] §More useful array operations）：

> By default, every NumPy aggregation function will return the aggregate of the entire array. … You can specify on which axis you want the aggregation function to be computed. For example, you can find the minimum value within each column by specifying `axis=0`.

**译文**：默认情况下，聚合函数给出整个数组的一个汇总值；也可以指定沿哪个轴聚合。例如 `axis=0` 求的是每一列的最小值。

**实例**：

```python
a = np.array([[1, 1], [2, 2]])
a.sum(axis=0)    # [3, 3]：把行压掉，每列剩一个数
a.sum(axis=1)    # [2, 4]：把列压掉，每行剩一个数
a.mean(axis=0)   # [1.5, 1.5]
```

**记法**：`axis=k` 表示“把第 k 维消掉”。`(4, 2)` 沿 `axis=0` 消掉时间维，输出 `(2,)`，正好是每个关节一个数。

### 3.1 第 2 题会用到的小函数

- `np.isfinite(x)`：逐元素判断是否为有限数，返回布尔数组。
- `np.isnan(x)`：逐元素判断是否为 NaN。
- `np.sqrt(x)`、`np.mean(x, axis=0)`：开方、沿轴求平均。
- `np.asarray(x, dtype=np.float64)`：转成数组，并指定浮点类型。

**自查**：`error` 形状是 `(4, 2)`，`np.mean(error ** 2, axis=0)` 的形状是？单位是什么？

## 4. 视图与复制（对应第 3 题）

**原文**（[2] §View）：

> It is possible to access the array differently by just changing certain metadata like stride and dtype without changing the data buffer. … The data buffer remains the same, so any changes made to a view reflects in the original copy.

**译文**：只改动 stride、dtype 这类元数据、不动数据缓冲，就能得到另一种访问方式，这叫视图。数据缓冲不变，所以对视图的修改会反映到原数组上。

**原文**（[2] §Copy）：

> When a new array is created by duplicating the data buffer as well as the metadata, it is called a copy. Changes made to the copy do not reflect on the original array.

**译文**：把数据缓冲和元数据一起复制出来，得到的是副本。改副本不影响原数组。

**原文**（[2] §Indexing operations）：

> Views are created when elements can be addressed with offsets and strides in the original array. Hence, basic indexing always creates views. … Advanced indexing, on the other hand, always creates copies.

**译文**：只要元素能用偏移和步长在原数组里定位，就会产生视图；所以基本切片总是视图。高级索引（如 `x[[1, 2]]`）则总是副本。

**实例**：

```python
x = np.arange(10)
y = x[1:3]         # 视图
x[1:3] = [10, 11]
print(y)           # [10 11]：跟着变

q = np.array([[0., 1.], [0.1, 0.9], [0.2, 0.8], [0.3, 0.7]])
part = q[:2]           # 视图
saved = q[:2].copy()   # 独立副本
alias = q              # 只是第二个名字，不是副本
```

**原文**（[2] §How to tell if the array is a view or a copy）：

> The `base` attribute of a view returns the original array while it returns `None` for a copy.

**译文**：视图的 `base` 属性指向原数组；副本的 `base` 是 `None`。

```python
q[:2].base is q      # True：是视图
q[:2].copy().base    # None：是副本
```

**自查**：`alias = q` 之后改 `q`，`alias` 会变吗？为什么？要让“原始基准”不被后续修改影响，应该怎么写？

## 5. np.diff（对应第 4 题）

**原文**（[4] 描述与 Returns）：

> Calculate the n-th discrete difference along the given axis. The first difference is given by `out[i] = a[i+1] - a[i]` along the given axis … The shape of the output is the same as *a* except along *axis* where the dimension is smaller by *n*.

**译文**：沿指定轴计算 n 阶离散差分；一阶差分的定义是 `out[i] = a[i+1] - a[i]`；输出形状除了该轴少 n 个元素以外，与输入相同。

**实例**：

```python
x = np.array([1, 2, 4, 7, 0])
np.diff(x)              # [1, 2, 3, -7]，长度从 5 变 4

X = np.array([[1, 3, 6, 10], [0, 5, 6, 8]])
np.diff(X)              # (1, 3)：默认最后一维
np.diff(X, axis=0)      # (1, 4)：按行（时间）差分
```

### 5.1 形状推理：为什么“能算”不等于“算对”

> 这一节会把第 4 题要你自己发现的那个坑提前演示出来。如果还想先独立做一遍，先停在这里，做完再回来读。

用另一组数演示（练习时请换成讲义第 4 题自己的数）：

```python
t = np.array([0.0, 0.2, 0.5])          # (3,)
q = np.array([[0.0, 1.0],
              [0.2, 0.6],
              [0.7, 0.1]])             # (3, 2)

dt = np.diff(t)                        # (2,)
dq = np.diff(q, axis=0)                # (2, 2)
v  = dq / dt                           # (2, 2) / (2,)，能算
```

从右往左对齐：`dq` 的列有 2 个，`dt` 有 2 个，相等 ✓；`dq` 的行 2 个，`dt` 缺省为 1 ✓。所以不报错。

**但每一格实际除的是谁？** 广播把 `dt` 的第 j 个元素对到 `dq` 的第 j **列**：

```text
v[i, j] = dq[i, j] / dt[j]
```

而“第 i 个区间的平均速度”应该是：

```text
v[i, j] = dq[i, j] / dt[i]     ← 应当用第 i 个区间自己的时间差
```

只有 i 恰好等于 j 时两者才相同。用上面的数：`v[0, 1] = dq[0, 1] / dt[1] = (-0.4) / 0.3`，可第一区间是 `[0, 0.2]`，根本没有 0.5 这个时间点。**程序接受你的写法，只能证明广播规则允许，不能证明含义正确。**

**自查**：把讲义第 4 题的 `t`、`q` 代进去，手算两个区间、两个关节的速度；再指出 `v_bad` 的每一格实际除以了哪个 `dt`。

## 6. 四道题与这份文件的对应

| 题 | 先读这份文件 | 再读讲义 |
|---|---|---|
| 第 1 题 写形状 | §1.1—§1.3、§2.1—§2.3 | [第 1 题](ENG-02_NumPy形状广播与计算.md#ex1)（:58-73） |
| 第 2 题 RMSE | §1.1、§3、§3.1 | [第 2 题](ENG-02_NumPy形状广播与计算.md#ex2)（:77-85） |
| 第 3 题 视图 | §4 | [第 3 题](ENG-02_NumPy形状广播与计算.md#ex3)（:89-101） |
| 第 4 题 差分 | §2.3、§5 | [第 4 题](ENG-02_NumPy形状广播与计算.md#ex4)（:105-115） |

## 7. 术语表

| 英文 | 中文 | 一句话 |
|---|---|---|
| array | 数组 | 同类型元素、形状固定的数据块 |
| shape | 形状 | 每一维有几个元素的元组，如 `(4, 2)` |
| axis | 轴 | 数组的一维；聚合时指“被消掉的那一维” |
| broadcast | 广播 | 按尾部对齐规则把较小的数组扩展成兼容形状 |
| view | 视图 | 共享原数据的新数组，改它会改到原数组 |
| copy | 副本 | 数据独立复制，改它不影响原数组 |
| base | 基 | 视图指向的原数组；副本为 `None` |
| aggregation | 聚合 | 把一维或多维压成一个汇总值，如 sum、mean |
| discrete difference | 离散差分 | 相邻元素的差，`a[i+1] - a[i]` |
| RMSE | 均方根误差 | 误差平方的平均再开方 |

## 8. 出处

[1] NumPy Developers. *Broadcasting*, §General broadcasting rules. NumPy v2.5 Manual. https://numpy.org/doc/stable/user/basics.broadcasting.html#general-broadcasting-rules （2026-11-16）

[2] NumPy Developers. *Copies and views*, §View、§Copy、§Indexing operations、§How to tell if the array is a view or a copy. NumPy v2.5 Manual. https://numpy.org/doc/stable/user/basics.copies.html （2026-11-16）

[3] NumPy Developers. *NumPy: the absolute basics for beginners*, §Array fundamentals、§Array attributes、§Basic array operations、§More useful array operations. NumPy v2.5 Manual. https://numpy.org/doc/stable/user/absolute_beginners.html （2026-11-16）

[4] NumPy Developers. *numpy.diff*. NumPy v2.5 Manual. https://numpy.org/doc/stable/reference/generated/numpy.diff.html （2026-11-16）

> 原文片段版权归 NumPy Developers 所有，按 BSD-3-Clause 许可使用；这里只摘录与 ENG-02 相关的短句，并附链接，供个人学习。
