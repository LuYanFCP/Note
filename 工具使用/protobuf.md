## ProtoBuf简介

ProtoBuf 是google是一种轻便高效的结构化数据存储格式，可以用于结构化数据串行化，很适合做数据存储或RPC 数据交换格式。在TensorFlow和gRPC上有很好的应用。其作用类似于XML、json和yaml。

Protobuf包含序列化格式的定义、各种语言的库以及一个IDL编译器。正常情况下你需要定义proto文件，然后使用IDL编译器编译成你需要的语言。

## ProtoBuf3的更新

+ 移除了原始值字段的出现逻辑。
+ 移除了required字段
+ 移除了缺省值
+ 移除了unknown字段 （3.5中又加上了）
+ 移除了扩展，使用Any代替
+ 修复了未知的枚举值的语义
+ 添加了map类型
+ 添加了一些标准类似，比如time、动态数据的呈现
+ 可以使用JSON编码代替二进制proto编码

## Beginning

```proto
syntax = "proto3";

message SearchRequest {
    string query = 1;   // [type] fieldName = [fieldNumber]
    int32 page_num = 2;
    int result_per_page = 3; 
}
```

输入格式为: [type] fieldName = [fieldNumber];

type种类:

+ query
+ string
+ Oneof
+ Map

得到proto文件后，可以使用`protoc -I=. -I/usr/local/include -I=$(GOPATH)/src --go_out=. simple.proto` 其中`-I`是添加protobuf依赖（import内容）的寻找目标。`xx_out`是生成某语言的代码。

### 基本部分

1. 版本说明 `syntax="proto3"`
2. `import`其他文件，其中还要`public`和`weak`两种引入方式，weak引入不存在的文件，`public`具有传递性，如果你在文件中通过public引入第三方的proto文件，那么引入你这个文件同时也会引入第三方的proto。
3. `package` 包名，定义proto的包名，包名可以避免对message 类型之间的名字冲突，同名的Message可以通过package进行区分。
4. `repeated` 允许字段重复
5. 字段
   + 数字类型： double、float、int32、int64、uint32、uint64、sint32、sint64: 存储长度可变的浮点数、整数、无符号整数和有符号整数
   + 存储固定大小的数字类型：fixed32、fixed64、sfixed32、sfixed64: 存储空间固定
   + 布尔类型: bool
   + 字符串: string
   + bytes: 字节数组
   + messageType: 消息类型
   + enumType:枚举类型
   + 字段名、消息名、枚举类型名、map名、服务名等名称首字母必须是字母类型，然后可以是字母、数字或者下划线_。
6. `Oneof`类型：类似于C中的`Union`字段，但是`Oneof`允许你设置零各值，此字段不能使用repeated
7. `Map`类型：map<key,value> values = [序号]，其中`map`字段不能同时使用`repeated`。 
8. `Reserved`关键字：Reserved可以用来指明此message不使用某些字段，也就是忽略这些字段。
9. `enum`枚举类型：注意枚举类型的定义采用C++ scoping规则，也就是枚举值是枚举类型的兄弟类型，而不是子类型，所以避免在同一个package定义重名的枚举字段。第一个枚举值必须是0，而且必须定义。可以通过`option allow_alias = true`设置字段冲覅。
10. `Any`: 需要引入`google.protobuf.Any`去定义变量类型，一个`Any`以bytes呈现序列化的消息，并且包含一个URL作为这个类型的唯一标识和元数据。

## 编码

首先，我们先要了解`varint`方法。`varint`方法是一种使用变长方式表示整数的方法，可以使用有个或者多个字节来表示小整数和大整数，数越少，使用字节数越少。

### Varient方法

Varint 是一种紧凑的表示数字的方法。它用一个或多个字节来表示一个数字，值越小的数字使用越少的字节数。这能减少用来表示数字的字节数。比如对于 int32 类型的数字，一般需要 4 个 byte 来表示。但是采用 Varint，对于很小的 int32 类型的数字，则可以用 1 个 byte 来表示。当然凡事都有好的也有不好的一面，采用 Varint 表示法，大的数字则需要 5 个 byte 来表示。从统计的角度来说，一般不会所有的消息中的数字都是大数，因此大多数情况下，采用 Varint 后，可以用更少的字节数来表示数字信息

Varint 中的每个 byte 的最高位 bit 有特殊的含义，如果该位为 1，表示后续的 byte 也是该数字的一部分，如果该位为 0，则结束。其他的 7 个 bit 都用来表示数字。因此小于 128 的数字都可以用一个 byte 表示。大于 128 的数字，比如 300，会用两个字节来表示：1010 1100 0000 0010

![20191214174608.png](https://i.loli.net/2019/12/14/Ns9OburHyAYomqS.png)

事实上。Protobuf是编码的键值对，其中键用varint来表示，其中后三位代表wire type。

![20191214180329.png](https://i.loli.net/2019/12/14/zGqDagQbLNpxhWX.png)

数据使用如下步骤组织：

![20191214182748.png](https://i.loli.net/2019/12/14/s6rwFRyPBXSeCzg.png)

Proto3中对数字类型的repeated字段采用pack处理方式，同一个repeated元素共享同一个key，之后是字段的整体字节长度，然后是各个元素。因为数字类型天生具有可区分性，不需要额外的分隔符进行区分。

之后额外说
---
> `option java_package = "com.example.foo"`其定义`option optionName = constant;`字面意思是可选的意思，具体protobuf里面怎么处理这个字段呢，就是protobuf处理的时候另外加了一个bool的变量，用来标记这个optional字段是否有值，发送方在发送的时候，如果这个字段有值，那么就给bool变量标记为true，否则就标记为false，接收方在收到这个字段的同时，也会收到发送方同时发送的bool变量，拿着bool变量就知道这个字段是否有值了，这就是option的意思。


> https://colobu.com/2019/10/03/protobuf-ultimate-tutorial-in-go/
> https://www.ibm.com/developerworks/cn/linux/l-cn-gpb/index.html
> https://www.cnblogs.com/smark/archive/2012/05/03/2480034.html