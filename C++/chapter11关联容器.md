# 关联容器

主要两个两个容器 `map` 和 `set`。
`set`支持高效查询，而且没有重复。
`map`字典

8个容器三个维度

1. set或者map。
2. 允许重复和不允许重复。
3. 按顺序保存元素或者无须。

注：

+ 允许重复一般开头为 `multi`
+ 无序的开头一般是 `unordered`

## pair类型

在头文件`utility`中定义

pair就是将两个元素绑定在一起。在`map`中使用的一个单元就是`pair`对象。

```cpp
pair<T1, T2> p;
pair<T1, T2> p(v1, v2);
pair<T1, T2> p = {v1, v2};
make_pair(v1, v2)
p.first
p.second
p1 relop p2
```

## map的操作

```cpp
c.insert(v) // v是一个value_type类型的对象；args用来构造一个元素
c.emplace() // 对于map和set，只有当元素的关键字步走c中时才插入（或者构造）元素，函数返回一个pair，包换一个迭代器，指向具有指定关键字的元素，以及一个指令算法插入是否成功的bool值
c.insert(b, e) //b和e是迭代器，表示一个c::value_type 类型值的范围；il这种值的花括号列表。函数返回void
c.insert(il) // 对于map和set，值插入关键字步走c种的元素。对于multimap和multiset，则会插入范围种的每个元素
c.insert(p, v) // p是一个迭代器，指出去哪插入新元素。返回一个迭代器指向具有给定关键字的元素。
c.emplace(p, args)
c.erase(k) // k可以是迭代器，可以是元素 
```

统计单词

```cpp

map<string, size_z> word_count;
string word;
while (cin >> word) {
    // 插入一个元素 关键字等于word，值为1
    auto ret = word_count.insert({word, 1})
    if (!ret.second)
        ++(ret.first->second);
}

```

插入操作：
```cpp
c[k] // 返回key==k的元素，如果k不在c种，添加一个关键字为k的元素，对其进行初始化操作。
c.at(k)  // 访问k,如果k不存在，抛出一个out_of_range的异常。
```

`set`的访问元素：

```cpp
c.find(k)    //返回一个迭代器，指向第一个关键字为k的元素，若k步走容器种返回尾迭代器
c.count(k)   // 返回关键字等于k的元素的数量。对于不允许重复关键字的容器，返回值永远是0或者1

c.lower_bound(k)  // 返回一个迭代器，指向第一个关键词不小于k的元素
c.upper_bound(k)  // 返回一个迭代器，指向第一个关键字大于k的元素
c.equal_bound(k)  // 范围一个迭代器pair，表示关键字等于看元素的范围，如果不存在，两个成员均为c.end()
```

## 无序容器

使用hash实现。

这些都使用链hash去实现。因此我们可以管理链hash的桶
桶的接口：

+ `c.bucket_count()` 桶的个数。
+ `c.max_bucket_count()` 最大桶的个数。
+ `c.backet_size(n)` 第n个桶的内元素的数量。
+ `c.bucket(k)`  元素k在哪个桶中。

桶迭代：

+ `local_iterator` 桶的迭代器
+ `const_local_iterator` 桶的const迭代器
+ `c.begin() c.end()` 
+ `c.cbegin() c.cend()`
  
哈希策略

+ `c.load_factor()` 每个桶平均元素 float
+ `c.max_load_factor()` c试图维护的平均桶大小，返回float。 使得 load_factor <= max_load_factor
+ `c.rehash(n)` 重建存储，使得 bucket_count>=n，使得 bucket_count > size / max_load_factor
+ `c.reserve()` 