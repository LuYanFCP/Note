## BN

1. 解决的问题Internal Covariate Shift。（在深层网络训练的过程中，由于网络中参数变化而引起内部结点数据分布发生变化的这一过程被称作Internal Covariate Shift。）
   1. 上层网络需要不停调整来适应输入数据分布的变化，导致网络学习速度的降低
   2. 容易进入饱和区，现在已经使用ReLu去避免了。
2. 如何解决这个问题
    1. 白化->PCA白化（means=0, std=1），ZCA白花(means=0, std一致).同分布，去除相关性。
    2. 但是白化成本高
    3. 白化改变每一层的分布导致，底层网络学习到的参数信息会被白化操作丢失掉。

3. 如何解决白化成本高的问题
   1. 对每一个特征进行normalization，均值0，方差1
   2. 白化操作减弱了网络中每一层输入数据表达能力，那我就再加个线性变换操作，让这些数据再能够尽可能恢复本身的表达能力就好了。$\gamma$和$\beta$
![BN算法](https://i.loli.net/2019/10/22/OUDLkHzG1qAIPyY.png)
4. 测试时如何BN
   1. 测试时数据集，数据集少$\mu$和$\sigma^2$一定会有偏估计。因此保留训练时候每一个$\mu_{batch}$和$\sigma^2_{batch}$，然后test的方差使用:
   $$\begin{array}{l}{\mu_{t e s t}=\mathbb{E}\left(\mu_{b a t c h}\right)} \\ {\sigma_{t e s t}^{2}=\frac{m}{m-1} \mathbb{E}\left(\sigma_{b a t c h}^{2}\right)}\end{array}$$
    2. 另外，除了采用整体样本的无偏估计外。吴恩达在Coursera上的Deep Learning课程指出可以对train阶段每个batch计算的mean/variance采用指数加权平均来得到test阶段mean/variance的估计。













参考资料
------
https://zhuanlan.zhihu.com/p/34879333