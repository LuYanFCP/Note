场景：低速的设备，主要强调推理速度和准确度

问题1： 激活量化时出现的问题：ReLU输出没有界限，这以为着量化需要较大的输出范围（更大位宽）。当位宽有限时，就会出现很多问题。训练误差急剧上升。如图
![](https://i.loli.net/2019/10/26/AMEf23Qlg9dpI7i.png)
过去使用截断（clipping）去解决这个问题。效果比不使用好一些，但是还是达不到要求。

如何解决问题1: 参数化截略式激活（PArameterized Clipping acTivation, PACT） 讲传统的ReLU改造为PACT ReLU

![PACT-ReLu](https://i.loli.net/2019/10/26/n715DHoLdEprbFB.png)

PACT-ReLU的收敛效果：
![](https://i.loli.net/2019/10/26/ahPHKeL2rEp9JsC.png)

有了$\alpha$还要注意其大小的权衡，如果$\alpha$太大了则需要量化位宽，因此需要让$\alpha$和量化位宽做有个权衡。其方法是基于输出与目标的相近程度来调整输出的范围，即如果目标输出有较大的幅度，PACT 会调整到更高的$\alpha$值.截略误差和量化误差都会使输出偏离目标，PACT 会在训练期间增大或降低输出范围，以尽力最小化这两个误差。

![](https://i.loli.net/2019/10/26/RnN6ShcQszabJC2.png)

在图4(a)中可以更好地观察到剪裁和量化误差之间的平衡，图中显示了CIFAR10 ResNet20在不同剪裁级别的训练中，剪裁和2位量化的归一化均方误差。这个图解释了为什么ReLU网络和裁剪激活函数在激活量子化时没有收敛;ReLU存在较大的量化误差，而剪裁激活函数存在较大的剪裁误差。这增加了找到一个适当的裁剪级别来平衡裁剪和量化的负担

亮点2：提出了新的权重的量化方法。tatistics-aware weight
binning (SAWB)。
主要的思想是：
1. 依赖权值分布。借助对称均匀量化（硬件友好）。

