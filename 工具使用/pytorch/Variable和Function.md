## Pytorch 构建计算图

+ Pytorch中也是构建计算图实现`forward`计算以及`backward`梯度计算。
+ 计算图由节点和边组成。
+ 计算图中边是一种函数或者一种运算，节点是参与运算的数据，边上两端的两个节点中，一个为函数的输入数据，另一个为函数的输出数据。
+ `Variable`是相应的节点。 `Function`相当于计算图的边。`Variable`需要保存forward时的激活值，即`Variable.data`它是由一个`Tensor`表示。同时在反向传播的时候它还需要保存梯度，因此有一个`Variable.grad`可以得到其梯度

## Variable与Tensor的差别

Variable中封装了三种属性`data`、`grad`、`grad_fn`三种属性。其中`data`和`grad`封装了激活值和梯度。`grad_fn`封装了是那个`Function`输出了这个`Variable`。

在forward时，`Variable`和`Function`构建一个计算图。只有得到了计算图，构建了`Variable`与`Function`与Variable的输入输出关系，才能在backward时，计算各个节点的梯度。`Variable`可以进行`Tensor`的大部分计算。

对`Variable`使用`.backward()`方法，可以得到该Variable之前计算图所有Variable的梯度

## 动态图机制的运行

+ `Variable`与`Function`组成了计算图。
+ `Function`是在每次对`Variable`进行运算生成，表示的是该次运算。
+ 动态图每次由forward的时候动态生成的。具体说，加入有Variable x, Function `*`。他们需要进行运算 y = x * x，则在运算过程时生成得到一个动态图，该动态图输入是x，输出为y，y的`creator`是`*`。
+ 一次forward过程将有多个Function连接各个Variable，Function输出的Variable将保存该Function的引用（即.creator），从而组成计算图。

## Tensor

+ 有两个属性一个.required_grad如果是True就类似于Variable的作用， 它可以通过调用`backward()`计算出之前所有计算图的梯度`.grad`
+ 要停止张量跟踪历史记录，可以调用.detach（）将其与计算历史记录分离，并防止跟踪将来的计算。也可以通过 `with torch.no_grad():` 在其空间内的代码块是不会跟踪`grad`的。
+ `Tensor`和`Function`共同组成一个计算图，他说一个无环图。每个张量都有一个`.grad_fn`属性，该属性引用创建了张量的函数（用户创建的张量除外-它们的`grad_fn`为None）。

## Function自定义化

Function与Module都可以对pytorch进行自定义拓展，使其满足网络的需求，但这两者还是有十分重要的不同：

+ Function 一般定义一个操作，因此无法保存参数，因此适用于激活函数、pooling等操作；Module是保存了参数，因此适合定义一层，例如线形层、卷积层、也适合定义一个网络。
+ Function定义需要三个方法: `__init__`、`forward`、`backward` （需要根据自己的需求写求导公式）
+ Module不仅包括了Function，还包括了对应的参数，以及其他函数与变量，这是Function所不具备的

### 自定义一个ReLU

+ 首先我们定义一个继承Function的ReLU类
+ 然后我们来看Variable在进行运算时，其grad_fn是否是对应的Function
+ 最后我们为方便使用这个ReLU类，将其wrap成一个函数，方便调用，不必每次显式都创建一个新对象

```python

```