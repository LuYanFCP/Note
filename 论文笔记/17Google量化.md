## Intruduction
由于之前的模型都过于关心acc，例如VGG，而很少关心模型的大小和计算的速度。另方面CNN模型有需要部署到例如智能手机，AR/VR等，设备计算力弱且有内存限制的设备上部署。

现在解决这个问题的主要有两个方向。第一个方向是诸如MobileNet、SqueezeNet、shuffleNet、DenseNet 通过设计更好的网络结构去加速网络推断和减少内存占用。第二种注入量化权值或者激活值从FP32 量化至低bit的一个表达。这个方法广泛使用在TWN，BNN，XNOR-net等等。尽管现有的量化方法数量众多，但在精确地权衡延迟方面，它们在两个方面存在不足

第一、缺少一个baseline，大多数工作都压缩的是冗余较多的AlexNet，VGGnet、googleNet，这些网络有很多冗余设计，在这些网络上实验主要是去验证理论。另方面诸如MobileNet主要是去量化机构

第二、许多量化在真实的硬件平台上无法达到效果。一些工作只关心压缩体积，不关心推断速度。另外一些方法需要特定且昂贵的设备。

## Quantized Inference
### 量化方案
首先记$r$为真实值，$q$为已经被量化的值。本方法使用整数推断，浮点数训练。

我们的方案的基本要求是所有操作都用整数进行。这个这相当从$r->q$的仿射。
$$r=S(q-Z)$$
其中$S$和$Z$是量化参数，在整个过程都是用单一的一组参数。
1. S是范围（scale）是一个正数，跟$r$一样为浮点数
2. Z是表示零点（zero-point）它与$q$的类型一致，表示$r=0$时量化值的大小
使用C++来表示改数据结构
```c++
// 如果是 float -> int8，则QType=uint8
template<typename, QType>
struct QuantizaedBuffer {
    vector<QType> q;
    float S;
    QType Z;
}
```

### 只用整数的矩阵乘法（Integer-arithmetic-only matrix multiplication）
基本的两个真实值相乘为$r1*r2 = r3$，在矩阵中我们设置矩阵的每一个数字为$r_a^{i, j}$其中$a = 1, 2, 3， i,j \in [1, N]$对于每一个真实值
$$r_{\alpha}^{(i, j)}=S_{\alpha}\left(q_{\alpha}^{(i, j)}-Z_{\alpha}\right)$$
我们定于矩阵乘法
$$S_{3}\left(q_{3}^{(i, k)}-Z_{3}\right)=\sum^{N} S_{1}\left(q_{1}^{(i, j)}-Z_{1}\right) S_{2}\left(q_{2}^{(j, k)}-Z_{2}\right)$$
$$q_{3}^{(i, k)}=Z_{3}+M \sum_{j=1}^{N}\left(q_{1}^{(i, j)}-Z_{1}\right)\left(q_{2}^{(j, k)}-Z_{2}\right)$$
其中M为
$$M:=\frac{S_1 S_2}{S_3}$$
在整个运算式子中M是唯一的浮点数，而且它还是常数，可以离线计算。**通过实验发现，M的大小一般都在(0,1)之间，因此我们又可以把M的表达式写成如下这样子**
$$M=2^{-n} M_0$$
其中$M_0$的范围是[0.5-1]是一个非负整数，可以表示为定点数。 实现可以使用定点乘法由于$2^{-n}$是可以用移位的方式计算的。

### 有效处理零点

为了更快运算，我们将上式继续运算
$$\begin{array}{r}{q_{3}^{(i, k)}=Z_{3}+M\left(N Z_{1} Z_{2}-Z_{1} a_{2}^{(k)}\right.} \\ {\left.-Z_{2} \overline{a}_{1}^{(i)}+\sum_{j=1}^{N} q_{1}^{(i, j)} q_{2}^{(j, k)}\right)}\end{array}$$
其中
$$a_{2}^{(k)} :=\sum_{j=1}^{N} q_{2}^{(j, k)}, \overline{a}_{1}^{(i)} :=\sum_{j=1}^{N} q_{1}^{(i, j)}$$

这两个的需要$2N^2$次乘法，其余的计算量主要集中在后面核心整数矩阵乘法累加。将问题简化为与我们在任何其他无零点量化方案中计算相同的核心整数矩阵乘法累加。

### 实现特殊的层的融合（Implementation of a typical fused layer）
进一步要将bias-addition和activation function都融入到了量化乘法中。由于我们必须在推理和训练使用一样的代码，因此推理代码中融合运算符的粒度(接受8位量化输入并生成8位量化输出)必须匹配训练图中“伪量化”运算符的位置。


-------
差一张图
-------


本文使用`google`的`gemmlowp`进行实现，它提供本文的操作

设$q1$是权值矩阵，$q2$是activation矩阵。两者都是`uint8`,其乘法需要32-bit的加法器（有符号），因此矩阵的乘法的形式为
$$int32 += uint8*uint8$$
为了使量化的偏置加法变成int32累加器中int32偏置的加法，`bias`使用`int32`进行量化，它使用0作为量化零点，他的量化范围为$S_{bias} = S_1S_2, Z_{bias} = 0$与加法器一样为int32的范围。

虽然bias是int32，但是在整个参数中他占比很少，并且它可以保证精度（由于每个偏置向量都被添加到许多输出激活中，偏置向量中的任何量化错误都倾向于充当总体偏置）。

之后还有三个重要的事
1.  scale down to the final scale used by the 8-bit output activations
2.  cast down to uint8 and apply the activation function to yield the final 8-bit output activation.

