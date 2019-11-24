## 本论文方法的优点
1. 不需要data, fine-tuning 或者 超参数的选择


## 观点
1. FP32->INT8引入 量化噪声


## 分级的量化解决方案
在文献中很少讨论所提出的量化方法的实际应用。 为了区分量化方法的适用性差异，我们按实际适用性的降序介绍了四个级别的量化解决方案。

1. 无数据 没有训练需要，这个方法可以运行在所有的模型上。直接使用简单APi进行调用，查看模型定义和权重。
2. 需要数据，但无反向传播。 适用于任何模型。 使用数据例如 重新校准批次归一化统计数据，计算逐层损失函数以提高量化性能。但是，不需要微调。（Probabilistic binary neural networks. arXiv preprint arxiv:1809.03368, 2018）
3. 需要数据和反向传播。 适用于任何模型。 模型可以量化，但需要进行微调才能达到可接受的性能。 通常需要进行超参数调整才能获得最佳性能。These methods require a full training pipeline（需要完整的pipeline） (google, 最初的增量量化)
4. 需要数据和反向传播。 仅适用于特定型号。 在这种情况下，网络架构需要不平凡的重做，和/或架构需要从头开始进行训练，同时要考虑量化问题（例如[(quantization-friendly separable convolution for mobilenets.)]）。 需要花费大量的额外训练时间和超参数调整才能工作。

这种方法的一个主要缺点是，它并不是在所有的硬件上都受支持，而且它会在计算中产生不必要的开销，因为需要为每个通道分别设置比例和偏移量。**证明了我们的方法改进了每通道量化，同时为整个权张量保留了一组比例尺和偏移量。**

另一些量化结构需要从一开始就进行架构更改或进行量化训练，这个属于Level4，由于采样和噪声优化，它们在训练过程中会产生较大的开销，并引入额外的超参数进行优化。

二值与三值网络虽然很快，然而，将模型量化为二进制常常会导致严重的性能下降。通常他们需要从头开始训练，使他们成为4级方法。

低比特浮点->硬件实现是低效的

> Recovering neural network quantization error through weight factorization
其方法还利用ReLU函数的尺度方差来重新调整权重通道，并注意到权重量化[7]所引入的偏置误差

## 动机

### 权重量化

