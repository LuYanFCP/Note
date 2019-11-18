
# Quantization

## 量化的理由

|INT8 Operation | Energy Saving vs FP32 | Area Saving vs FP32|
|-----|----|----|
|Add | 30x | 116x|
|Multiply |18.5x |27x|

### INT VS FP32

讨论数字格式时，有两个主要属性。第一个是动态范围，它是可表示数字的范围。第二个是动态范围内可以表示多少个值，这又决定了格式的精度/分辨率（两个数字之间的距离）。

在GEMMLWOP中，FP32比例因子是使用整数或定点乘法加上移位运算来近似得出的。在许多情况下，这种近似对精度的影响可以忽略不计。

由于整数格式的动态范围有限，如果我们将相同的位宽用于权重和激活以及累加器，则可能会很快溢出。因此，累加器通常以更高的位宽实现。 两个n位整数相乘的结果最多为2n位数字。如果是卷积的话$ck^2$其中$c$是`input channel`，$k$是核宽。在许多情况下，使用32位累加器，但是对于INT4及更低版本，可能会使用少于32位的累加器，具体取决于预期的使用情况和层宽度。

### INT8（"Conservative" Quantization: INT8）

如上所述，比例因子用于使当前张量的动态范围适应整数格式的范围。

最简单的方式:
1. `scale factor` 最简单的方式是 `FP min/max -> INT8 min/max`
2. activation 的 scale factor需要动态获得

#### Offline

脱机意味着在部署模型之前（在培训期间或通过在经过训练的FP32模型上运行一些“校准”批次）来收集激活统计信息。基于这些收集的统计信息，可以计算出比例因子，并在部署模型后将其固定。此方法可能会在运行时遇到超出先前观察到的范围的值的风险。这些值将被裁剪，这可能导致精度降低。(Nvidia)

#### Online

在线训练是动态的

然而，重要的是要注意，激活张量的整个浮动范围通常包括在统计上离群的元素。可以通过使用更窄的最小/最大范围来丢弃这些值，从而有效地进行一些削波，从而有利于提高提供给包含大部分信息的部分分布的分辨率。一种可以产生良好结果的简单方法是，仅使用观察到的最小/最大值的平均值代替实际值。或者，可以使用统计方法来智能地选择在哪里裁剪原始范围，以保留尽可能多的信息（Migacz，2017）。更进一步，Banner等人（2018年）提出了一种在特定条件下分析计算限幅值的方法。

### INT4以及一下的激进量化

+ Train/Re-Training
+ Replacing the activation function
+ Modifying network structure: (1)尝试通过使用更宽的层（更多的通道）来补偿由于量化导致的信息丢失[WRPN: Wide Reduced-Precision Networks] (2) 提出了一种二进制量化方法，其中用多个二进制卷积(?)代替单个FP32卷积，每个二进制卷积被缩放以表示不同的“基数”，从而覆盖了较大的总体动态范围。[Towards Accurate Binary Convolutional Neural Network]
+ First and last layer: 大多数方法将第一层和最后一层保留在FP32中。然而，Choi等人在2018年表明，这些层的保守量化例如至INT8，不会降低精度。
+ Iterative quantization：大多数方法会一次量化整个模型。 Zhou A等人，2017年采用了一种迭代方法，该方法从训练有素的FP32基线开始，然后仅量化模型的一部分，然后再进行几次重新训练以从量化中恢复准确性损失
+ Mixed Weights and Activations Precision：激活比权重对量化更敏感。（这什么意思）因此，与权重相比，看到激活量化后的精度更高的实验并不少见。一些作品只专注于量化权重，将激活保持在FP32。

## Post-train quantization

### 基础指令


