## quantization network

### 聚焦的问题

forward和backward 过程中使用的函数的不同，梯度不同会导致训练的不稳定性。[详见train-aware quanization]
+ forward: $x_{out} = \delta clamp(0, N-1, round(\frac{x}{\delta} - z))$
+ backward: $x_{out} = clamp(x_{min}, x_{max}，x)$
这样会出现梯度不匹配的现象

过去的工作：

本文的贡献
1. 提出了量化方法`simple/straightforward` and `general/uniform`
2. 实现了一个`end-to-end`量化网络 可用与分类与目标检测

### 过去的工作

approximate-based 和 optimization-based 

approximation-based:
1. BinaryConnect -> 直接量化权重，backward使用 hard tanh [疑似SDQ的思路来源]
2. BWN 加入scale factor 在二值量化中。
3. TWN：三值。
4. TTQ：可训练的三值网络。
5. DoReFa-Net -> 量化weight和activation使用不同的量化方式。梯度是由基于全精度权重绝对值平均值的自定义形式近似得到的。
6. 全整数训练
7. Google提出一种整数到实数的仿射映射，允许使用只使用整数的算法进行推理。[经典论文]
8. HashNet 采用类似的连续松弛来训练散列函数，其中使用单个tanh函数进行二值化。

optimization-based
1. Leng等人在中引入了权值的凸线性约束，并用乘法的交替方向法求解

缺点是只能用在weight的量化，且此类迭代解的训练计算量较大。

## QN

思想有点像`Maxout`（一种激活函数，缓解了ReLU的问题，但本身参数过多，已淘汰）
我们首先从非线性函数的角度提出量化的新解释，然后是量化网络的学习。

## Experiments

第一层和最后一层不量化。

先训练weight量化再训练activation量化。

T采取的是使用Linear策略， DSQ采用的是进化策略

本文虽然对比了几种T的增长方式，需要大量的手动调参，而且不同网络的收敛速度，也不尽相同，很大的限制了这种。

# 总结

## train-aware quantization

### 解决forward与backward的不匹配问题

+ Quantization Network [使用sigmoid函数做step function的拟合]
+ Differentiable Soft Quantization: Bridging Full-Precision and Low-Bit Neural Networks [使用系列tanh拟合 step function]
+ Deep learning with low precision by half-wave gaussian quantization [分段逼近, 待看]
