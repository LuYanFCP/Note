## 基本介绍

基于nvidia-docker，的容器云。

## start

获取

```bash
$ docker pull nvcr.io/nvidia/tensorrtserver:18.09-py3
$ nvidia-docker run -it --rm nvcr.io/nvidia/tensorrtserver:18.09-py3
$ trtserver --help # 确认服务可以运行
```

> 注：需要计算能力在6.0以上的GPU

## 模型存储库

支持`TensorRT、TensorFlow 和 Caffe2`的模型trt运行时，无法改变模型存储库中的模型，但替换系版本

例如我们有目录结构，作为一个模型库
```
/tmp/models
    mymodel/
        config.pbtxt
        3/
        model.pan

```
模型存储库中必须包含一个配置`.config.pbtxt`的文件，该文件包含着配置信息,模型配置信息需要以`https://github.com/NVIDIA/tensorrt-inference-server/blob/master/src/core/model_config.proto` 这个文件为原型。 例如配置适用于Caffe2的 `ResNet50`的配置文件

```
name: "resnet50_netdef"
platform: "caffe2_netdef"
max_batch_size: 128
input [
   {
      name: "gpu_0/data" 
      data_type: TYPE_FP32
      format: FORMAT_NCHW
      dims: [ 3, 224, 224 ]
   }
]
output [
   {
      name: "gpu_0/softmax"
      data_type: TYPE_FP32
      dims: [ 1000 ]
   }
]
```

+ `name`: 是您在向`trtserver`发送推理请求时用于引用模型的名称。
+ `platform`：是模型的格式，如此例使用的是NetDef格式的Caffe2模型
+ `max_batch_size`: 最大批
+ `input`： 是一系列输入的设置，包括，`name`也就是在图中定义的输入节点名称。还要数据的format格式。
+ `output`： 同样与input

### TensorFlow Model

TensorFlow的保存格式有两种: GraphDef（pb模型）和 SavedModel（ckpt模型），TensorRT两者都支持。

GraphDef或者用freeze_graph转换为GraphDef，或者用`save builder`或者`tensorflow_savedmodel`field去定义。

### Caffe2 Model

### TensorRT Models

PLAN模型不可跨平台也不可以跨硬件。如果需要多算力版本显卡的异构的话，可以将各个算例版本的模型都存一遍。`trtserver`会根据具体的情况筛选模型

```
# 文件结构
/tmp/models
   plan_model/
      config.pbtxt
      1/
         model_6_1.plan
         model_7_0.plan

# 配置
name: "plan_model"
platform: "tensorrt_plan"
max_batch_size: 16
input [
   {
      name: "input"
      data_type: TYPE_FP32
      dims: [ 3, 224, 224 ]
   }
]
output [
   {
      name: "output"
      data_type: TYPE_FP32
      dims: [ 10 ]
   }
]
cc_model_filenames [
   {
      key: "6.1"
      value: "model_6_1.plan"
   }
   {
      key: "7.0"
      value: "model_7_0.plan"
   }
]
```

### ONNX

使用ONNX转换为PLAN在使用或者使用ONNX转换为`Caffe NetDef`

## 分类标签关联(Classifer任务)

可以使用一些输出配置进行

```
output [
   {
      name: "gpu_0/softmax"
      data_type: TYPE_FP32
      dims: [ 1000 ]
      label_filename: "resnet50_labels.txt"
   }
]
# 文件目录
/tmp/models
   netdef_model/
      config.pbtxt
      resnet50_labels.txt
      1/
         init_model.netdef
         model.netdef
```