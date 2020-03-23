

## Tracing vs Scripting

`onnx exporter` 可以是`trace-based`或者`trace-based`

+ `trace-based` 它可以通过执行一次模型并导出在此运行期间实际运行的运算符来运行。如果模型是动态的，根据输入数据更改行为，则导出模型将不准确。`trace-base`可能仅对特定的输入大小有效（这就是为什么我们需要在跟踪中使用显式输入的原因之一。如果您的模型包含诸如for循环和if条件之类的控制流，则基于跟踪的导出器将展开循环以及if条件，并导出与此运行完全相同的静态图。如果要使用动态控制流导出模型，则需要使用`script-base`的导出器。
+ `script-based`: `ScriptModule`是`TorchScript`中的核心数据结构，而`TorchScript`是`Python`语言的子集，可从PyTorch代码创建可序列化和可优化的模型。

