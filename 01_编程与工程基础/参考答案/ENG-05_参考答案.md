# ENG-05：提示与参考答案

[返回题目](../讲义/ENG-05_CPP容器类与所有权.md) · [复盘记录](../练习与复盘记录.md)

<a id="ex1"></a>

## 第 1 题

a 的 size 是 3，值为 `[0.5,0.5,0.5]`；b 的 size 是 2，值为 `[3.0,0.5]`。

auto x 是每次迭代得到的 double 副本，对 x 赋值不改变 v。auto& x 绑定原元素，清零后 v 为 `[0.0,0.0]`。将这两段分别从相同初始数组运行。

<a id="ex2"></a>

## 第 2 题

提示：用协议给出的名字序列逐一取值，不从容器自身的排序推出协议。

```cpp
#include <map>
#include <string>
#include <vector>

std::vector<double> ordered_values(
    const std::vector<std::string>& names,
    const std::map<std::string, double>& state) {
    std::vector<double> result;
    result.reserve(names.size());
    for (const auto& name : names) {
        result.push_back(state.at(name));
    }
    return result;
}
```

题目应得到 `[0.2,0.1]`。缺键时 at 抛 out_of_range；入口可补充“缺失哪个关节”的信息。直接遍历默认 string map 按键排序，不等于接口指定顺序。

在非 const map 上访问 `state["joint_3"]` 会插入值 0.0。这个“零”不能当成真实设备读数。

<a id="ex3"></a>

## 第 3 题

next 持有原来的 Joint，owner 已为空。shared 和 also_shared 共同持有另一个 Joint；仅这段代码中，强引用计数为 2。

unique_ptr 不允许复制，移动才表达责任转移。对这两个普通构造出的 shared_ptr，最后一个强持有者释放时，所管理的 Joint 销毁；若还有 weak_ptr，控制块可能继续存在，但 weak_ptr 不保持 Joint 存活。

对象间只用 shared_ptr 互相持有可能形成环，使强引用数降不到零。R.24 中的 weak_ptr 可用于表达非拥有关系；现阶段先能识别环，不要求实现完整观察者框架。

<a id="ex4"></a>

## 第 4 题

提示：先完成所有输入检查，再改变内部状态。

```cpp
#include <cmath>
#include <stdexcept>
#include <vector>

class Sampler {
public:
    Sampler() : values_(2, 0.0) {}

    void update(const std::vector<double>& values) {
        if (values.size() != 2) {
            throw std::invalid_argument("expected two joints");
        }
        for (double value : values) {
            if (!std::isfinite(value)) {
                throw std::invalid_argument("joint values must be finite");
            }
        }
        values_ = values;
    }

    const std::vector<double>& state() const {
        return values_;
    }

private:
    std::vector<double> values_;
};
```

赋值复制 vector 数据，因此改变调用者的 vector 不会改变 values_。state 返回的是内部 vector 对象的只读引用，不能在 Sampler 销毁后继续使用。

若保存 `const auto& previous = sampler.state();`，它不是快照。sampler 再次成功 update 后，通过 previous 会看到更新后的 vector 内容。想保存更新前的数据，写 `auto previous = sampler.state();`，这里按值复制 vector。

两种 auto 用法的差别，可以与 Python 列表/NumPy 视图对照理解，但不要直接假设它们遵循完全相同的复制规则。

