## 程序入口
1. 首先将使用 add_cmdline_args 的方法，将`classifier.init_classifier_compression_arg_parser()`总的需求的args添加当前解析
2. 创建一个`ClassifierCompressorSampleApp` 这个对象对分类模型进行处理
3. 是否要使用知识蒸馏
4. 开始运行 使用类的`run_training_loop`方法进行运行
5. 返回一个测试

## ClassifierCompressorSampleApp

继承于`classifier.ClassifierCompressor`方法

+ 类的初始化
    `early_exit_init` 这个方法前处理
+ 是否保存未训练的模型， 如果保存使用 `app.save_checkpoint()`进行保存
+ 定义了`handle_subapps`方法，其作用是调用本地的`handle_subapps`方法。

### handle_subapps方法
