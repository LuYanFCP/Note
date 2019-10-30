## quantization network

### 聚焦的问题

forward和backward 过程中使用的函数的不同，梯度不同会导致训练的不稳定性。
+ forward: $x_{out} = \delta clamp(0, N-1, round(\frac{x}{\delta} - z))$
+ backward: $x_{out} = clamp(x_{min}, x_{max}，x)$
这样会出现梯度不匹配的现象

过去的工作：


本文的贡献
1. 提出了量化方法`` ``~~~~simple/straightforward and general/uniform
2. 实现了一个end-to-end量化网络 可用与分类与目标检测

### 过去的工作


approximate-based 和 optimization-based 

approximation-based:
1. BinaryConnect -> 直接量化权重，backward使用 hard tanh
2. BWN 加入scale factor 在量化中
3. TWN
4. TTQ 
5. DoReFa-Net -> 量化weight和activation使用不同的量化方式。梯度估计为全精度权重绝对值的平均
6. 

