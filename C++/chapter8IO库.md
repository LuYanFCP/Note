## 基本IO类

头->类
+ iostream->istream,ostream,iostream(多一个w是宽字节版)
+ fstream->ifstream,ofstream,iofstream(多一个w是宽字节版)
+ sstream->istringstream,ostringstream,iostringstream(多一个w是宽字节版)
istringstream,ifstream都继承于istream

IO对象无拷贝和赋值

```cpp
ofstream out1, out2
out1 = out2 //出错：不能对流对象赋值
ofstream print(ofstream) // 不能初始化流对象
out2 = print(out2) // 不能拷贝流对象
```

## 条件状态

IO库的条件状态
+ `strm::iostate` 条件状态集合。
+ `strm::badbit` 指出流已经崩溃。
+ `strm::failbit` 指出IO流操作失败。
+ `strm::eofbit` 流到达了文件结束。
+ `strm::goodbit` 用来指出流未处于错误状态，此值保证为0。

+ `s.eof()` 若eofbit置位则返回true,表示到达流末尾
+ `s.fail()` 若badbit或failbit置位，则返回true
+ `s.good()` 若流s处于有效状态，则返回true
+ `s.clear()` 清空各个状态位，将流置为有效
+ `s.clear(flag)` 复位flag中设置的标志位。可以先使用rdstate()读取到流标志位，进行位操作，作为flag参数传入。
+ `s.rdstate()` 返回流当前的状态。

一个流一旦发生错误，其上后续的IO操作都会失败
通常确定一个流对象的状态的最简单的办法就是当作一个条件来使用
```cpp
while (cin >> word)
    // 读操作
```

### 查询流的状态

IO定义了一个与机器无关的`iostate`类型，它提供了表达流状态的完整功能。这个类型应作为一个位集合来使用。IO库定义了4个iostate类型的`constexper`值，表示特定位的模式。可以与位运算一起来使用检测和设置多个标志位。

+ `badbit`系统将错误，一旦出现不可被复位。
+ `failbit`、`eofbit`可以被修正

good索引错误位均未置位的情况下返回`true`，在`badbit`被置位时，fail也会返回`true`，也就是说 使用good或者fail就可以。

![](https://i.loli.net/2019/10/28/pdgMLfitwQs3NlA.png)

### 缓冲

输出缓冲的时机
+ 程序结束
+ 缓冲区慢
+ endl、ends、flush
+ 使用unitbuf刷新（cerr是设置unitbuf，内容立即刷新）
+ 一个输出流被关联到另一个流。 cin和cerr都会关联到 cout

```cpp
cout << unitbuf; //设置立即刷新
cont << nounitbuf; // 不设置立即刷新
```

#### 关联

```cpp
x.tie(&o) // x与o关联一起
```

### 文件输入输出

```cpp


```

#### 文件模式

1. 文件模式
std::ios::xxxx

+ `in`: 以读的方式打开。
+ `out`: 以写的方式打开。（截断）
+ `app`: 没错写操作都定位到文件结尾。
+ `ate`: 打开文件后立即定位到文件末尾。
+ `trunc`: 截断文件
+ `binary`: 二进制IO

## string流

`#include <sstream>`
流式对string的操作。

特有的操作
+ sstream strm 没有绑定stringstream对象。
+ sstream strm(s) 保存s的副本的sstream。
+ strm.str() 返回strm琐保存的string的拷贝。
+ strm.str(s) 将string s拷贝到strm中
