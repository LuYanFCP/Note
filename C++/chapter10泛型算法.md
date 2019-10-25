标准库并未给每个容器都定义那么多成应函数去实现查找特定元素、替换、删除等算法。而是定义了一组泛型算法去实现(generic algorithm),他们是公共操作。

大多数算法都定义在头algorithm中，还要一些数值泛型算法定义在numeric中。

## 基本概述

一般算法的特点：

1. 严重依赖迭代器
2. 依赖元素类型的操作。（比较大小之类，一般使用默认的，但很多时候也能自己指定）。、
3. 算法永远不会改变容器的大小，算法可能改变容器中保存的元素

## 基本的泛型算法

算法的基本形参模式：

1. alg(beg, end, other args)
2. alg(beg, end, dest, other args)
3. alg(beg, end, beg2, other args)
4. alg(beg, end, beg2, end2, other args)

算法接受的所有迭代器范围都是左闭右开

算法的命名规范：

1. 一些算法使用重载形式传递一个谓语。
    类似`unique(beg, end)`和`unique(beg, end, cmp)`
2. 一些算法为了避免重载歧意使用`_if`在后面做后缀。
    类似`find(beg, end, val)`和`find_if(beg, end, pred)`
3. 区分拷贝元素版本和不拷贝版本，会加入后缀`_copy`
    `reverse(beg, end)`和`reverse_copy(beg, end, dest)`，后者将逆序拷贝进dest内

特定容器算法：
一些特定的数据结构容器，比如说list，forward_list他们又独特的操作，是因为他们不支持随机访问迭代器，因此无法使用通用的`sort`、`merge`、`remove`、`reverse`。因此他们又独特成员函数去支持。
另外链表定义的其他算法的通用版本用于链表，但代价太高。这些算法需要交换输入序列中的元素。一个链表可以通过改变元素间的连接而不是复制元素。因此链表版本比通用版本好用。

算法的分类

**只读算法**
`accumulate(beg, end, sum_init)`

`equal(beg, end, beg1)`
**写容器算法**
`fill(beg, end, val)`

`fill_n(beg, n, val)`这个比较特别，之前有说算法不能增加容器的size，因此不要对空容器调用这个函数，会产生未定义行为。如果想在容器上写可以通过`back_inserter`这些插入迭代去实现。

**拷贝算法**
`replace(beg, end, search_val, replace_val)`和`replace(beg, end, search_val, beg2, replace_val)`把结果写入beg2中

**元素重排算法**
`unique`就是整理一些元素，覆盖相邻相等的元素，使得集合唯一，但容器的大小一直没变，返回的end_unique迭代器就是末尾。

## 定制操作

谓语：是一个可调用的表达式，传入若干个参数而会返回一个算法能作为条件的值。
例如：

```cpp
bool isShort(const string &s1, const string &s2) 
{
    return s1.size() < s2.size();
}

```

我们可以在一些算法中使用`isShort`去代替`<`。

### lambda表达式

c++的lambda表达式的基本形式`[capture list] (parameter list) -> return type {function body}`

```cpp
auto f = [] {return 42;}
f() // return 42
auto f1 = [] (int a, int b) {return a + b;}
f1(1, 2) // return 3
```

#### 捕获列表

可以捕获局部变量，分为值捕获和引用捕获

```cpp
sz = 10;
auto f1 = [v1] {return v1;}; // 直接将sz的值捕获进f1这个闭包的生命周期中了
auto f2 = [&v1] {return v1;} // 只是将引用捕获进闭包里面了
sz = 0;
f1() // return 10
f2() // return 0
```

当引用方式捕获一个变量时，一定要保证lambda执行时变量是存在的.

隐式捕获:

----
这里缺一张图
----

指定返回类型：默认情况下，如果一个lambda体系包含return之后的语句，则编译器假定此lambda返回void，这就照成了许多麻烦，因此需要手动的添加返回值。类如

```cpp
[](int i) {if (i < 0) return -i; else return i; } // 这条语句会出错
[](int i)->int {if (i < 0) return -i; else return i; }
```

## 参数绑定

类似与python中的`functools.partial()`可以固定一个或者几个参数返回一个可调用对象，这也可以使得普通函数也获得捕获局部变量的方式。使用标准库中的函数`bind`这个函数在头`functional`中

```cpp
auto newCallable = bind(callable, arg_list);
```

使用placeholder名字，即占位符。就是不会用bind绑定的参数，使用占位符去填充。

```cpp
using std::placeholders:_1
using std::placeholders:_2
....
```

可以使用`using namespace std::placeholders`直接全部导入。

```cpp
auto g = bind(f, a, b, _2, c, _1);
g(X,Y) -> f(a, b, Y, c, X)
// 因此我们可以通过bind实现参数顺序互换
auto f2 = bind(f1, _2, _1);
f2(X, Y) -> f1(Y, X)
// 如果是绑定引用 要使用标准库中的`cref`和`ref`函数
```

## 迭代器

按照功能去区分：

+ 插入迭代器（insert iterator）
+ 流式迭代器（stream iterator）绑定到输入输出流上了，可以用来遍历和关联IO流
+ 反向迭代器（reverse iterator）：除了forward_list都有反向迭代器
+ 移动迭代器（move iterator）：专门来移动elem

### 插入迭代器

+ back_inserter
+ front_inserter
+ inserter：`inserter(c, iter)`，`c是个容器，iter是迭代器`创建一个使用`insert`的迭代器。此函数接受第二个参数，这个参数必须是一个指向给定容器的迭代器。元素将被插入到给定迭代器所表示的元素之前。

这些`inserter_iter`只有有这些的容器才能使用。

### iostream迭代器

1. istream_iterator：
2. ostream_iterator：

### 反向迭代器

![反向迭代器](https://i.loli.net/2019/10/22/AElxy7whpMQTsKo.png)

`base()`：
![](https://i.loli.net/2019/10/22/LKuF6OdnTWowZrP.png)

![](https://i.loli.net/2019/10/22/fTAYc87FOi46stK.png)

### 迭代器类别

1. 输入迭代器：只读；不写；单遍扫描，只能递增。（find， accumulate要求的迭代器；istream_iterator）
2. 输出迭代器：只写；不读；单遍扫描，只能递增。（copy的第三个参数；ostream_iterator）
3. 前向迭代器：可读写；多遍扫描，只能递增。（replace要求前向迭代器，forward_list上的迭代器是前后迭代器）。
4. 双向迭代器：可读写；多遍扫描，可递增可递减。（reverse要求双向迭代器，除forward_list之外，其他标准库都符合双向迭代器）
5. 随机访问迭代器：可读写；多遍扫描，支持所有操作。（sort要求的；array、deque、string和vector的迭代器）