## TensorBoardX

基于TensorBoard的pytorch可视化工具，就是Pytorch版本的TensorBoard接口。

## 基本用法

### SummaryWriter

与tensorflow相同，tensorboardX提供了一种创建tensorboard log的文件方法`SummaryWriter`

`SummaryWriter`的参数有

+ `logdir` 指定存储log的位置，如果不设置，则为当前目录下的`runs`文件夹中
+ `comment`： 提交log的文件名称`time + commentName`

相应的成员方法，也就是`add_something`系列API,其中`something`可以是

+ `scalar` 一般用作存储某些参数的变化，比如说loss，比如说acc等。 `add_scalar(namespace, value, iteration)` 其中，namespace是这个变量的名称或者称为命名空间， value相当于y轴。如果要绘制多个曲线在一张图可以使用`add_scalars(namespace, dict, iteration)`其就会将`dict`中的多组数据绘制在图中。
+ `image` 可视化图片，输入一个[3, H, W]的张量，为RGB格式的图片.
+ `histogram` 可视化分布直方图 `add_histogram(name, array, iteration)`

+ `figure` 添加一些图输入必须是`matplotlib.pyplot.figure`或者一个这样的list