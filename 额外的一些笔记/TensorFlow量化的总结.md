## Post-training quantization

两个工具去实现这个实现这个，一个是`TensorFlow Lite Optimizing Converter`(toco命令行)和`TensorFlow Lite Converter`（API接口）

![](https://i.loli.net/2019/11/05/vBPw9Og3RoNIK1S.png)

### weight quantization

```python
import tensorflow as tf
converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_SIZE]
tflite_quant_model = converter.convert()
```

该方法将浮点数的权重转换位int8的整数，在推理过程中需要将int8反量化位浮点再计算，一次完成此转换，然后将其缓存以减少延迟。混合运算符将激活值动态量化为8位，并使用8位权重和激活值执行计算。如果某些Ops不支持int8量化的，那么其保存的权重依然是浮点型的，即部分支持int8量化的Ops其权重保存为int8整型且存在quantize和dequantize操作，否则依然是浮点型的，因而称该方式为混合量化。该方式可达到近乎全整型量化的效果，但存在quantize和dequantize操作其速度依然不够理想，支持该方式的操作如下：

+ tf.contrib.layers.fully_connected
+ tf.nn.conv2d
+ tf.nn.embedding_lookup
+ BasicRNN
+ tf.nn.bidirectional_dynamic_rnn for BasicRNNCell type
+ tf.nn.dynamic_rnn for LSTM and BasicRNN Cell types

### Full integer quantization of weights and activations

该方式则试图将权重、激活值及输入值均全部做int8量化，并且将所有模型运算操作置于int8下进行执行，以达到最好的量化效果。为了达到此目的，我们需要一个具有代表性的小数据集，用于统计激活值和输入值等的浮点型范围，以便进行精准量化，方法如下:

```python
import tensorflow as tf

def representative_dataset_gen():
  for _ in range(num_calibration_steps):
    # Get sample input data as a numpy array in a method of your choosing.
    yield [input]

converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset_gen
tflite_quant_model = converter.convert()
```


### 版精度float15量化-权重

该方式是将权重量化为半精度float16形式，其可以减少一半的模型大小、相比于int8更小的精度损失，如果硬件支持float16计算的话那么其效果更佳，这种方式是google近段时间提供的，其实现方式也比较简单，仅需在代码中调用如下接口即可：

```python
import tensorflow as tf
converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.lite.constants.FLOAT16]
tflite_quant_model = converter.convert()
```

当在CPU运行时，半精度量化也需要像int8量化一样进行反量化到float32在进行计算，但在GPU则不需要，因为GPU可以支持float16运算，但官方说float16量化没有int8量化性价比高，因此，在实作中也需要仁者见仁智者见智了。

## 量化感知训练

tensorflow量化感知训练是一种伪量化的过程，它是在可识别的某些操作内嵌入伪量化节点（fake quantization nodes），用以统计训练时流经该节点数据的最大最小值，便于在使用TOCO转换tflite格式时量化使用并减少精度损失，其参与模型训练的前向推理过程令模型获得量化损失，但梯度更新需要在浮点下进行因而其并不参与反向传播过程。某些操作无法添加伪量化节点，这时候就需要人为的去统计某些操作的最大最小值，但如果统计不准那么将会带来较大的精度损失，因而需要较谨慎检查哪些操作无法添加伪量化节点。值得注意的是，伪量化节点的意义在于统计流经数据的最大最小值并参与前向传播提升精确度，但其在TOCO工具转换为量化模型后，其工作原理还是与训练后量化方式一致的！

使用伪造的量化节点对量化误差进行建模，以模拟前向和后向传递中的量化效果。