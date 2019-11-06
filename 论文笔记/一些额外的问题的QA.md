# 一些论文中读到问题的探究

## Q：为什么要使用activation quantization

1. 如果只量化weight，而不量化activation会出现很多问题，比如计算效率比较低（原因是中最中最重要的就是activation与activation的点积， 低比特与fp32的点积效率很低）
2. 在推断里面使用量化的quantitied activation会加速运算。（低比特运算更快）

## Q：gradient mismatch是什么

# 基础性问题

## Q：为什么使用BN之后就不再需要`bias`

BN ： $z = \frac{x - \mu_{B}}{\sqrt{\sigma^2_{B} + \epsilon }}$

BN之后使用$\mu_{B}$直接归一化了，导致`bias`失效了。

## Q： trick和hack

trick : it works but maybe nobody knows why
hack : it works and only a few know why

## Q： classification、object localization、semantic segmentation、 instance segmentation的不同

Semantic segmentation的目的是在一张图里分割聚类出不同物体的pixel(pixel-wise prediction)，目前的主流框架都是基于Fully Convolutional Neural Networks (FCN)，semantic segmentation把图片里人所在的区域分割出来了，但是本身并没有告诉这里面有多少个人，以及每个人分别的区域，因此引入了instance segmentation， instance segmentation其实是semantic segmentation和object detection殊途同归的一个结合点。最后,我个人觉得之所以大家猛搞semantic segmentation而忽略instance segmentation的一个原因是没有好的数据集。

最后,我个人觉得之所以大家猛搞semantic segmentation而忽略instance segmentation的一个原因是没有好的数据集

Semantic Segmentation（c语义分割）：将每一个像素分类。
Object Localization|detection（b目标检测）：检测并用方框标记出图片中的物体（找出方框中心点和长宽），并作分类。
Instance Segmentation（d实例分割）：将图片中属于物体类别的像素识别出来并作分类。

## Q FCN

FCN对图像进行像素级的分类，从而解决了语义级别的图像分割（semantic segmentation）问题。与经典的CNN在卷积层之后使用全连接层得到固定长度的特征向量进行分类（全联接层＋softmax输出）不同，FCN可以接受任意尺寸的输入图像，采用反卷积层对最后一个卷积层的feature map进行上采样, 使它恢复到输入图像相同的尺寸，从而可以对每个像素都产生了一个预测, 同时保留了原始输入图像中的空间信息, 最后在上采样的特征图上进行逐像素分类。

其实，CNN的强大之处在于它的多层结构能自动学习特征，并且可以学习到多个层次的特征：较浅的卷积层感知域较小，学习到一些局部区域的特征；较深的卷积层具有较大的感知域，能够学习到更加抽象一些的特征。这些抽象特征对物体的大小、位置和方向等敏感性更低，从而有助于识别性能的提高

**传统的基于CNN的分割方法：**为了对一个像素分类，使用该像素周围的一个图像块作为CNN的输入用于训练和预测。这种方法有几个缺点：一是存储开销很大。例如对每个像素使用的图像块的大小为15x15，然后不断滑动窗口，每次滑动的窗口给CNN进行判别分类，因此则所需的存储空间根据滑动窗口的次数和大小急剧上升。二是计算效率低下。相邻的像素块基本上是重复的，针对每个像素块逐个计算卷积，这种计算也有很大程度上的重复。三是像素块大小的限制了感知区域的大小。通常像素块的大小比整幅图像的大小小很多，只能提取一些局部的特征，从而导致分类的性能受到限制。

(https://zhuanlan.zhihu.com/p/30195134)

## Q：机器学习论文中 xxx-wise是上面意思

从某方面某个角度考虑。
