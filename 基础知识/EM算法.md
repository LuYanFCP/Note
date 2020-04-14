# EM算法笔记

> 最近又接触了EM算法，很多时候自己只会用而不知道为什么，因此这次使用的时候，又回头多看了看

EM算法应用场景: 解决有隐变量的的概率模型的参数的极大似然估计。

首先第一个问题：什么是隐变量？

## 隐变量

> 不能被直接观察到，但是对系统的状态和能观察到的输出存在影响的一种东西。指的是不可观测的随机变量。潜变量可以通过使用数学模型依据观测得的数据被推断出来。

概率模型有时既含有观测变量(observable variable)，有含有隐变量或者潜在变量(latent variable)。

比如在高斯混合模型中，从混合模型角度来看，$z$这个随机变量表示对应的样本$x$属于哪一个高斯分布，它是一个离散分布，满足$\sum_{i=1}^{K}p_{z_i}=1$，其中$z$有$k$个取值，但是在实际的数据采用过程中，我们并不能从数据中观测到$z$这个随机变量，而只能观测到$x$这个变量，这个$z$就是隐变量。

**隐变量的出现导致了带来了什么问题？**

隐变量的出现会导致在构造MLE的L的时候引入一些隐变量的参数，导致整个L没有解析解。

举例：

1. GMM的MLE
按照上面的例子对GMM的MLE进行推导

$$
\begin{aligned}
L &= log(p(x)) = log(\prod_{i=1}^{N} p(x_i)) \\
  &= \sum_{i=1}^{N} log(p(x_i)) \\
  &= \sum_{i=1}^{N} log(\sum_{k=1}^{K} p_{k}N(x_i|\theta_k))
\end{aligned}
$$

由于$log(a+b+c)$这种式子很难找到解析解。因此求解困难。

2. 三硬币模型（来自统计机器学习）

假设有3枚硬币A、B、C，每个硬币正面出现的概率是π、p、q。进行如下的掷硬币实验：先掷硬币A，正面向上选B，反面选C；然后掷选择的硬币，出正面记1，出反面记0。独立的进行10次实验，结果如下：1，1，0，1，0，0，1，0，1，1。假设只能观察最终的结果（只知道最后0还是1的结果），而不能观测掷硬币的过程(不知道A的正反情况，也就是不知道选B还是C)，问如何估计三硬币的正面出现的概率？

记观测变量为$y$，随机变量$z$为无法观测到的隐变量，即A的投币情况，$\theta=(\pi, p, q)$是模型参数，则分布可写为:

$$P(y|\theta)=\sum_{z}P(y, z|\theta)=\sum_{z}P(y|z\theta)P(z|\theta)=\pi p^y (1-p)^{1-y} + (1-\pi) q^y (1-q)^{1-y}$$

将观测数据$Y=(Y_1,Y_2,Y_3,...,Y_n)^T$，未观测数据表示$Z=(Z_1, Z_2,...,Z_n)^T$，则观测函数的似然函数：
$$
P(Y|\theta)=\sum_{z} P(Z|\theta)P(Y|Z,\theta)
$$
即
$$
P(Y|\theta) = \prod_{j=1}^{n}[\pi p^y (1-p)^{1-y} + (1-\pi) q^y (1-q)^{1-y}]
$$
则根据极大似然估计

$$
\hat{\theta} = \argmax_{\theta} logP(Y|\theta)
$$

由$P(Y|\theta)$表达式可知，其在使用$logP(Y|\theta)$求导之后等于0的时候没有解析解。因此只能通过迭代的方式进行逼近。这就引入了EM算法，EM算法就是用来解决此问题的高效迭代方法。

## EM算法

一般称$Y$表示观测随机变量的数据，$Z$表示隐变量的数据，$Y,Z$为完全数据（complete-data），$Z$为不完全数据（incomplete-data）。

EM算法的核心是通过迭代的方式在含有隐变量的情况下求出$L(\theta) = logP(Y|\theta)$的极大似然估计，包含两部E步和M步。

首先不看EM算法首先看EM算法的导出。究竟EM算法是如何解决$logP(Y|\theta)$没有解析解的问题。

### EM的导出

根据上面的分析，我们知道EM没有解析解，因此不能一下着就拿到最值，因此我们采用迭代逼近的方式进行求解。例如使用梯度上升或者牛顿法等方式，但这个方式有个问题就是$logP(Y|\theta)$本身的梯度或者说导数，并不好求解，因此EM算法首先通过Jensen不等式找到了$logP(Y|\theta)$的下界。

#### 找到$logP(Y|\theta)$的下界

$$
\begin{aligned}
L(\theta) = logP(Y|\theta) &= log(\sum_{Z} P(Y, Z|\theta)) \\

&= log(\sum_{Z} P(Z|Y, \theta^{t})\frac{P(Y, Z|\theta)}{P(Z|Y, \theta^{t})})\\

& \geq \sum_{Z} P(Z|Y, \theta^{t}) log(\frac{P(Y, Z|\theta)}{P(Z|Y, \theta^{t})})
\end{aligned}
$$

其中中间的不等式变换又Jensen不等式得到。我们令$B(\theta, \theta^{t}) = \sum_{Z} P(Z|Y, \theta^{t}) log(\frac{P(Y, Z|\theta)}{P(Z|Y, \theta^{t})})$则$logP(Y|\theta) \geq B(\theta, \theta^{t})$。

