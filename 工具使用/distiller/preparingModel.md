## Preparing a Model for Quantization

### Distiller Quntizer

可以自动搜索模块。操作通常是通过直接重载张量运算符（+，-等）和在Torch名称空间下的函数（例如torch.cat（））执行的。还有torch.nn.functional命名空间，它提供与torch.nn中提供的模块等效的功能。

+ 在收集统计信息时，重用的每次调用都会覆盖为先前的调用收集的统计信息。最后，除最后一次调用外，所有调用的统计信息都丢失了。
+ 因此，为了确保Distiller对模型中所有受支持的操作进行了正确的量化，可能有必要在将模型代码传递给量化器之前对其进行修改。请注意，支持的操作的确切集合可能在不同的可用量化器之间有所不同。

### Model preparation

+ 替换掉直接的张量操作
+ 将重复使用的模块替换为专用实例
+ 等效模块替换torch.nn.functional调用
+ 特殊情况-用无法量化的变量替换无法量化的模块

类如如下代码
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class BasicModule(nn.Module):
    def __init__(self, in_ch, out_ch, kernel_size):
        super(BasicModule, self).__init__()
        self.conv1 = nn.Conv2d(in_ch, out_ch, kernel_size=kernel_size)
        self.bn1 = nn.BatchNorm2d(out_ch)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size)
        self.bn2 = nn.BatchNorm2d(out_ch)

    def forward(self, x):
        indentity = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)

        # (1) overloaded tensor addition opertation
        out += indentity

        # (2) relu module re-used
        out = self.relu(out)

        # (3) Using operation from torch namespace
        out = torch.cat([indentity, out], dim=1)
        # (4) Using function from nn.funtional
        out = F.sigmoid(out)

        return out

```

1. 替换其张量操作
(1)(3)都会被替换成distiller.modules.xxxx()， 并且会将其实现为成员

2. 重复使用的成员
要使用其他的量代替
(2) 调用self.relu会再定义一个relu然后替换掉原来的操

3. 外部调用与操作也会将其变为成员

按照如上规则就变成如下

```python
class BasicModule(nn.Module):
    def __init__(self, in_ch, out_ch, kernel_size):
        super(BasicModule, self).__init__()
        self.conv1 = nn.Conv2d(in_ch, out_ch, kernel_size=kernel_size)
        self.bn1 = nn.BatchNorm2d(out_ch)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size)
        self.bn2 = nn.BatchNorm2d(out_ch)

    def forward(self, x):
        indentity = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)

        # (1) overloaded tensor addition opertation
        out += indentity

        # (2) relu module re-used
        out = self.relu(out)

        # (3) Using operation from torch namespace
        out = torch.cat([indentity, out], dim=1)
        # (4) Using function from nn.funtional
        out = F.sigmoid(out)

        return out
```

