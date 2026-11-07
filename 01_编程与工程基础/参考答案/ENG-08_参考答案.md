# ENG-08：提示与参考答案

[返回题目](../讲义/ENG-08_构建调试与基本验证.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

提示：用一正一负且绝对值相等的数。

`[-1.0,1.0]` 的 RMSE 是 1，但原函数返回 0；`[2.0,2.0]` 却会让错误实现碰巧得到正确值。

```python
import math

def rmse(errors):
    values = [float(x) for x in errors]
    if not values or not all(math.isfinite(x) for x in values):
        raise ValueError("errors must be non-empty and finite")
    return math.sqrt(sum(x * x for x in values) / len(values))
```

这是小规模、普通量级误差的参考实现。极大数值的平方还可能溢出；当前不把它推广为适用所有数值范围的计算库。

<a id="ex2"></a>

## 第 2 题

把上题放入自己的 `metrics.py` 后，可在项目根目录保存 `test_metrics.py`：

```python
import math
import unittest
from metrics import rmse

class TestRMSE(unittest.TestCase):
    def test_zero(self):
        self.assertAlmostEqual(rmse([0.0, 0.0]), 0.0)

    def test_opposite_signs(self):
        self.assertAlmostEqual(rmse([-1.0, 1.0]), 1.0)

    def test_different_sizes(self):
        self.assertAlmostEqual(rmse([3.0, 4.0]), math.sqrt(12.5))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            rmse([])
        with self.assertRaises(ValueError):
            rmse([float("nan")])

if __name__ == "__main__":
    unittest.main()
```

运行 `python3 -m unittest -v`。这些数值答案来自公式与手算，而不是把被测函数再写一遍；正负例能区分错误实现。

如果你用 tests 子目录，明确对应的 discovery 命令与模块路径，不要先引入复杂测试配置。

<a id="ex3"></a>

## 第 3 题

1. 编译：检查首个相关语法诊断，修复源码；后续诊断可能是连锁反应。
2. 链接：看定义是否实现、签名是否一致、stats.cpp 是否加入目标。
3. 运行/输入：记录实际绝对路径、当前目录与配置路径，再检查文件是否存在。
4. 运行/边界：q 长度为 2，合法下标是 0、1；查索引来源。这里用 at 会抛异常；换成 [] 并不能修复越界。

<a id="ex4"></a>

## 第 4 题

最小参考实现如下，分别保存四个文件。它只验证构建与小计算，不是已完成的轨迹分析项目。

stats.hpp：

```cpp
#ifndef TRAJECTORY_STATS_HPP
#define TRAJECTORY_STATS_HPP
double squared_error(double observed, double reference);
#endif
```

stats.cpp：

```cpp
#include "stats.hpp"

double squared_error(double observed, double reference) {
    const double error = observed - reference;
    return error * error;
}
```

main.cpp：

```cpp
#include <iostream>
#include "stats.hpp"

int main() {
    std::cout << squared_error(0.3, 0.1) << '\n';
}
```

CMakeLists.txt：

```cmake
cmake_minimum_required(VERSION 3.16)
project(trajectory_demo LANGUAGES CXX)
add_executable(trajectory_demo main.cpp stats.cpp)
target_compile_features(trajectory_demo PRIVATE cxx_std_17)
```

按题目三条命令运行，输出约 0.04。若删除目标中的 stats.cpp，而保留函数声明，通常在链接时出现 undefined reference。恢复源文件并重新构建后通过。

留意修改的是源码目录的 CMakeLists，不是在 build 目录里临时补文件。已有源码改动后重新 build，不能只运行上次成功留下的旧二进制并认为改动已经生效。

