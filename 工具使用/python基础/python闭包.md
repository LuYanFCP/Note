# python的命名空间

> namespace （命名空间）是一个从名字到对象的**映射**。 大部分命名空间当前都由 Python 字典实现，但一般情况下基本不会去关注它们（除了要面对性能问题时），而且也有可能在将来更改。

命名空间是为了避免名字重复的一种重要结构。命名空间是动态的，推随着解释器的执行产生，在程序过程中一直在维护。

命名空间：

+ 内置命名空间：Python解释器一启动就自带的命名空间，Python解释器结束后停止。
+ 全局命名空间：Python模块全局名字集合，直接定义在模块中的名字，如类，函数，导入的其他模块等。解析器退出时销毁。
+ 局部命名空间：局部命名空间就是在函数中，类中的命名空间。当一个函数被调用是创建，并在函数返回时或者抛出一个不再函数内除处理的错误时被删除。
+ 一个对象的属性命名空间
+ 类命名空间

# 作用域

一个 作用域 是一个命名空间可直接访问的 Python 程序的**文本区域**。 这里的 “可直接访问” 意味着对名称的非限定引用会尝试在命名空间中查找名称。

作用域被静态确定（文本区域），但被动态（命名空间）使用。 在程序运行的任何时间，至少有三个命名空间可被直接访问的嵌套作用域：

+ 最先搜索的最内部作用域包含局部名称（local）
+ 从最近的封闭作用域开始搜索的任何封闭函数的作用域包含非局部名称，也包括非全局名称（enclosing）
+ 倒数第二个作用域包含当前模块的全局名称（global）
+ 最外面的作用域（最后搜索）是包含内置名称的命名空间（built-in）

python的作用域解析如同其他语言也遵循着就近原则，从近到远安装命名空间进行搜索，依据：Local -> Enclosing Local -> Gobal -> built-in 的顺序进行解析。

## local（局部命名空间）

局部命名空间就是在函数中，类中的命名空间。当一个函数被调用是创建，并在函数返回时或者抛出一个不再函数内除处理的错误时被删除。

```python
def hello():
    _str = "hello world"  # local局部名称
    print(_str)
    return _str
```

## Enclosing Local

enclosing搜索也是在局部作用域中，根据嵌套层次从内到外搜索，包含非局部（nonlocal）非全局（nonglobal）名字的任意封闭函数的作用域。如两个嵌套的函数，内层函数的作用域是局部作用域，外层函数作用域就是内层函数的 Enclosing作用域。

比如说:

```python
def hello():
    _str = "hello world"
    a = 1
    nonlocal b = 2
    def say():
        print(a)  # 1
        # a += 2  # 出错， 无法修改
        a = 3 # local变量覆盖外层的函数的变量
        b += 3  # ok 可以通过

    print(a)  # 1
    print(b)  # 5
    return say
```

上述例子内部的函数`c`在`print(a)`的时候首先在自己的`local`找没有找到，因此在其外一层中找，找到了a，打印

执行`a += 2`时，还是一样的搜索途径，但是`a`并不是非本地变量（没有关键词声明`nonlocal`），**只能访问不能修改。自由变量只能访问，不能修海**

执行`a = 3`，则使用local变量去覆盖外层函数的变量。因此最后`print(a)`输出为1。

执行`b+=3`成功，`b`是非本地变量，可以修改。

## global （全局名称）

例如

```python
a = 1
def hello():
    print(a) # 可以访问
    a += 1  # 错误
```

> 如果一个名称被声明为**全局变量**，**则所有引用和赋值将直接指向包含该模块的全局名称的中间作用域**。 要重新绑定在最内层作用域以外找到的变量，可以使用 nonlocal 语句声明为非本地变量。 如果没有被声明为非本地变量，这些变量将是只读的（尝试写入这样的变量只会在最内层作用域中创建一个 新的 局部变量，而同名的外部变量保持不变）。

如果要修改全局变量需要使用`global`进行声明，将全局变量绑定到该作用域。

## Built-in（内置名称的命名空间）

> 包含内置名称的命名空间是在 Python 解释器启动时创建的，永远不会被删除。模块的全局命名空间在模块定义被读入时创建；通常，模块命名空间也会持续到解释器退出。被解释器的顶层调用执行的语句，从一个脚本文件读取或交互式地读取，被认为是 `__main__` 模块调用的一部分，因此它们拥有自己的全局命名空间。（内置名称实际上也存在于一个模块中；这个模块称作 builtins 。）

这个命名空间在`python`解释器启动的时候创建，退出时销毁。

## 作用域的引入

`Built-in`、`Gobal`一般是默认的，在加载的时候就加载进去，而`Enclosing Local`和`Local`是动态载入的。

什么时候引入作用域：

+ 函数会引入`Local`或者`Enclosing Local`, `lambda`和`generator`也是函数。
+ 类引入`local`
+ 列表推导引入`local`

什么时候不引入作用域：

+ `if`语句
+ `for`语句也不引入新的作用域
```python
for i in range(10):
    print(i)
print(i) # 还是ok
```

## 自由变量

自由变量是在其他作用域下，通过索引规则能访问到的，但是没有绑定到当前作用域的变量。

核心：自由变量可以访问不可以修改

```python
i = 0
def add(n):
    print(i) # 可以
    # i += n # 不可以
```

需要使用`gobal`与`nonlocal`将变量绑定到当前作用域下，即可修改。`gobal`用于绑定全局变量，`nonlocal`用于邦定`local`变量

# 闭包

**闭包指延伸其作用域的函数，其中包含函数定义体中引用、但是不在定义体中定义的非全局变量。闭包是一种函数，它会保留定义函数时存在的自由变量的绑定，这样调用函数时，虽然定义作用域不可用了，但是仍能使用那些绑定。**

## 一个简单的例子

如果有一个函数`avg`，它的作用是不断计算系列值的均值；例如整个历史重平均收盘价，每天都会增加新价格，因此平均值要考虑至目前为止所有的价格。

例如

```python
avg(10)
10.0
avg(11)
10.5
avg(12)
11.0
```

avg从何而来，它又在哪里保存历史值，为了实现它，我们实现一个简单的`class`版本

```python
class Averager():
    def __init__(self):
        self.series = []

    def __call__(self, new_value):
        self.series.append(new_value)
        total = sum(self.series)
        return total / len(self.series)

>> avg = Averager()
>> avg(10)
10.0
>> avg(11)
10.5
>> avg(12)
11.0
```

同样我们可以使用高阶函数实现

```python
def Averager():
    series = []
    def averager(new_value):
        series.append(new_value)
        total = sum(series)
        return total / len(series)
    return averager

>> avg = Averager()
>> avg(10)
10.0
>> avg(11)
10.5
>> avg(12)
11.0
```

注意到在使用高阶函数`series`是`Averager`的局部变量，课是在avg得到时候`Averager`已经范围，本地作用于与已经消失，这个时候内层的`averager`函数的作用域就多一个自由变量`series`，也就是`averager`延申到自己函数作用域之外。

```python
In [9]: avg.__code__.co_varnames
Out[9]: ('new_value', 'total')

In [10]: avg.__code__.co_freevars
Out[10]: ('series',)
```

其中`series`绑定在返回的avg函数的`__closure__`属性中。这些元素是`cell`对象，有一个`cell_contents`属性，保存着真正的值。因此`avg`是闭包。

参考
-----
https://docs.python.org/zh-cn/3/tutorial/classes.html#python-scopes-and-namespaces

https://www.cnblogs.com/crazyrunning/p/6914080.html

《流畅的python》