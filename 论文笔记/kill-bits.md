## 信息

+ 论文：https://arxiv.org/abs/1907.05686 (ICLR2020)
+ 代码复现：https://github.com/facebookresearch/kill-the-bits

## 亮点

+ 使用不需要标注的数据(降低了成本)
+ 关注restructed error (以往的量化都是只关心weight能否恢复，而这篇文章的立意在与关注，是否能恢复激活值)

## 一些缺点

1. 结构化量化（structed quantization）推理上很麻烦，没有现成的实现。


## 核心

+ 关注feature-map而不是weight, 降低量化后的`restruct error`.
+ 使用类似`Deep Compression`中的`structed quantization`方法，使用的是codebook+indexMatrix方式存储。（这里使用 product quantization去优化）
+ 使用蒸馏对`codebook`进行微调（蒸馏的teacher 网络是全精度网络，student网络是量化网络）
+ 所有层量化完了之后需要对整体做微调。（很关键）

## 具体步骤

### 大体的思路

逐步量化每一层，量化使用的输入是

### fc层的量化

1. 将权重矩阵w以列为单位，将每一列分成$m$个`subvector`，`vector`的维度为$d$，然后每一个`subvector`对应着一个`codebook` $C$ 其中的维度为`k`每一个$d$的单元。因此`codebook`的大小为$k^m$
2. 由于关注的是`output activation`和`restructions`因此，目标函数为$\|\mathbf{y}-\widehat{\mathbf{y}}\|_{2}^{2}=\sum_{j}\left\|\mathbf{x}\left(\mathbf{w}_{j}-\mathbf{q}\left(\mathbf{w}_{j}\right)\right)\right\|_{2}^{2}$

步骤:
1. 将输入的形式由$B \times C_{in}$变成$\mathbf{x}$它的大小为$(B \times m) \times d$
2. 然后使用EM算法：
   1. E-step(cluster assignment): 将每一个$w_j$分割成m个维度为d的向量，每一个向量v指定为一个codeword $c_j$ 它的定义为$\mathbf{c}_{j}=\underset{\mathbf{c} \in \mathcal{C}}{\operatorname{argmin}}\|\widetilde{\mathbf{x}}(\mathbf{c}-\mathbf{v})\|_{2}^{2}$
   2. M-step(codeword update): 然后更新`codebook` $c <- c^*$
    $$\mathbf{c}^{\star}=\underset{\mathbf{c} \in \mathbf{R}^{d}}{\operatorname{argmin}} \sum_{p \in I_{\mathbf{c}}}\left\|\widetilde{\mathbf{x}}\left(\mathbf{c}-\mathbf{v}_{p}\right)\right\|_{2}^{2}$$


### conv层的量化

conv的weight主要都是4D-张量，因此使用一些reshape的方法，现将weight从 $C_{out} \times C_{in} \times K \times K$变成$(C_{out}, C_{in} \times K \times K)$ 然后使用与FC层相同的量化方法

![Selection_002.png](https://i.loli.net/2019/12/01/KXwoaPL2nHMSpmx.png)

### Netword Quantization

从低层向高层量化（从到尾）。


#### Learning the codebook

恢复了该层当前的输入激活，即通过量化的低层转发一批图像得到的输入激活。而不是教师网络的激活。**当使用未压缩网络的激活而不是当前激活时，测量误差和分类误差都有漂移。（之后可以复现）**

#### Finetuning the codebook

使用未压缩网络为教师网络，使用（到当前层）的老师网络为学生网络去finetune codebook。

y_t -> teacher 网络的结果（概率）
y_s -> student 网络的结果（概率）

$$L = KL(ys, yt)$$

使用此作为优化的loss函数，对codeword的微调方法是对分配给每个子向量的梯度求平均值。然后使用SGD：

![20191201164259.png](https://i.loli.net/2019/12/01/aieyJTdSUKItpX6.png)

这种方法的效果优于直接用Label去训练。（一种可能的解释是，来自教师网络的监督信号比作为监督学习中的传统学习信号的向量更丰富）

## 全局训练

最后进行全局的finetune codebook，这个时候需要将BN解冻（BN在次过程中要添加统计的信息）。


## 实验

条件：16GB v100

large block size(small): 

+ conv 3x3 ->> d=9(d=18) 
+ conv 1x1 ->> d=4(d=8)
+ k = {256, 512, 1024, 2048}
+ $centriods = min(k, C_{out} \times m/4 )$

### sample input

在对每一层进行量化之前，我们随机抽取一批1024张训练图像，获取当前层的输入激活，并按照conv量化所述对其进行整形。然后，在我们的方法的每个迭代(E+M步骤)之前，我们从那些重新构造的输入激活中随机抽取10,000行。

### 超参

each layer finetune 2500iter(batchsize=128/64 Resnet18/50)

LR = 0.01

weight decay 1e-4, momentum=0.9

### 实验结果

![20191201171046.png](https://i.loli.net/2019/12/01/pJtd1uCWahiSQ7r.png)

![20191201171114.png](https://i.loli.net/2019/12/01/DFf5tNaHxSnX3ic.png)

#### 消溶实验

![20191201171409.png](https://i.loli.net/2019/12/01/on7tixfMj5WNCph.png)

证明了 激活约束（restruct）和 distiller的有效性。

## other

+ 存储激活的内存可以忽略不记， 首先在现实的实时推断中，batch的大小基本等于1；其次正想传递只需要存储当前层的激活，通常小于输入的大小，而不是整个网络的激活。