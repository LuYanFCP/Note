过程

## 1. 创建一个WorkFlow

`parser` -> `network` -> `engine` -> `context` -> `run` -> `save`

+ `parser`使用自己不同模型的默认`parser`
+ network由`parser`创建

## 2. Calibrator的输入

需要自定义Calibrator进行操作，自定义的Calibrator会通过继承以下的类而达到使用该算法的目的

+ IInt8Calibrator (这个可以通过get_algorithm更好的选择下面三种算法)
+ IInt8LegacyCalibrator
+ IInt8EntropyCalibrator
+ IInt8EntropyCalibrator2
+ IInt8MinMaxCalibrator

然后自己去实现相应的算法需要的方法

例如在`int8_caffe_mnist`
```
```