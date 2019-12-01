## 最邻近点搜索问题

在尺度空间M中给定一个点集$S$和一个目标点$q ∈ M$，在S中找到距离$q$最近的点。

## Vector quantization

基本定义： VectorQuantization (VQ)是一种基于块编码规则的有损数据压缩方法。它的基本思想是：将若干个标量数据组构成一个矢量，然后在矢量空间给以整体量化，从而压缩了数据而不损失多少信息。

VectorQuantization的聚类中心成为码矢(code vector)，可以同样保存成码矢的区域称为(encoding regions)，码矢的集合成为码书(code book)。

VQ问题：给定一个已知统计属性的矢量源（也就是训练样本集，每一个样本是一个矢量）和一个失真测度。还给定了码矢的数量（也就是我们要把这个矢量空间划分为多少部分，或者说量化为多少种类），然后寻找一个具有最小平均失真度（数据压缩，肯定是失真越小越好）的码书和空间的划分。

设定原来的矢量为m维度

$$Xi = (x_{i1}, x_{i2}, x_{i3} ... x_{im})$$

设定码矢的数量为n，codebook集合为$C = (c_1, c_2, c_3...c_n)$，码矢的k维矢量为$c_n = (c_{n,1}, c_{n,2}, c_{n,3}...c_{n,k})$，码矢对应的编码区域为Sn，将空间划分为: $P={S_1, S_2...S_n}$。

如果源矢量$x_m$在$S_n$内，那么它的近似(Q(xm)表示)就是$c_n$
则失真度量为
$$D_{ave} = \frac{1}{mk} \sum_{i=1}^{m} ||x_m - Q(x_m)||^2$$

#### 优化条件

1. 最邻近条件(Nearest NeighborCondition)：区域里面都里码矢近
2. 质心条件(Centroid Condition): 这个条件要求码矢$c_n$编码区域$S_n$内所有的训练样本向量的平均向量。在实现中，需要保证每个编码区域至少要有一个训练样本向量，这样上面这条式的分母才不为0。


定义`q`为D维度矢量$x\in R^D$ 到另外一个矢量$q(x) \in c = {c_i;i\in L}$的映射，$c_i$称为`centriods`也可以称为`codeword`, 质心，其中C称为codebook大小为k。



### Lloyd optimality conditions（劳埃德最优条件）:

+ vector x 一定被量化到与它最近的质心
+ 所有的Voronoi cell被超平面分割

这样通过聚类的方式，将原vector量化到了k和Voronoi cell，每个cell内的值由质心 $c_i$ 来代表，index花费 $log2k$ 这么大的存储空间。

### Product quantizers

先把input vector x 拆分为m个互斥的subvectors， PQ便可以表示成为如下所示：并对分解得到的低维向量空间分别做量化，那如何对低维向量空间做量化呢？恰巧又正是用kmeans算法。所以换句话描述就是，把原始，PQ算法相当于对原始向量的每一维都用kmeans算出码本。



#### other

其实PQ算法可以理解为是对vector quantization做了一次分治，首先把原始的向量空间分解为m个低维向量空间的笛卡尔积，


## 参考
> https://www.jiqizhixin.com/graph/technologies/2ece0beb-329e-4700-87b9-92af8d21d2b7
> https://zhuanlan.zhihu.com/p/36675549
> https://www.cnblogs.com/mafuqiang/p/7161592.htmle
> https://blog.csdn.net/liangjiubujiu/article/details/88833069
> http://blog.pluskid.org/?p=57
> http://www.fabwrite.com/productquantization
> http://www.fabwrite.com/productquantization