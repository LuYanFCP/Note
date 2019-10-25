
由于低比特量化的离散性，现有的量化方法常常面临训练过程不稳定和性能严重下降的问题，为了解决这个问题本文提出了Differentiable Soft Quantization(DSQ)。DSQ可以在训练过程中逐步逼近标准的量化。DSQ可以在反向传播的时候近似梯度，减少量化区间裁剪(clipping range)引起的误差。本文也在经典的模型上实现了DSQ，结果都可以得到比较好的结果。本文也首次实现了将2,4-bit量化的DSQ部署在ARM上，而且比腾讯开源的推理平台`ncnn`快1.7倍。

## Introduce

大多数的量化方法很依赖特定的硬件，并且由于指令集的限制很多时候并未能达到加速的效果。
在各种量化中只有二值网络和均匀量化(uniform quantization)是硬件友好型(现成的硬件即可使用, 不需要NPU等定制的硬件)的方法。即使如此两者在低比特的时候也会出现很明显的性能下降。原因:

1. 量化反向传播的时候需要量化（Google的实现方法，使用量化正向，浮点反向的方式避免了这一点），一般使用STE（straight through estimation）去近似，因此在低比特的时候误差非常大.
2. 量化无法避免的会引入误差，量化通常通过两种操作完成:裁剪（clipping）和舍入（rounding）。前者将数据限制在较小的范围内，而后者将原始值映射到最近的量化点。这两种操作都会造成量化损失。因此，为了缓解性能下降，找到一个合适的裁剪范围并在裁剪和舍入之间取得平衡也是很重要的。

为了解决这些问题我们提出了Differentiable Soft Quantizatio (以下称DSQ)
1. 采用一系列 tanh函数 逐步逼近阶梯函数进行低比特量化，这样也可导。并且使用自定义的DSQ函数去估计微分。
2. 在训练中自动训练裁剪的范围(clipping values)和自动训练还有tanh函数与真实量化的接近程度。

DSQ的优势：
1. 新的量化方式：引入DSQ函数去更好的估计，减少了量化反向传播时估计的误差。
2. 易收敛：DSQ可以看成一个整流器（rectifier）根据量化点逐步重新分配数据。因此正反传播趋向一致更容易收敛。
3. 平衡损失：通过DSQ同时确定clipping的范围和量化的估计程度，因此可以起到权衡各方面损失的作用。
4. 高效：比开源实现推理效果要快。
5. 高度灵活：DSQ与二值网络或uniform方法兼容，易于部署在最先进的网络结构中，并能得到进一步的精度提高。

## Related Work

## 网络量化

网络量化有两种思路。一种是使用{-1, +1}或者{-1, 0, +1}使用比特操作去量化。这种方式挑战很大。另一种思路是是将权重和激活统一转换为定点表示。低比特量化在精度上的挑战非常大，为了解决这个问题，前人尝试以端到端方式优化特定任务损失的裁剪值或量化区间，也有人应用不同的技术去解决各层不同的位宽。也有人尝试采用增量量化和渐进量化的方式优化训练的方法，还有一些尝试通过调整网络结构去适配量化。

### 高效部署(Efficient Deployment)

+ Nvidia TensorRT->提供了INT8的支持，支持TensorFlow的加速工具。
+ Intel Caffe 主要针对CPU平台的优化。
+ Gemmlowp TensorFlow平台的低比特GEMM库。（支持ARM与X86的部署）
+ NCNN 腾讯开源的移动端推理框架。支持int8。

以上框架都不针对较低的位计算进行特定的优化.

本文为了实现更低比特的位运算使用ARM NEON，它是在ARM Cortex-A 系列和Cortex-R52处理器的SIMD。

## Differentiable Soft Quantization

### Preliminaries