| Long Form                | Short     | Description                                                                           | Default |
|--------------------------|-----------|---------------------------------------------------------------------------------------|---------|
| `--quantize-eval`        | `--qe`    | Apply linear quantization to model before evaluation                                  | Off     |
| `--qe-mode`              | `--qem`   | Linear quantization mode. Choices: "sym", "asym_u", "asym_s"                          | "sym"   |
| `--qe-bits-acts`         | `--qeba`  | # of bits for quantization of activations                                             | 8       |
| `--qe-bits-wts`          | `--qebw`  | # of bits for quantization of weights                                                 | 8       |
| `--qe-bits-accum`        | N/A       | # of bits for quantization of the accumulator                                         | 32      |
| `--qe-clip-acts`         | `--qeca`  | Set activations clipping mode. Choices: "none", "avg", "n_std"                        | "none"  |
| `--qe-clip-n-stds`       | N/A       | When qe-clip-acts is set to 'n_std', this is the number of standard deviations to use | None    |
| `--qe-no-clip-layers`    | `--qencl` | List of layer names (space-separated) for which not to clip activations               | ''      |
| `--qe-per-channel`       | `--qepc`  | Enable per-channel quantization of weights (per output channel)                       | Off     |
| `--qe-scale-approx-bits` | `--qesab` | Enables scale factor approximation using integer multiply + bit shift, using this number of bits the integer multiplier | None |
| `--qe-stats-file`        | N/A       | Use stats file for static quantization of activations. See details below              | None    |
| `--qe-config-file`       | N/A       | Path to YAML config file. See section above. (ignores all other --qe* arguments)      | None    |


### 是否要进行细粒度控制

如果进行细粒度控制的话，还需要配置一个`yaml`文件，并将其添加到`--qe-config-file`的参数中。

命令行参数一般是粗粒度控制量化。

### 第一步收集fp32的统计信息

将统计各个层的参数状态放到一个yaml文件中（之后要用）

如何产生统计信息

```shell
python compress_classifier.py -a <models> -p 10 -j 22 <path_to_imagenet_dataset> --pretrained --qe-calibration 0.05
```

+ `-p` 是指多少个iter打印一次
+ `-j` 是用多少个线程读取数据
+ `--pretrained`
+ `--qe-calibration` 多少统计数据 范围未$[0,1]$


产生于`logs`中

### 第二步进行量化shuffleNet

```shell 
time CUDA_VISIBLE_DEVICES=1 python compress_classifier.py -a shufflenet_v2_x1_0 --pretrained /data/public/datasets/ImageNet --evaluate --quantize-eval --qe-per-channel --qe-stats-file ./logs/2019.11.02-120554/layer_quant_params.yaml
```

会出现问题
```
  File "/data/users/ly/miniconda3/envs/distiller/lib/python3.5/site-packages/torch/onnx/__init__.py", line 40, in _optimize_trace
    trace.set_graph(utils._optimize_graph(trace.graph(), operator_export_type))
  File "/data/users/ly/miniconda3/envs/distiller/lib/python3.5/site-packages/torch/onnx/utils.py", line 188, in _optimize_graph
    graph = torch._C._jit_pass_onnx(graph, operator_export_type)
  File "/data/users/ly/miniconda3/envs/distiller/lib/python3.5/site-packages/torch/onnx/__init__.py", line 50, in _run_symbolic_function
    return utils._run_symbolic_function(*args, **kwargs)
  File "/data/users/ly/miniconda3/envs/distiller/lib/python3.5/site-packages/torch/onnx/utils.py", line 589, in _run_symbolic_function
    return fn(g, *inputs, **attrs)
  File "/data/users/ly/miniconda3/envs/distiller/lib/python3.5/site-packages/torch/onnx/symbolic.py", line 412, in symbolic
    dim, keepdim = _get_const(dim, 'i', 'dim'), _get_const(keepdim, 'i', 'keepdim')
  File "/data/users/ly/miniconda3/envs/distiller/lib/python3.5/site-packages/torch/onnx/symbolic.py", line 116, in _get_const
    return _parse_arg(value, desc)
  File "/data/users/ly/miniconda3/envs/distiller/lib/python3.5/site-packages/torch/onnx/symbolic.py", line 75, in _parse_arg
    return int(tval)
ValueError: only one element tensors can be converted to Python scalars
```

`pytorch` nn本身的问题

该问题在`torch1.2`中得到解决，~~但是现在1.1无法使用，正在探究问题~~