另外观察到:
$$
\begin{aligned}
B(\theta^{t}, \theta^{t}) &= \sum_{Z} P(Z|Y, \theta^{t}) log(\frac{P(Y, Z|\theta^{t})}{P(Z|Y, \theta^{t})} \\
&=\sum_{Z} P(Z|Y, \theta^{t}) log(\frac{P(Y|\theta^{t})P(Z|Y,\theta^{t})}{P(Z|Y,\theta^{t})} \\
&=\sum_{Z} P(Z|Y, \theta^{t}) logP(Y|\theta^{t}) \\
&=P(Y|\theta^{t})
\end{aligned}
$$

我们使用迭代算法的目的是将$L(\theta^t)$逐步的逼近最大的$L(\theta)$因此两者的关系还有$L(\theta) > L(\theta^t)$。由上式可得任何可以让$B(\theta, \theta^{t})$增大，都能让$L(\theta)$增大，为了能让$L(\theta)$尽可能的大，选择$\theta^{t+1}$使得$B(\theta, \theta^{t})$达到极大，则:

$$
\begin{aligned}
\theta^{t+1} &= \argmax_{\theta} B(\theta, \theta^{t}) \\
&= \argmax_{\theta}{\sum_{Z} P(Z|Y, \theta^{t}) log(\frac{P(Y, Z|\theta)}{P(Z|Y, \theta^{t})}} \\
&= \sum_{Z} P(Z|Y, \theta^{t}) logP(Y, Z|\theta)\\
&= \mathbb{E}_{Z|X,\theta^t}[logP(X,Z|\theta)]\\
\end{aligned}
$$

记$\mathbb{E}_{Z|X,\theta^t}[logP(X,Z|\theta)]$为$Q(\theta, \theta^t)$，也就是EM算法的核心`Q-function`。

**Q函数的定义：完全数据的对数似然函数$logP(Y,Z|\theta)$关于给定观测的数据$Y$和当前参数$\theta^{t}$下对未观测数据$Z$的条件概率分布$logP(Z|Y,\theta)$的期望称为Q函数。**

则EM算法的过程为：

初始化：选择参数$\theta^{0}$对初始化值进行初始化

1. E-step: 计算$Q(\theta, \theta^t)$
2. M-step: 计算$\theta^{t+1} = \argmax_{\theta} Q(\theta, \theta^t)$

重复1，2直到收敛。一般设定迭代次数或者$|\theta^{t+1}-\theta^{t}| < \epsilon$作为停止条件。

EM算法的性质：由于EM算法要设置初值，因此EM算法对初值有一定的敏感性。

## EM算法收敛证明

定理1：设$P(Y|\theta)$为观测数据的似然函数，$\theta^{t}$为EM算法得到的参数估计序列，$P(Y|\theta^{t})$对应的似然函数序列，则$P(Y|\theta^{t})$是单调递增的，即$P(Y|\theta^{t+1}) \geq P(Y|\theta^{t})$

证明:

$$
\begin{aligned}
P(Y|\theta^{t}) &= \log P(Y, Z|\theta)-\log P(Z|Y, \theta) \\
&=\sum_{z} \log P(Y, Z | \theta) P\left(Z | Y, \theta^{t}\right) - \sum_{Z} \log P(Z | Y, \theta) P\left(Z | Y, \theta^{t}\right) \\ 
&= Q\left(\theta, \theta^{t}\right) -\sum_{Z} \log P(Z | Y, \theta) P\left(Z | Y, \theta^{t}\right)
\end{aligned}
$$

令

$$
H\left(\theta, \theta^{t}\right)=\sum_{Z} \log P(Z | Y, \theta) P\left(Z | Y, \theta^{t}\right)
$$
则

$$
P(Y|\theta^{t}) = Q\left(\theta, \theta^{t}\right) - H\left(\theta, \theta^{t}\right)
$$

由上我们知道$Q\left(\theta^{t+1}, \theta^{t}\right) > \left(\theta^{t}, \theta^{t}\right)$

另外对于$H\left(\theta, \theta^{t}\right)$有如下关系：

$$
\begin{aligned}
H\left(\theta^{t+1}, \theta^{t}\right) - H\left(\theta^{t}, \theta^{t}\right) & = \sum_{Z} [\log P(Z|Y, \theta^{t+1}) - log P(Z|Y, \theta^{t})] P\left(Z | Y, \theta^{t}\right) \\
&= \sum_{Z} \log [P(Z|Y, \theta^{t+1})/P(Z|Y, \theta^{t})] P\left(Z | Y, \theta^{t}\right) \\
&= -D_{KL}(P(Z|Y,\theta^{t})||P(Z|Y,\theta^{t+1}))
\end{aligned}
$$

由于KL散度是非负的因此$H\left(\theta^{t+1}, \theta^{t}\right) - H\left(\theta^{t}, \theta^{t}\right) \leq 0$

因此$P(Y|\theta^{t})$为递增得证。因此使用EM算法可以将$P(Y|\theta^{t})$ 收敛。

## EM算法的应用

EM算法最核心的就是在无监督或者弱监督下的学习算法，其核心是因为在无监督的条件下，我们拿到的数据为$\{(x_1,),(x_2,)...,(x_N,)\}$数据中并没有标签$y$，我们可以将$Y$认为是未观测到的隐变量，因此EM主要可以用作生成模型的非监督训练，其生成模型的$P(X,Y)$，中$X$是观测到的数据，$Y$为隐变量。

参考资料
--------
https://www.hrwhisper.me/machine-learning-em-algorithm/

https://www.cnblogs.com/jerrylead/archive/2011/04/06/2006936.html

《统计学习方法》李航