uniform量化框架：
1. 1-bit:
![二值量化](https://i.loli.net/2019/10/17/pFxfrgwsKjIDn4W.png)
2. 多比特量化模型
![多比特量化模型](https://i.loli.net/2019/10/17/7Ue2zNDJcq6xBQg.png)

### DSQ function

首先将x切为n个区间$\mathcal{P}_{i}$

其中：
$$\varphi(x)=s \tanh \left(k\left(x-m_{i}\right)\right), \quad \text { if } x \in \mathcal{P}_{i}$$
$$m_{i}=l+(i+0.5) \Delta \text { and } s=\frac{1}{\tanh (0.5 k \Delta)}$$
标度参数$s$可以保证每一个段顺利链接，另外$k$控制与量化值相近程度，k越大越接近真实的量化函数，如下图。

![不同k情况下的DSQ](https://i.loli.net/2019/10/17/lrc1MyaLiwth293.png)

**因此DSQ函数的定义为**

![DSQ](https://i.loli.net/2019/10/17/3FEXArH5vfOPpZC.png)

因为DSQ的连续的，因此可以直接进行梯度计算。

另一方面：DSQ就像一个整流器(rectifer)，通过简单的重分发使数据与量化点对齐，量化误差很小。

![1-bit与多bit量化的DSQ](https://i.loli.net/2019/10/17/AWicom4w9CDFYlU.png)

### 逼近标准量化(Evolution to the standard quantization)

DSQ与真实量化的接近程度(k)影响着最后量化模型的效果。也就是说，在训练过程中，我们需要自适应地选择合适的DSQ参数，从而根据量化网络的优化目标来保证受控逼近。

为了衡量DSQ与标准量化的相似程度，这篇论文引入$\alpha$去衡量相似程度。

$\alpha = 1 - tanh(0.5k\delta) = 1 - \frac{1}{s}$

$\alpha$对模型在DSQ中的表示如图3(a)。
![a](https://i.loli.net/2019/10/17/GEO5MTY1FrbN8nL.png)

图3(b)展示$\alpha$了影响,其中2比特量化模型是第一个训练使用DSQ对不同的$\alpha$，分别给出了DSQ、带符号函数的DSQ和标准均匀量化的推理精度性能曲线。很容易看出，我们的带符号的DSQ函数与均匀量化很一致。特别是,当$\alpha$很小,
DSQ可以很好地近似均匀量化的性能。这意味着一个适当$\alpha$可以帮助提高量化模型的精度。

<!-- 如果只能用$\alpha$和$\delta$来表示。
$$s = \frac{1}{1-\alpha}$$
$$k = \frac{1}{\delta} log(\frac{2}{\alpha} - 1)$$。 -->

因此本文使用训练策略(evolution training strategy)去确定$\alpha$。因此我们使用L2-正则化去约束和调整$\alpha$

$$\min _{\alpha} \mathcal{L}(\alpha ; x, y) \quad \text { s.t. }\|\alpha\|_{2}<\lambda$$

$$\frac{\partial y}{\partial \alpha}=\left\{\begin{array}{ll}{0,} & {x<l} \\ {0,} & {x>u} \\ {\frac{\partial Q_{S}(x)}{\partial \alpha},} & {x \in P_{i}}\end{array}\right.$$

### 平衡裁剪误差和舍入误差(balance clipping error and rounding error)

剪切和舍入会导致量化误差。通常情况下，当量化器剪切量越大，剪切误差越大，舍入误差越小。由于DSQ向标准量化器的演化是可微的，因此我们可以进一步分析DSQ中剪切误差和舍入误差之间的关系。具体来说，我们可以共同优化裁剪的下界和上界，在裁剪误差和舍入误差之间寻求平衡。

![](https://i.loli.net/2019/10/17/APvO5ZDouaXj8IB.png)

可以从此式子中看出，较大的离群点被u裁剪，主要贡献于u的更新，较小的离群点被l裁剪，主要贡献于l的更新。落在中间区间的数据店会影响u和k的倒数。当有裁剪误差主导整个量化时（离群的多）是权重更新的主要动力。否则，当舍入误差大于误差时，在反向传播过程中，中间区间的点影响更大。

### 训练与部署

本文提出了一种基于进化训练的DSQ函数，对DSQ和网络参数进行优化，旨在从全精度网络中对量化网络进行微调。算法1列出了卷积网络的具体调优过程

![算法1](https://i.loli.net/2019/10/17/WPT2c9tuLligXCw.png)

为了能在移动端运行本文还实现了在ARM上的低比特计算推断计算内核。

法和累加是通用矩阵乘法(GEMM)的核心运算，通过ARM NEON上的MLA指令可以高效地完成。MLA在8-bit的寄存器中乘两个数，并将结果累加到一个8-bit的寄存器。如果加法器溢出，我们将结果转移到16-bit寄存器中。
![GEMM](https://i.loli.net/2019/10/17/nykbsKNxpo6JlCt.png)

转移到SADDW中需要额外的成本，但是本文可以减少它的发生。图一展示了调用MLA(8位寄存器)和(16位寄存器)的时间比率相对于不同数量的量化位。

![Table1](https://i.loli.net/2019/10/17/zwv8LxmSJIREriP.png)

## 实验

使用的数据集 CIFAR-10和ImageNet(ILSVRC12)/

### Settings

平台：Pytorch
网络：
+ VGG-small、ResNet-20（CIFAR-10）
+ ResNet18，34，MobileNetV2（ImageNet）

初始化：使用预训练模型。
参数$\alpha$,我们选择0.2作为一个初始值。对于裁剪值l和u，我们尝试了以下两种策略:移动平均统计和反向传播优化。

### DSQ的分析

#### Rectification

DSQ函数的一个重要作用是重新分配数据并将它们与量化值对齐，从而减少了反向传播的误差。为了研究这一点，在图5中，我们可视化了2-bitDSQ函数之前和之后，ResNet-20在CIFAR-10上的权值s分布。从图中可以看出，经过DSQ 校正后，原本与正态分布相似的数据分布(图5(a))在直方图中出现了几个峰值(图5(b))，经过符号函数处理后，数据可以完全量化为4个量化点(图5(c))。这一观察结果证明，在实践中大大降低了量化损失。

![](https://i.loli.net/2019/10/17/OphYAKHG7l9wLxm.png)

#### Convergence

最先进的二值/均匀量化网络通常采用直接在正向传播过程中应用量化，而在反向过程中使用STE的训练策略。它们忽略了量化损失对梯度计算的负面影响，因而在大多数情况下往往面临不稳定训练的问题。
随着DSQ的重新分布，量化数据与全精度数据之间的数值差值减小了，从而使得反向传播的精度提高。从另一个角度来看，DSQ的引入可以看作是STE的优化器，可以提高优化过程中的收敛能力。图6对比了在CIFAR-10上使用VGG-Small和在ImageNet上使用ResNet-34上使用3-bit均匀量化时使用DSQ和不使用DSQ时验证的精度曲线。我们可以发现，使用DSQ进行训练可以获得更高的准确性

![](https://i.loli.net/2019/10/17/U8OaeKAVbRuQ5qr.png)

#### Evolution

将$\alpha$的初始值设定为0.2然后范围设定在$(0, 0.5)$，图7是

![图7](https://i.loli.net/2019/10/17/qUEjiF5T4pkAbzX.png)

我们可以看到,一开始的训练,$\alpha$将急剧增加，使量化现象。之后,α逐渐减少,最后收敛于一个稳定值,这使得DSQ近似量化的标准。在整个训练过程中,$\alpha$自动调整，比手动调节更灵活。

![表2]](https://i.loli.net/2019/10/17/idOaXY9D3UplmtI.png)

有图我们可以看出，权值的$\alpha$比激活值的$\alpha$更小，这意味着在低比特量化网络中，对比激活值，权值通常对量化更有容忍度。也就是说激活值一般比较敏感。不同层的$\alpha$说明不同层对量化敏感不同。这一结论对理解和改进网络量化有重要意义

### Ablation study


![](https://i.loli.net/2019/10/17/nBjwDpSN2WzIVva.png)


![](https://i.loli.net/2019/10/17/nDfuaSwybg4EX7q.png)


### Comparison with State-of-the-arts

![二值量化](https://i.loli.net/2019/10/17/89CTyWzoZqhnsiw.png)

![多bit量化](https://i.loli.net/2019/10/17/mkR3HOhfMXGZYzQ.png)

### Deploying Efficiency

本文做实现支持基于GEMM内核和ARM NEON 8位指令的超低位(小于4位)整数运算，而现有的开源高性能推理框架(如ncnn)通常只支持8位运算。在实践中，较低的位宽并不意味着更快的推理速度，这主要是由于如3.5节所分析的寄存器之间的溢出和传输。但幸运的是，如表8所示，我们的实现可以加速推理，即使使用最低位。我们还测试了在Raspberry Pi 3B上使用DSQ对ResNet-18进行量化时的实际执行速度。如表9所示，使用DSQ的推理速度要比使用NCNN的推理速度快得多。

![推理速度](https://i.loli.net/2019/10/17/Mu43NRdQjEFmaYp.png)