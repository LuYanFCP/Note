## 动态内存与智能指针

静态内存和栈内存，静态内存保存局部static 类static以及定义在任何函数之后的遍历。栈保存非static对象。着两个内存的对象都由编译器创建和销毁。栈对象运行才存在，static对象在使用前分配，程序结束就销毁。

除了这部分还要一个自由空间又叫堆，可以存储动态分配的对象。

两种智能指针：
+ `shared_ptr` 运行多个指针指向同一个对象。
+ `unique_ptr` 独占所指向的对象。
+ `weak_ptr` 伴随类，它是一个弱引用，指向`share_ptr`所管理的对象，着三种类型都定义在`memory`头文件中。
  
智能指针都支持的操作

+ *p 解引用
+ p->mem 等价于 (*p).mem
+ p.get() 返回p中保存的指针，如果智能指针释放了对象，这个就悬空了
+ swap(p, q) 交换p和q => p.swap(q)

`shared_ptr`独有的

+ make_shared<T>(args) 返回一个shared_ptr
+ shared_ptr<T>p(q) p是shared_ptr q的拷贝，此从中会递增q中的计数器。q中的指针必须能转换为`T*`
+ p = q p和q都是shared_ptr，所保存的指针必须能互相转换。此操作会递减p的引用激素，递增q的引用技术；若p的引用计数为，则将其管理的原内存释放
+ p.unique() 如果p.use_count() 为1，则是true
+ p.use_count() 返回共享对象指针数目。

share_ptr在无用在无用之后仍然会保持一段时间可能为：你将share_ptr放到了一个容器中，随后重排了容器，从而不再需要这些数据，这种情况下你应该确保使用`erase`去删除那些shared_ptr元素。

### 使用了动态生存期的资源的类

使用动态内存处于一下三个原因之一：

1. 程序不知道自己需要使用多少对象。（容器）
2. 程序不知道所需对象的准确类型。
3. 程序需要在多个对象间共享数据。

### shared_ptr 和 new 结合使用

接受指针参数的智能指针的构造函数是`explicit`的（有这个的关键字必须显示构造）。
只能使用 shared_ptr<T> p2(new xxx) 不能使用 shared_ptr<T> p2 = new xxxx

默认情况下，一个用来初始化智能指针的普通指针必须指向动态内存，因为智能指针默认使用delete释放它所关联的对象。我们可以将智能指针绑定在一个指向其他类型资源的指针上，但是这样做，必须提供自己的操作来代替delete

定义和改变`shared_ptr`

+ `shared_ptr<T> p(q)` p管理内置指针去q所指向的对象，q必须是new分配的内存，且能转换为T
+ `shared_ptr<T> p(u)` p从unique_ptr u那接管了对象的使用权；讲u置空。
+ `shared_ptr<T> p(q, d)` p接管了内置指针q所指向的对象的所有权。q必须能转换为`T*`类型。p将使用可调用对象来delete
+ `shared_ptr<T> p(p2, d)`
+ `p.reset()` 若p是唯一指向其对象的shared_ptr，reset会释放此对象。，如果传递了可选参数内置指针`q`，会令p指向q，否者将p置空。如传递了参数d则会调用d来delete `q`。

### 三个问题

#### 不要混用普通指针和智能指针

```c++
void process(shared_ptr<int> ptr)
{
    xxx;
}

int *x(new int(1024));
process(x); // 错误， 因为普通指针转换为 智能指针必须要显式定义
process(shared_ptr<int> (x)); // 合法但是出来的时候会释放内存

int j = *x // 危险
```

#### 不要使用get初始化另一个智能指针或为智能指针赋值

```c++
share_ptr<int> p(new int(42));
int *q = p.get();
{
    share_ptr<int>(q);
}
int foo = *p; // 已经被销毁

```

#### 其他的shared_ptr操作

```c++
p = new int(1024);

```

#### 使用shared_ptr的重要性

shared_ptr无论程序在局部是否正确结束，都可以释放所持有的内存。但自己new出来的内存就无法做到这样

```c++
{
    shared_ptr<int> (new int(1024));
}// 无论正常结束还是出现异常都可以释放内存

{
    int *p = new int(1024);
    // 如果这里出现异常，这个内存是不会被释放的
    delete p;
}

```

也可以使用智能指针的一些性质控制资源的释放，例如使用智能指针去控制web connect的连接与释放。

```c++
struct destination;
struct connection;
connection connect(destination*);

void disconnect(connection);

void end_connection(connection *p) {disconnect(*p);};
void f(destination &d)
{
    connection c = connect(&d);
     // 如果忘记调用disconnect释放的话就会出现问题
     /*可以这样做*/
     shared_ptr<connection> p(&c, end_connection);
}
```

#### 陷阱总结

+ 不使用相同的内置指针值初始化（或者reset）**多个智能指针**。
+ 不delete get() 返回的指针
+ 不适用get() 初始化或者reset另一个智能指针。
+ 如果你使用get()返回的指针，记住当最后一个对应的智能指针销毁后，你的指针就变的无效。
+ **如果你使用智能指针管理的资源不是new分配的内存，记住传递给它一个删除器。**

### unique_ptr

一个`unique_ptr` 拥有它所指向的对象，只能指向一个吗，它没有`make_shared`这样的函数返回一个`unique_ptr`，只能使用new 返回的指针进行初始化。

`unique_ptr`不支持普通的拷贝和赋值

+ `unique_ptr<T> u1` 空`unique_ptr`，可以指定类型为T的对象。u1会使用delete来释放指针； u2会使用一个类型为D的可调用对象来释放它的指针。
+ `unique_ptr<T, D> u2`
+ `unique_ptr<T, D> u(d)`
+ `u = nullptr` 释放u指向的对象。
+ `u.release()` u放弃对指针的控制权，返回指针（原来存储的），并将u置为空。
+ `u.reset()` 释放u指向的对象
+ `u.reset(q)` 如果提供了内置指针q，令u指向这个对象；否则将u置为空。
+ `u.reset(nullptr)`

#### 传递删除器

```c++
void f(destination &d)
{
    connect c = connect(&d); // 打开连接
    // 定义指针
    unique_ptr<connection, decltype(end_connection)*> p(&c, end_connection);
    // 使用连接
}

```

其中decltype来指明函数指针的类型。由于decltype(end_connection)返回一个函数类型，所有我们必须添加一个`*`来知名我们正在使用该类型的指针。

## weak_ptr

不控制所指对象生存周期的智能指针，它指向由一个`shared_ptr`管理对象。将一个`weak_ptr`绑定到一个`shared_ptr`不会改变`shared_ptr`的引用计数。一旦最后一个指向对象的`shared_ptr`被销毁，对象就会被释放。即使有`weak_ptr`指向对象，对象就会被释放，因此，`weak_ptr`的名字抓住了这种共享指针弱的特点。

+ `weak_ptr<T> w` 空`weak_ptr`可以指向类型为`T`的对象。
+ `weak_ptr<T> w(sp)` 与`shared_ptr sp`指向相同对象的`weak_ptr`。`T`必须转换为sp指向的类型。
+ `w = p` p可以是一个shared_ptr 或者一个 weak_ptr，共享对象。
+ `w.reset()` 将w置为空。
+ `w.use_count()` 与w共享对象的shared_ptr的数量
+ `w.expired()` 若w.use_count() 为0，返回true，否则返回false
+ `w.lock()` 如果expired为true， 返回一个空的shared_ptr，否则则返回w所指的shared_ptr
  
