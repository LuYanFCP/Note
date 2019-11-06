
# Quantization

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