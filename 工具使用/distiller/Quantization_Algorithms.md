## Range-Based Linear Quantization

+ Linear: 表示浮点值是通过与数字常数（比例因子）相乘来量化的。

+ Range-Based: 意味着为了计算比例因子，我们查看张量值的实际范围。在简单的实现中，我们使用张量的实际最小/最大值。或者，我们使用基于张量的范围/分布的一些推导来得出较窄的最小/最大范围，以消除可能的异常值。这与此处描述的其他方法形成了鲜明对比，我们可以将其称为基于裁剪的方法，因为它们在张量上施加了显式裁剪功能（使用硬编码值或学习值）。

Asymmetiric Mode

![](https://i.loli.net/2019/11/15/W4qcZUadtQYJEyD.png)

$$x_q = round\left ((x_f - min_{x_f})\underbrace{\frac{2^n - 1}{max_{x_f} - min_{x_f}}}_{q_x} \right) = round(q_x x_f - \underbrace{min_{x_f}q_x)}_{zp_x} = round(q_x x_f - zp_x)$$

在使用的时候一般使用$zp_x = round(min_{xf} \times q_{x})$，这样的话可以将0与一个确定值对应一个确定的INT8的值。

Symmetric Mode

在对称模式下，我们选择最小/最大之间的最大绝对值，而不是将浮动范围的确切最小值/最大值映射到量化范围。另外，我们不使用零点。因此，我们正在有效量化的浮点范围相对于零是对称的，量化范围也是如此。

![](https://i.loli.net/2019/11/15/GxwRI2PM3VAtigJ.png)

两种方式的对比

1. 如果值的分布不均匀Symmetric Mode会有很大损失
2. 另一方面，如果我们考虑到卷积/FC层的计算，我们可以看到对称模式的实际实现要简单得多。在非对称模式下，零点在硬件中需要附加逻辑。当然，就等待时间和/或功率和/或面积而言，这种额外逻辑的成本将取决于确切的实现。


Removing outliers(post-training only):
类似nvidia的方案就是要提出异常值，做一个阈值裁剪。
支持两种算法：

+ 平均：将全局最小值/最大值替换为批次中每个样品的最小值/最大值的平均值。
+ Mean +/- N*Std: 张量的均值取N个标准差，无论如何不要超过张量的实际最小/最大值。 N是用户可配置的。（使用标准差）

Scale factor approximation (post-training only)：
可以模拟，

![](https://i.loli.net/2019/11/15/6wlI1zJMomBUrfH.png)


## Post-Training

对于训练后量化，通过用量化和反量化操作包装现有模块来实现此方法。包装器为`range_linear.py`
支持操作为

+ Convolution
+ Fully connected
+ Element-wise addition
+ Element-wise multiplication
+ Concatenation
+ Embedding

整个过程由`PostTrainLinearQuantizer`的对象调用

```python
quantizer = distiller.quantization.PostTrainLinearQuantizer(model, <quantizer arguments>)
quantizer.prepare_model()
```

量化器能转换的目标仅限于`torch.nn.Module`的子类。

一些张量的基本操作（例如 + * ）会被distiller的操作符替代

对于权重和偏差，比例因子和零点在量化设置（“离线”/“静态”）下确定一次。对于激活，同时支持“静态”和“动态”量化。静态定量激活需要事先收集统计信息。

静态量化要使用`Collectiong Statistics for Quantization`去实现这个效果

量化的参数会被保存在缓冲中，因此在保存模型检查点时它们会自动序列化。

## Quantization-Aware Training

使用`QuantAwareTrainRangeLinearQuantizer`类去实现，需要插入`FakeLinearQuantization`

在激活量化时使用指数移动平均值来跟踪激活范围。

`QuantAwareTrainRangeLinearQuantizer`的当前实现仅支持使用单个GPU进行训练。(Pytorch的一机多卡呢？)

请注意，尚不支持从感知量化的训练模型转换为训练后的量化模型。这样的转换将使用在训练过程中跟踪的激活范围，因此将不需要进行离线或在线的量化参数计算。

### DoReFa

定义一个量化函数
$$a_q = quantizer_k (a_f) = \frac{1}{2^k - 1} round((2^k - 1) a_f)$$

其中$a_f \in [0, 1], a_q \in \{ \frac{1}{2^k - 1}, \frac{2}{2^k - 1}...,\frac{2^k - 1}{2^k - 1} \}$

对于激活量化直接将激活值剪切到[0, 1]的范围内，$x_q = quantizer_k(x_f)$

对于权值，我们使用如下办法将其转换为[0, 1]的区间中：
$$f(w) = \frac{tanh(w)}{2 max(|tanh(w)|)} + \frac{1}{2}$$
然后量化权值
$$w_q = 2quantizer_k(f(w_f)) - 1$$

+ 目前尚不支持本文提出的梯度量化。
+ Distiller不支持特殊处理

### PACT

### WRPN

激活被剪切到$[0,1]$

$$x_q = \frac{1}{2^k - 1}round((2^k - 1)x_f)$$

权重剪切到$[-1, 1]$

$$x_w = \frac{1}{2^{k-1} - 1}round((2^{k-1} - 1)w_f)$$

这种方法需要使用量化感知训练来训练模型，如此处所述。使用`WRPNQuantizer`类将现有模型转换为适合使用WRPN进行量化训练的模型。

+ 本文提出了加宽层以减少精度损失的方法。目前尚未将其实现为WRPNQuantizer的一部分。要对此进行试验，请修改模型实现以具有更大的层次。
+ 不支持特殊操作。