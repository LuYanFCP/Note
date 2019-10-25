
## UniformQuantTFLearner的初始化

这个类继承于AbstractLearner类，首先在它初始化的先判断是否有训练好的预训练模型。此时使用继承过来的download_model进行查找，如果不存在预训练模型就直接下载。

然后在筛选出不进行量化的参数（主要是手动插入的效果）与`uqtf_enbl_manual_quant`参数有关，默认它是`false`也就是不使用
> UQ-TF: enable manually inserting quantization operations.

然后使用`__build_train()去初始化训练前的过程`

### __build_train() 函数

主要目的是创建训练使用的图