down-scaling ：这个操作对应着之前操作中的$M$，它是由乘法器$M0$h和一个移位器实现的，然后我们把他映射到uint8。

我们使用的activation function主要是clamps例如ReLU、ReLU6之类的。因此，我们的融合激活函数需要做的惟一一件事就是在存储最终的uint8输出激活之前，将uint8值进一步固定到某个子区间$[0,255]$。

**这里可以多考虑考虑**

## 量化训练

传统方法：浮点训练，训练完再量化之后微调。

我们发现，这种方法对于具有相当大的代表性的`过参数模型`非常有效，但是对于小型模型却会导致显著的精度下降。

传统方式的缺点：

1. 每一个通道参数的大小都不同，如果使用统一的量化，会导致较大的误差。
2. 异常值（outlier weight values）问题。异常值会降低量化精度。

本文使用伪量化操作，使得正向和反向操作都是fp32，所以它减少异常值的影响。在前向传播时，在推断时需要量化的地方，插入伪量化操作。

1. 权值在conv之前就行量化，如果有BN的话则在量化前将批量归一化参数folded into到权重中。
2. activation在推理过程中会被量化，例如激活函数应用于卷积或全连接层的输出之后，或旁路连接将多个层的输出添加或连接在一起之后(在ResNets中)

注：这里的biases没量化主要源于已经表示为int32

伪量化操作
$$\begin{aligned} \operatorname{clamp}(r ; a, b) & :=\min (\max (x, a), b) \\ s(a, b, n) & :=\frac{b-a}{n-1} \\ q(r ; a, b, n) & :=\left\lfloor\frac{\operatorname{clamp}(r ; a, b)-a}{s(a, b, n)}\right] s(a, b, n)+a \end{aligned}$$

其中$[a;b]$是量化的范围（quantization range），$n$是quantization levels（比如说8-bit的量化n=2^8=25），上下那个符号是最接近的整数,$n$所以层都是固定的。

**这个过程是先量化再还原**

### Learning quantization ranges

权重量化和激活量化对量化范围的处理不同:

+ 对于权值，$a:=min w, b:=max w$ 此处我们做出了一个小小的改进去掉[-128, 127]中的-128这样能更好。
+ 对于激活值为了估计范围，我们收集了[a;b]在训练过程中观察到的活动范围，**然后通过指数移动平均线(exponential moving averages， EMA)**在训练中去统计这个量化范围，使平滑参数接近1，从而使观察到的范围在数千个训练步骤中变得平滑。

EMA: 若范围快速变化时，指数移动平均会延迟反映出来，所以在训练初期（5万步到200万步）时，不量化activation是有用的。

给出训练一般过程算法

![](https://i.loli.net/2019/10/31/tcUnC28YQZBTbMr.png)

整个

![](https://i.loli.net/2019/10/31/vhdJj3o7bP8AOmF.png)

### BN folding （之前提到的BN融入w）

$$w_{\text {fold }} :=\frac{\gamma w}{\sqrt{E M A\left(\sigma_{B}^{2}\right)+\varepsilon}}$$ 

BN的另一部分参数在$\beta-\gamma \mu / \sigma$中。

其中$\gamma$是BN的范围参数，$E M A\left(\sigma_{B}^{2}\right)$是使用EMA得到的方差。

原始的BN训练与推断。



使用了folded无量化模型


![](https://i.loli.net/2019/10/31/UqyNsw1WnEZQYk6.png)

其中没有bias， （一个合格的BN是不需要bias的 😀）

![](https://i.loli.net/2019/10/31/fCmHBw9ygJQ1Rn7.png)

量化的模型

## 实验

两个判断参数

1. 量化效率
2. 在通用硬件上改进量化模型的 latency-vs-accuracy trade-off

GEMM推断使用的 `gemmlowp`实现8-bit整数推断，`Eigen` 32-bit浮点数的推断

实验使用ResNet和InceptionV3

在resnet的上的表现

![](https://i.loli.net/2019/10/31/ngwtyifMhPIvLxp.png)

在InceptionV3上的表现

![](https://i.loli.net/2019/10/31/OfGyzUhgWYS2AJZ.png)

7位量化训练的模型精度接近于8位量化训练，而ReLU6量化模型的精度下降较小， ReLU6可以提供固定区间，更容易量化（ReLU的没有区间约束各个clannel的解决范围不同）

---------------------------------------------------------以下主要是对MobileNet的讨论--------------------------------------------------------------------
### MobileNet的量化

MobileNet是一类实现了一个权衡设备延时和ImageNet分类误差的网络。以下将继续讨论其量化方面的权衡

使用的平台为 1) Qualcomm Snapdragon 835 LITTLE core、2) Snapdragon 835 big core和2)Snapdragon 821 big core

在相同的运行条件下，只对整数进行量化的MobileNets比浮点的MobileNets具有更高的精度

![](https://i.loli.net/2019/10/31/dwHVcbjxPu3sADT.png)

### COCO上的表现

mobile-SSD

![](https://i.loli.net/2019/10/31/yr5qVXKSIYxf4J1.png)

量化MobileNet-SSD在COCO目标检测任务上，时间减少50%，精度下降1.8%;

MobileNet-SSD在人脸数据集上的表现

![](https://i.loli.net/2019/10/31/Lbu9Ul8sB6R3KA4.png)

量化Mobile SSD在人脸检测任务上，精度下降2%，耗时下降接近一半，四核加速1.5~2.2倍：

