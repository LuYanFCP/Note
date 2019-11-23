## 介绍

这个类是进行分类模型压缩的基类，其提供的功能为:

- Command-line arguments handling
- Logger configuration
- Data loading
- Checkpoint handling
- Classifier training, verification and testing

### 初始化

初始化主要进行的是Logger的初始化

```python
    def __init__(self, args, script_dir):
        self.args = args
        _infer_implicit_args(args)  # 推断出使用的数据集
        self.logdir = _init_logger(args, script_dir)  # 初始化logger
        _config_determinism(args)  # 配置决定器
        _config_compute_device(args)
        
        # Create a couple of logging backends.  TensorBoardLogger writes log files in a format
        # that can be read by Google's Tensor Board.  PythonLogger writes to the Python logger.
        if not self.logdir:
            self.pylogger = self.tflogger = NullLogger()
        else:
            self.tflogger = TensorBoardLogger(msglogger.logdir)
            self.pylogger = PythonLogger(msglogger)   
        (self.model, self.compression_scheduler, self.optimizer, 
             self.start_epoch, self.ending_epoch) = _init_learner(args)  # 核心

        # Define loss function (criterion)
        self.criterion = nn.CrossEntropyLoss().to(args.device)
        self.train_loader, self.val_loader, self.test_loader = (None, None, None)
        self.activations_collectors = create_activation_stats_collectors(self.model, *args.activation_stats)  # 收集激活值
```

### _init_learner 核心

```python

def _init_learner(args):
    # Create the model
    model = create_model(args.pretrained, args.dataset, args.arch,
                         parallel=not args.load_serialized, device_ids=args.gpus)  # load_serialized?  # 创建模型
    compression_scheduler = None  # 特别关键

    # TODO(barrh): args.deprecated_resume is deprecated since v0.3.1
    if args.deprecated_resume:  # 是否要弃用resume
        msglogger.warning('The "--resume" flag is deprecated. Please use "--resume-from=YOUR_PATH" instead.')
        if not args.reset_optimizer:
            msglogger.warning('If you wish to also reset the optimizer, call with: --reset-optimizer')
            args.reset_optimizer = True
        args.resumed_checkpoint_path = args.deprecated_resume  # 这开始

    optimizer = None
    start_epoch = 0
    if args.resumed_checkpoint_path:
        model, compression_scheduler, optimizer, start_epoch = apputils.load_checkpoint(
            model, args.resumed_checkpoint_path, model_device=args.device)
    elif args.load_model_path:
        model = apputils.load_lean_checkpoint(model, args.load_model_path, model_device=args.device)
    if args.reset_optimizer:
        start_epoch = 0
        if optimizer is not None:
            optimizer = None
            msglogger.info('\nreset_optimizer flag set: Overriding resumed optimizer and resetting epoch count to 0')

    if optimizer is None:
        optimizer = torch.optim.SGD(model.parameters(), lr=args.lr,
                                    momentum=args.momentum, weight_decay=args.weight_decay)
        msglogger.debug('Optimizer Type: %s', type(optimizer))
        msglogger.debug('Optimizer Args: %s', optimizer.defaults)

    if args.compress: 
        # The main use-case for this sample application is CNN compression. Compression
        # requires a compression schedule configuration file in YAML.

        # 从文件得到配置信息和scheduler
        compression_scheduler = distiller.file_config(model, optimizer, args.compress, compression_scheduler,
            (start_epoch-1) if args.resumed_checkpoint_path else None)   # 输入配置文件  最核心的一部
        # Model is re-transferred to GPU in case parameters were added (e.g. PACTQuantizer)
        model.to(args.device)
    elif compression_scheduler is None:
        compression_scheduler = distiller.CompressionScheduler(model)

    return model, compression_scheduler, optimizer, start_epoch, args.epochs

```

```python
compression_scheduler = distiller.file_config(model, optimizer, args.compress, compression_scheduler,
            (start_epoch-1) if args.resumed_checkpoint_path else None)   # 输入配置文件  最核心的一部
```

其中这段代码通过调用 `file_config` 将yaml文件解析为`Ordered_Dict`, 然后将解析的对象传给`dict_config`（这个类在`config.py`）进行分析和生成对象。

