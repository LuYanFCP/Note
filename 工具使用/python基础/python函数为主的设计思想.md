# 装饰器

装饰器是可调用的对象，其参数是另一个函数（被装饰函数）。装饰器可能会处理被装饰的函数，然后把它返回，或者替换成另一个函数或者可调用对象。

```python
@test
def target():
    print("run target function!")
```

其作用与以下代码一样

```python
def target():
    print("run target function!")
target = test(target) # 在test函数中，会加强函数或者替换函数
```

函数装饰器在导入模块时理解执行，而被装饰的函数只是在明确调用的时候才运行。

Python不需要声明变量，但是假定在函数定义体重赋值的变量是局部变量。这比`javascript`的行为好太多，`javascript`也不需要声明变量，但是如果忘记把变量声明为局部变量（使用var），可能会在不知请的时候获取到全局变量。

## 一个装饰器的例子---给程序打运行log

目标，每次程序运行都输出`log`，输出程序运行的时间，结果等等，将`log`输出到`terminal`中

```python
import time
def log(func):
    def ff(*args, **kwargs):
        t0 = time.time()
        run_time = time.asctime(time.localtime(t0))
        res = func(*args, **kwargs)
        cost = time.time() - t0
        name = func.__name__
        args_str = ', '.join(repr(arg) for arg in args)  # repr转换为人阅读的方式
        print('[{}] {}({})->{} cust_time={} s'.format(run_time, name, args_str, res, cost))
        return res
    return f

@log
def f(n):
    if n <= 1:
        return 1
    return n * f(n-1)

>> f(5)
[Fri Mar 20 16:04:05 2020] f(1)->1 cust_time=0.0 s
[Fri Mar 20 16:04:05 2020] f(2)->2 cust_time=0.0 s
[Fri Mar 20 16:04:05 2020] f(3)->6 cust_time=0.000997304916381836 s
[Fri Mar 20 16:04:05 2020] f(4)->24 cust_time=0.000997304916381836 s
[Fri Mar 20 16:04:05 2020] f(5)->120 cust_time=0.000997304916381836 s
120
```

以上的例子就实现了这个功能，但是这个功能还不够完全，因为不支持关键词参数，同时器还会遮盖被装饰函数的`__name__`和`__doc__`等属性引入入`functools.wraps`来协助装饰器。

```python
def log(func):
    @functools.wraps(func)
    def f(*args, **kwargs):
        t0 = time.time()
        run_time = time.asctime(time.localtime(t0))
        res = func(*args, **kwargs)
        cost = time.time() - t0
        name = func.__name__
        args_str = ', '.join(repr(arg) for arg in args)  # repr转换为人阅读的方式
        print('[{}] {}({})->{} cust_time={} s'.format(run_time, name, args_str, res, cost))
        return res
    return f
```

## 参数化装饰器

我们将此见到很多wrap引入参数去辅助，类如

```python
from functools import lru_cache
@lru_cache(max_size=16)
def f(n):
    if n <= 1:
        return 1
    return n * f(n-1)
```

这个就等价于

```python
f = lru_cache(max_size=16)(f)
```

因此如果要添加参数必须要让`wraper`的函数在多一层，还是以上面的例子，这个时候，可以将fmt当作参数

```python
import functools, time
fmt='[{}] {}({})->{} cust_time={} s'
def log(fmt):
    def log_f(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            t0 = time.time()
            run_time = time.asctime(time.localtime(t0))
            res = func(*args, **kwargs)
            cost = time.time() - t0
            name = func.__name__
            args_str = ', '.join(repr(arg) for arg in args)  # repr转换为人阅读的方式
            print(fmt.format(run_time, name, args_str, res, cost))
            return res
        return f
    return log_f
```


