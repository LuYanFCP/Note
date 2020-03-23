自己在量化方面的一个小整理

## 基本的小分类

1. Quantization的两种方式:
   + 已CodeBook形式为主的量化方式(Deep Compression)：使用聚类处理参数，然后将某一类全部由质心的值表示，然后已质心列表为CodeBook，然后权重张量只保存`index`因此可以压缩，但是这种方式，只能压缩不能加速（加速需要配合特殊的体系结构），这种方式在移动端基本没有采用。
   + 使用得bit定点或者浮点数直接进行表示。（主要）
2. Fixed-point quantization
   1. Post-Training Quantization: 使用FP32完成训练之后然后，通过一定的算法直接产生定点数参数，然后进行部署。(大部分移动端推理框架，都支持这种方式，比如说TensorRT)
   2. Quantize-Aware Training：在训练中使用伪量化做定点训练。

### 论文

