
## MobileNetV1

以往网络的计算瓶颈：卷积层

如何加速卷积的速度: 

+ 深度可分离卷积(depthwise separable convolution) -> mobileNet、Xception
+ 组卷积(group convolution) -> shuffleNet

### 深度可分离卷积

标准卷积：

![](https://pic4.zhimg.com/80/v2-f471bdb9191d0c8b65688ececbe935fb_hd.jpg)

设定相关变量卷积核的长宽为$K$，输入channel与输出channel为$C_{in}$和$C_{out}$，feature map的边长为$M$，输入张量的变成为$X$则，$M-(X-K+2*padding)/stride + 1$

卷积核的大小为 $K * K * C_{in}$, 每一个卷积核对应一个输出channel，因此从输入到输出需要有$K * K * C_{in} * C_{out}$个参数， 计算量为$M^2 + K^2 + C_{in} + C_{out}$

![](https://pic1.zhimg.com/80/v2-2d11a371ccccc4716958e752ce6d423c_hd.jpg)

![](https://pic4.zhimg.com/80/v2-abb36872e97253589e659e6484e63423_hd.jpg)

因此将3X3卷积转换为

![](https://i.loli.net/2019/11/17/CrW7LBHOyZYagvc.png)

### 其他优点

用ReLU6代替ReLU，可以使得激活值有范围，提高低比特上的表现

网络结构如下

![](https://i.loli.net/2019/11/17/kwfDbBl8zsp2xot.png)

## MobileNetV2

MobileNetV1的问题：发现深度卷积部分的卷积核比较容易训废掉，训完之后发现深度卷积训出来的卷积核有不少是空的。

原因出在ReLU上面，ReLU训练低纬度的时候容易造成信息丢失，在高纬度上做ReLU就不会丢失。**这就解释了为什么深度卷积的卷积核有不少是空。发现了问题，我们就能更好地解决问题。针对这个问题，可以这样解决：既然是ReLU导致的信息损耗，将ReLU替换成线性激活函数**

### Linear bottleneck

将最后一层换成Linear激活函数

![](https://i.loli.net/2019/11/18/joRzsuYHrOBCd6G.png)

![](https://i.loli.net/2019/11/18/peS5aLTNPOZzbhl.png)


### shortcut的引入

![](https://i.loli.net/2019/11/18/2VORSPXjstKUYDE.png)


因为引入shortcut结构了，所有只用stride=1的情况才能使用shortcut，因此分为两种情况

![](https://i.loli.net/2019/11/18/zqOVCHsKTrvWiu6.png)


网络结构

![](https://i.loli.net/2019/11/18/HCirFk9d3Xs1GP4.png)

参考资料
-----------

https://zhuanlan.zhihu.com/p/70703846