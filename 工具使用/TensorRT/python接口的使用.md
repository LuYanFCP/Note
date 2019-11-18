
## TensorRT的基本部分

1. Logger: 提供logger功能，所有的`TensorRT`的类都使用它来进行`error`、`warning`和`informative message`
2. Engine和Context： `tensorrt.ICudaEngine`，它一般会产生一个`tensorrt.IExecutionContext`的对象用于推理。
3. Builder：`tensorrt.Build`通常用来创建`tensorrt.ICudaEngine`, 同时我们需要传入`tensorrt.INetworkDefinition`对象。
4. Network： `tensorrt.INetworkDefinition`通常用来表示一个计算图，TensorRT为各种深度学习框架提供了一套解析器，也可以使用网络API手动填充网络。
5. Parsers 用于解析不同框架

## 基本步骤

### 读入模型

### 自己创建，手动创建

### 导入caffe的模型

```python
trt.CaffeParser()
```

### 导入tensorflow模型

1. 固化参数模型 ckpt->pb
2. 使用convert-to-uff 转化位uuf格式
3. 通过uuf解析器读入

需要注册输入输出

```python
    parser.register_input("Placeholder", (1, 28, 28))
    parser.register_output("fc2/Relu")
    parser.parse(model_file, network)
```

#### 导入onnx模型

创建build、network和parser

```python
import tensorrt as trt

TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

with builder = trt.Builder(TRT_LOGGER) as builder, builder.create.network() as network, trt.OnnxParser(network, TRT_LOGGER) as parser:
    with open(model_path, 'rb') as model:
        parser.parse(model.read())
    
```

#### 创建一个引擎

`builder`的功能之一是搜索其CUDA内核目录，以寻求可用的最快实现，因此有必要使用与运行优化引擎的GPU相同的GPU进行构建。`builder`有很多属性，我们可以通过这些属性控制网络精度或者自动调整参数，例如确定哪个TensorRT对每个内核最快的时间（迭代次数越多，运行时间越长，但对噪声的敏感性越低。）也可以通过`builder`去查询本机支持混合精度类型。

最终他要的两个参数
+ `max_batch_size` 
+ `max_workspace_size` 构建优化引擎时构建器可用的内存量，通常应将其设置为尽可能高。层级之间的算法通常需要一个临时空间存放数据。他的参数限制了网络中任何层可以使用的最大大小。（该如何设置呢？）

```python
with trt.Builder(TRT_LOGGER) as builder, builder.create_builder_config() as config, builder.build_cuda_engine(network, config) as engine:
# Do inference here.
```

#### inference

1. 申请输入输出缓存

```python
# Determine dimensions and create page-locked memory buffers (i.e. won't be swapped to disk) to hold host inputs/outputs.
h_input = cuda.pagelocked_empty(engine.get_binding_shape(0).volume(), dtype=np.float32)
h_output = cuda.pagelocked_empty(engine.get_binding_shape(1).volume(), dtype=np.float32)
# Allocate device memory for inputs and outputs.
d_input = cuda.mem_alloc(h_input.nbytes)
d_output = cuda.mem_alloc(h_output.nbytes)
# Create a stream in which to copy inputs/outputs and run inference.
stream = cuda.Stream()
```

2. 创建一些空间来存储中间激活值。由于引擎保留了网络定义和训练好的参数，因此需要额外的空间。这些是在执行上下文中保存的：

```python
with engine.create_execution_context() as context:
    # Transfer input data to the GPU.
    cuda.memcpy_htod_async(d_input, h_input, stream)  # 从h to d
    # Run inference.
    context.execute_async(bindings=[int(d_input), int(d_output)], stream_handle=stream.handle)
    # Transfer predictions back from the    GPU.
    cuda.memcpy_dtoh_async(h_output, d_output, stream)
    # Synchronize the stream
    stream.synchronize()
    # Return the host output. 
return h_output
```

## 序列化模型

序列化引擎不可跨平台或TensorRT版本移植。引擎特定于它们所构建的确切GPU模型（除了平台和TensorRT版本）。

```python
serialized_engine = engine.serialize()
with trt.Runtime(TRT_LOGGER) as runtime:
    engine = runtime.deserialize_cuda_engine(serialized_engine)
with open("sample.engine", "wb") as f:
    f.write(engine.serialize())
# 反序列化
with open(“sample.engine”, “rb”) as f, trt.Runtime(TRT_LOGGER) as runtime:
    engine = runtime.deserialize_cuda_engine(f.read())
```

## 衍生工具集

`onnx-tensorRT`: 使用onnx模型进行转换和使用onnx模型。
`pytorch-tensorRT`: 直接使得pytorch模型可以在tensorRT上部署的一个包。

> 对pytorch的疑问，这个是如何做到如此高效的，我自己实现的效果很差，吞吐和比使用torch快一点。

> https://docs.nvidia.com/deeplearning/sdk/tensorrt-api/python_api