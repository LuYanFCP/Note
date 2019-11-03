#

## 第一个例子

```shell
time python3 compress_classifier.py -a alexnet --lr 0.005 -p 50 ../../../data.imagenet -j 44 --epochs 90 --pretrained --compress=../sensitivity-pruning/alexnet.schedule_sensitivity.yaml
```

+ 其中`time`是记录时间的linux指令
+ `-a`是指的是使用的模型
+ `-p`是指每50`mini-batches`打印一次状态
+ `-j`是加载数据的线程
+ `--epochs 90` 跑90轮
+ `--compress=../sensitivity-pruning/alexnet.schedule_sensitivity.yaml`压缩配置文件
+ `./logs` 默认的log文件

## 实现重现

重现问题很严重
(https://petewarden.com/2018/03/19/the-machine-learning-reproducibility-crisis/)重现问题

因此Pytorch支持固定随机性`--deterministic`（保证`j=1`）。

## 剪枝敏感性分析

Distiller支持按元素和按过滤器的修剪敏感性分析。在这两种情况下，L1-范数都用于对要修剪的元素或过滤器进行排名。例如，在运行过滤器修剪敏感性分析时，将计算每层权重张量的过滤器的L1范数，并且将底部x％设置为零。

分析过程相当长，因为当前我们使用整个测试数据集来评估每个权重张量的每个修剪级别的准确性。为此使用较小的数据集将节省大量时间，我们计划评估是否可以提供足够的结果。 结果输出为CSV文件（sensitiveivity.csv）和PNG文件（sensitiveivity.png）。该实现位于`distiller / sensitiveivity.py`中，其中包含有关过程和CSV文件格式的更多详细信息

可以将Sense命令行参数设置为元素或过滤器，具体取决于您要执行的分析类型。

## Post-training Quantization

具有量化模型的检查点将转储到运行目录中。它将包含量化的模型参数（数据类型仍为FP32，但值将为整数）。计算的量化参数（比例和零点）也存储在每个量化层中。

```shell
python3 compress_classifier.py -a resnet18 ../../../data.imagenet  --pretrained --quantize-eval --evaluate
```

具有量化模型的检查点将转储到运行目录中。它将包含量化的模型参数（数据类型仍为FP32，但值将为整数）。计算的量化参数（比例和零点）也存储在每个量化层中。

## 提供了TensorBoard中间可视化记录

```
tensorboard --logdir=logs
```

## Summaries

使用`summaries`功能，保存PNG需要特定Pytorch版本的支持

```
python3 compress_classifier.py --resume=../ssl/checkpoints/checkpoint_trained_ch_regularized_dense.pth.tar -a=resnet20_cifar ../../../data.cifar10 --summary=compute
```

## 收集激活值的统计信息

加一个参数`--act_stats`