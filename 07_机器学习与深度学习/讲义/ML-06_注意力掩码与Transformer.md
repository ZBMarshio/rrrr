# ML-06：先画清楚谁能看见谁

[学习指南](../学习指南.md) · [知识索引](../知识索引.md#ml-06) · [提示与答案](../参考答案/ML-06_参考答案.md)

<a id="intro"></a>

## 导读

**为什么学这一节。** 序列模型需要决定哪些信息可以相互读取。token、位置和mask解释了这种关系，也决定模型会不会偷看未来或学习无效填充。

**学完会有什么变化。** 从看到Transformer就把它当黑箱，进到能追踪Q/K/V与多头维度，手算注意力，区分因果、padding和loss掩码。

**接下来能做什么。** 可以读懂[LEARN-03](../../08_机器人学习与具身智能/导读.md#learn-03)的动作块与历史观测，检查多模态输入的信息流；当前先掌握机制和接口。

## 资料与范围

读 [D2L 注意力与 Transformer](https://zh.d2l.ai/chapter_attention-mechanisms/index.html) 的缩放点积、多头、位置编码与 Transformer 结构；对照原论文 [Attention Is All You Need](https://arxiv.org/abs/1706.03762) 第 3 节。API 查 [PyTorch 2.6 SDPA](https://docs.pytorch.org/docs/2.6/generated/torch.nn.functional.scaled_dot_product_attention.html)。

本节掌握计算与形状，不要求从零训练语言模型。ACT、时序策略、视觉语言模型都需要这里的基础；MLP actor/critic 等基本 RL 网络可以先开始，不以 Transformer 为前置。

## 沿着形状理解

输入 token `X:[B,T,D]`，线性投影得到 Q/K/V。一次注意力：

$$P=\operatorname{softmax}(QK^\top/\sqrt{d_k}+\text{mask}),\quad Y=PV.$$

自注意力的 Q/K/V 来源相同；交叉注意力的 query 与 key/value 来源可不同，序列长度 L 与 S 也可不同。多头拆成 `[B,H,T,d_h]`，每个头独立计算后拼回。常规实现 D 应能被 H 整除。

位置编码表达顺序；仅点积注意力本身不区分“前一个”和“后一个”。Transformer 还有残差、LayerNorm 和逐 token FFN；它们不能在解释结构时省略。Pre-LN/Post-LN 的顺序按具体模型核对。

## 三种 mask 分开说

- attention mask：哪些 query 可以看哪些 key；causal mask 禁止未来信息。
- padding/key mask：哪些位置不是有效内容，避免被当作 key；无效 query 的输出仍需在后续处理。
- loss mask：哪些输出参与目标函数，分母按有效项计数。

PyTorch 2.6 的 SDPA 布尔 True 表示允许参与；`nn.MultiheadAttention` 的布尔 attn_mask True 表示阻止。必须查正在使用的接口，不能只记“True 就屏蔽”。SDPA 的 dropout_p 也要显式在评测时设为 0，不会自动读取外层 eval。

本章手写注意力与 SDPA 在 CPU/CUDA 上都核对过；先用 float64 检查公式，再考虑 float32/AMP 与高效内核。设备、精度和内核会影响舍入误差与容差，不用逐位相同作为跨后端的默认要求。

## 练习

<a id="ex1"></a>

### 第 1 题：手算一次注意力。约 25 分钟

令 Q=K=I2、V=[[1,0],[0,2]]。计算缩放后的 scores、按行 softmax、输出。说明权重每行为什么和为 1、每列为什么不必。

<a id="ex2"></a>

### 第 2 题：实现并对照。约 35 分钟

实现无 dropout 的单头注意力，输入 Q:[B,L,D]、K:[B,S,D]、V:[B,S,Dv]，布尔 allowed:[B,L,S]。与官方 SDPA 对照。拒绝没有任何有效 key 的行，而不是任其产生 NaN。

<a id="ex3"></a>

### 第 3 题：未来信息与 API。约 30 分钟

四个 token，分别用全连接和 causal mask。只改最后一个 token 的 K/V，检查前面输出在 causal 下不变。再接 MultiheadAttention 时解释为何要反转布尔语义。用一层 batch_first TransformerEncoderLayer 验证 [2,4,8] 的输入输出。

<a id="ex4"></a>

### 第 4 题：padding 不应改变 loss。约 30 分钟

预测/标签 [B,T,A]，valid:[B,T]。实现 masked MSE。把无效标签改成很大数或 NaN，loss 应不变；全无效时明确拒绝。因果 mask 可以直接作为这个 valid 吗？

## 直觉与回顾

注意力是在当前特征下分配读取信息的权重。它没有自动理解时间、坐标和因果关系；这些约束需要位置、mask、数据和训练目标共同表达。

复盘：看到 [B,T,D] 时，你能指出 T 是观测历史、图像块还是未来动作吗？