1. 权重与很范围很浮动
![20191124120931.png](https://i.loli.net/2019/11/24/FKXslZNYErUIwAo.png)
2. 我们推测，经过量化的训练模型的性能可以通过调整每个输出通道的权值来提高，使它们的范围更加相似。（这是为什么）

### biased quantization error

1. 一般论文的假设是激活量化是无偏的。因此在一层的输出中可以抵消，从而确保一层的输出的平均值不会因为量化而改变。然而，正如我们将在本节中展示的，权值的量化误差可能会在相应的输出上引入偏差。这改变了下一层的输入分布，可能会造成不可预测的影响。具体的公式为:
![20191124140449.png](https://i.loli.net/2019/11/24/VQgG5ve7WUzyYfq.png)

其做出的改变是引入偏差矫正改变，效果如下：

![20191124140757.png](https://i.loli.net/2019/11/24/ni6bGHS13yUgvNE.png)

深度可分离卷积特别容易受该影响。在许多设置中，例如在剪裁权值或激活时，可能会引入这样的输出偏差。此外，本文证明了模型的批处理归一化参数可以用来计算输出的期望偏置误差，从而得到了修正量化所引入的偏置误差的第一级方法。（核心）

## 核心

### Cross-layer range equalization

线性特征（文称为 Positive scaling quivariance）：

$$f(sx) = sf(x)$$

比如说ReLU和PreLU就是这个思路，更一般地，对于任何分段线性激活函数，正尺度变换的方差可以放宽为$f(sx) = s\hat{f}(x)$，因此多分段的线性激活函数的参数变化为``

下式为PreLU函数：

$$
f(x)=\left\{\begin{array}{cc}{a_{1} x+b_{1}} & {\text { if } x \leq c_{1}} \\ {a_{2} x+b_{2}} & {\text { if } c_{1}<x \leq c_{2}} \\ {} & {\vdots} \\ {a_{n} x+b_{n}} & {\text { if } c_{n-1}<x}\end{array}\right.
$$

### Scaling equivariance in neural network

设连续两层为$h=f(W^{(1)}x + b^{(1)})$和$y=f(W^{(2)}x + b^{(2)})$

则通过缩放不变性可以这样表现:
$$
\begin{aligned} \mathbf{y} &=f\left(\mathbf{W}^{(2)} f\left(\mathbf{W}^{(1)} \mathbf{x}+\mathbf{b}^{(1)}\right)+\mathbf{b}^{(2)}\right) \\ &=f\left(\mathbf{W}^{(2)} \mathbf{S} \hat{f}\left(\mathbf{S}^{-1} \mathbf{W}^{(1)} \mathbf{x}+\mathbf{S}^{-1} \mathbf{b}^{(1)}\right)+\mathbf{b}^{(2)}\right) \\ &=f\left(\widehat{\mathbf{W}}^{(2)} \hat{f}\left(\widehat{\mathbf{W}}^{(1)} \mathbf{x}+\widehat{\mathbf{b}}^{(1)}\right)+\mathbf{b}^{(2)}\right) \end{aligned}
$$

其中$S = diag(s)$是一个对角矩阵$S_{ii}$是神经元的scale factor。因此我们将模型转换为$\hat{W}^{(2)} = W^{(2)}S$，$\hat{W^{(1)}} = S^{-1}W^{(1)}$和$\hat{b}^{(1)}=S^{-1}b^{(1)}$

### Equalizing ranges over multiple layers

使用rescaling和reparameterization去提高量化的鲁棒性。理想情况下，每个通道i的范围等于权张量的总范围。我们想找到S使得每个通道的总精度最大化

当在同一时间均衡多个层时，我们迭代这个过程，以获得相互连接的层对，它们之间没有输入或输出分隔，直到收敛。

### Absorbing high bias

如果$s_{i} < 1$ 这个会到导致$b_i$会膨胀，这可以反过来增加激活量化的范围，为了避免这个问题引入高偏差吸收到后续层的操作，其过程为：
$r(Wx + b - c) = r(Wx + b) - c$

![20191124161906.png](https://i.loli.net/2019/11/24/oG1EMLNrjnXCZSV.png)

为了实现本文所提出的data-free，这方面还做了如下处理。我们假设偏置激活（pre-bias）是BN移位而分布的。（为什么能这样， 什么是pre-bias）
因此 $c = max(0, \beta - 3 \gamma)$，上述等式适用于99:865%的x值。

他不会损失精度甚至可以提升效果。

### Quantization bias correction

如何校正层输出误差中的偏差，以及如何在不使用数据的情况下使用网络的批处理规范化参数来计算偏差。

$\mathbf{W}$是量化后的权重，$W$为量化前的权重。因此有$\widetilde{\mathbf{y}}=\widetilde{\mathbf{W}} \mathbf{x}$, $y = Wx$其中$\mathbf{y} = y + \epsilon x$，其中$\epsilon = \mathbf{W} - W$

1. 输入期望的计算：用前一层的BN去推导计算 $E(x)$
我们假设一个层的预激活输出是正态分布的，批量归一化在激活函数之前进行，激活函数是clip线性激活函数的某种形式（类似ReLU），它可以将输出clip到$[a, b]$区间中。
首先引入`cliped normal distribution` 之后通过此求出。

![20191124172339.png](https://i.loli.net/2019/11/24/fmaKEYJxwHPLnVe.png)

## 实验条件

+ 8-bit 非对称量化
+ 粒度： pre-tensor
+ BN fold
+ 权重： max-min量化

激活量化范围通过使用学习批量标准化转变和尺度参数向量β和γ如下：

$$\boldsymbol{\beta}_{i} \pm n \cdot \boldsymbol{\gamma}_{i}$$ n=6

剪切的最小值为0(ReLU)

结果

![20191124200208.png](https://i.loli.net/2019/11/24/G1gcB5OAV3UwQaL.png)