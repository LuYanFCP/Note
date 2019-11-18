
## Function的拓展

向autograd添加操作需要为每个操作实现一个新的Function子类。`function`是`autograd`用于计算结果和梯度以及对操作历史进行编码的功能。每个新功能都需要您实现2种方法：

+ `forward`  
+ `backward` 将为它提供与输出一样多的Tensor参数，每个参数代表梯度。如果您的输入不需要梯度（needs_input_grad是布尔值的元组，指示每个输入是否需要梯度计算）