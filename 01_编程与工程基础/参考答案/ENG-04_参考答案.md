# ENG-04：提示与参考答案

[返回题目](../讲义/ENG-04_CPP引用指针与生命周期.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

输出为 `0.2` 和 `1.2`。若约定空指针表示调用错误，可以写：

```cpp
#include <stdexcept>

void by_pointer(double* q) {
    if (q == nullptr) {
        throw std::invalid_argument("position pointer is null");
    }
    *q += 1.0;
}
```

指针副本仍保存同一地址，`*q` 访问的是原数值。若你约定空指针时直接返回，也可以符合自己声明的接口，但调用者需要知道这代表“没有操作”；不能让行为含糊。

继续使用原例 position 时，by_pointer 调用后成为约 2.2。浮点比较用合理容差，打印表示与内部精确值不是同一回事。

<a id="ex2"></a>

## 第 2 题

| 语句 | 结论 |
|---|---|
| `*p = 0.5;` | 不可通过指向 const 的通道修改值 |
| `p = &b;` | 可以，指针自身可改变 |
| `*fixed = 0.5;` | 可以修改 a |
| `fixed = &b;` | 不可以，指针自身是 const |

对每行独立从题目初始状态判断。`const double*` 不会把原本可修改的 a 永久冻结；例如直接 `a = 0.8;` 仍可行。

<a id="ex3"></a>

## 第 3 题

local 在函数返回、离开其作用域时销毁。返回的引用随后悬空；使用它没有可依赖的正常数值结果。

```cpp
double position_value() {
    double local = 0.2;
    return local;
}
```

返回 double 值独立于局部对象的寿命。对小数值，先写明白；对复杂对象，现代 C++ 还有返回值优化与移动等机制，以后按需学。不要用 static 局部变量作为这题的默认修复，它会额外引入共享状态。

<a id="ex4"></a>

## 第 4 题

提示：先验证边界，再限制数值。反向区间不能交给算法猜测。

```cpp
#include <algorithm>
#include <cmath>
#include <stdexcept>

double clamp_position(double q, double lower, double upper) {
    if (!std::isfinite(q) || !std::isfinite(lower)
        || !std::isfinite(upper) || lower > upper) {
        throw std::invalid_argument("invalid position or bounds");
    }
    return std::clamp(q, lower, upper);
}
```

对边界 `[-1,1]`，q 为 -2、0.2、3 时返回 -1、0.2、1；上下界同为 0.5 时，有效 q 都返回 0.5。反向边界或任何 NaN/无穷值抛异常。

这是函数片段，需要放到你自己的程序中，由 main 调用并检查结果。参考实现的返回类型是 double，立即按值返回；不要在这里改为返回 std::clamp 得到的引用。