然后装上了`torch1.2`

出现
```
ImportError: /data/users/ly/miniconda3/envs/distiller/lib/python3.5/site-packages/torchvision/_C.cpython-35m-x86_64-linux-gnu.so: undefined symbol: _ZN2at7getTypeERKNS_6TensorE
```

疑似`torchvision`版本于`torch`不对应，升级`torchvision==0.4`

~~问题暂时得到解决。~~

出现新问题

```
AttributeError: 'torch._C.Value' object has no attribute 'uniqueName'
```

疑似是torch._C.Value又更新

通过GitHub可知道在`torch1.2`中uniqueName 更新为 debugName

修改了`summary`的uniqueName->debugName之后再次进行训练

出现了以下问题
```
File "/data/users/ly/source/repos/Distiller/distiller/summary_graph.py", line 356, in add_footprint_attr
    n_ifm = self.param_shape(conv_in)[1]
IndexError: tuple index out of range
```

```
An input to a Convolutional layer is missing shape information (MAC values will be wrong)
For details see https://github.com/NervanaSystems/distiller/issues/168
```
在这两部分都加上try，去相关的`issue`查找解决方法

之后就可以运行了，可以看到如下状态

```shell
50000 samples (256 per mini-batch)
Test: [   10/  195]    Loss 1.417802    Top1 68.242188    Top5 87.656250
Test: [   20/  195]    Loss 1.450474    Top1 67.656250    Top5 87.265625
Test: [   30/  195]    Loss 1.441040    Top1 68.125000    Top5 87.174479
Test: [   40/  195]    Loss 1.443656    Top1 68.105469    Top5 87.333984
Test: [   50/  195]    Loss 1.439673    Top1 67.898438    Top5 87.437500
Test: [   60/  195]    Loss 1.441517    Top1 67.845052    Top5 87.506510
Test: [   70/  195]    Loss 1.444593    Top1 67.812500    Top5 87.371652
Test: [   80/  195]    Loss 1.440051    Top1 67.924805    Top5 87.397461
Test: [   90/  195]    Loss 1.455102    Top1 67.673611    Top5 87.209201
Test: [  100/  195]    Loss 1.451254    Top1 67.761719    Top5 87.292969
Test: [  110/  195]    Loss 1.447441    Top1 67.883523    Top5 87.254972
Test: [  120/  195]    Loss 1.447744    Top1 67.828776    Top5 87.272135
Test: [  130/  195]    Loss 1.448617    Top1 67.869591    Top5 87.295673
Test: [  140/  195]    Loss 1.447163    Top1 67.765067    Top5 87.313058
Test: [  150/  195]    Loss 1.445723    Top1 67.713542    Top5 87.283854
Test: [  160/  195]    Loss 1.444993    Top1 67.648926    Top5 87.307129
Test: [  170/  195]    Loss 1.437624    Top1 67.812500    Top5 87.387408
Test: [  180/  195]    Loss 1.439316    Top1 67.756076    Top5 87.354601
Test: [  190/  195]    Loss 1.435286    Top1 67.802220    Top5 87.386924
==> Top1: 67.828    Top5: 87.372    Loss: 1.436

Saving checkpoint to: logs/2019.11.02-185058/quantized_checkpoint.pth.tar

Log file for this run: /data/users/ly/source/repos/Distiller/examples/classifier_compression/logs/2019.11.02-185058/2019.11.02-185058.log
CUDA_VISIBLE_DEVICES=7 python compress_classifier.py -a shufflenet_v2_x1_0     934.08s user 87.54s system 410% cpu 4:08.67 total
```

### 部署

暂时未找到部署方法，考虑使用onnx，然后放到别的推理平台上做推理

<!-- ### 一些Post-quantization的方法辨析 -->


<!-- #### "Net-Aware" Quantization

不仅考虑一个操作的中的参数量化，而要考虑整体模型的量化。

## Train-aware quantization -->

http://10.108.126.36:4567/forum/topic/28/quantization-aware-training在解决梯度不匹配问题的进展