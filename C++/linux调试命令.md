## 调试指令 

+ `file`: 查看文件的基本信息，可以看ELF
+ `ldd`: 查看依赖库
+ `nm`: 产看ELF文件信息， 可以通过这个来获取是否有某个函数或者变量。
+ `size`: 统计个字段的长度(字节大小)
+ `strip`: 去掉elf文件的所以符号信息
+ `readelf`: 读取`elf`的信息
+ `objdump`: 反汇编指令。
+ `netstat -anp | grep 端口`: 查看端口占用情况

core dump文件，很多时候出现了core dump但是却没有 core文件。

+ `unlimit -c` 查看core文件配置，如果是0，则没有core文件。
+ `unlimit -c unlimited`： 不限制生成core文件的大小
+ `unlimit -c 10`: 设置最大生成为10kb

addr2line 如果程序崩溃了没有core文件，通过dmesg命令获取，dmesg命令会输出所以崩溃的文件信息，出错原因和出错位置。

然后使用`addr2line -e [file] [ip]`就可得到位置

## gdb

### 调试core dump

`gdb processFile PID` 调试正在运行的程序

`gdb file core` 调试出现coredump的程序

`(gdb) bt`: 踹下你core dump的位置

### gdb调试的前提

使用带有调试标志（debugging flags）的方式编译代码

```bash
gcc -g file
g++ -g file
```

### gdb的使用

`gdb [file]`

### gdb的经典操作

+ `run(r)`: 运行程序遇到断点停下来,等待用户下一步操作
+ `continue(c)`: 跳到下一个断点处
+ `next(n)`: **单步跟踪程序，当遇到函数调用时，也不进入此函数体；**此命令同`step`的主要区别是，**`step`遇到用户自定义的函数，将步进到函数中去运行，而`next`则直接调用函数，不会进入到函数体内。**
+ `step(s)`: 同上
+ `until`: 当你厌倦了在一个循环体内单步跟踪时，这个命令可以运行程序直到退出循环体。
+ `until+行号`: 运行至某行，不仅仅用来跳出循环
+ `finish`: 运行程序，直到当前函数完成返回，并打印函数返回时的堆栈地址和返回值及参数值等信息。
+ `call`: 函数(参数)：调用程序中可见的函数，并传递“参数”，如：call gdb_test(55)
+ `quit(q)`: 退出gdb

设置断点

+ `break(b) n`: 在第n行处设置断点
（可以带上代码路径和代码名称： b OAGUPDATE.cpp:578）
+ `b fn1 if a＞b`: 条件断点设置
break func（break缩写为b）：在函数func()的入口处设置断点，如：break cb_button
+ `delete 断点号n`: 删除第n个断点
+ `disable 断点号n`: 暂停第n个断点
+ `enable 断点号n`: 开启第n个断点
+ `clear 行号n`: 清除第n行的断点
+ `info b (info breakpoints)`: 显示当前程序的断点设置情况
+ `delete breakpoints`: 清除所有断点：

查看源代码

+ `list(l)`: 其作用就是列出程序的源代码，默认每次显示10行。
+ `list 行号`: 将显示当前文件以“行号”为中心的前后10行代码，如：list 12
+ `list 函数名`: 将显示“函数名”所在函数的源代码，如：list main

打印表达式

+ `print(p) 表达式`: 其中“表达式”可以是任何当前正在被测试程序的有效表达式，比如当前正在调试C语言的程序，那么“表达式”可以是任何C语言的有效表达式，包括数字，变量甚至是函数调用。
  + `print a`: 将显示整数 a 的值
  + `print ++a`: 将把 a 中的值加1,并显示出来
  + `print name`: 将显示字符串 name 的值
  + `print gdb_test(22)`: 将以整数22作为参数调用gdb_test() 函数
  + `print gdb_test(a)`: 将以变量 a 作为参数调用 gdb_test() 函数
+ `display 表达式`: 在单步运行时将非常有用，使用display命令设置一个表达式后，它将在每次单步进行指令后，紧接着输出被设置的表达式及值。如： display a
+ `watch 表达式`: 设置一个监视点，一旦被监视的“表达式”的值改变，gdb将强行终止正在被调试的程序。如: watch a
+ `whatis`: 查询变量或函数
+ `info function`: 查询函数
+ `info locals`: 显示当前堆栈页的所有变量

查询运行信息
+ `where/bt`: 当前运行的堆栈列表；
+ `bt backtrace`: 显示当前调用堆栈
+ `up/down` 改变堆栈显示的深度
+ `set args` 参数:指定运行时的参数
+ `show args`: 查看设置好的参数
+ `info program`: 来查看程序的是否在运行，进程号，被暂停的原因。

分割窗口
+ `layout`：用于分割窗口，可以一边查看代码，一边测试：
+ `layout src`：显示源代码窗口
+ `layout asm`：显示反汇编窗口
+ `layout regs`：显示源代码/反汇编和CPU寄存器窗口
+ `layout split`：显示源代码和反汇编窗口
+ `Ctrl + L`：刷新窗口

### 内存的越界定位与处理

使用`Address Sanitize`工具分析。
在`gcc/clang`上加上选项

+ `-fsanitize=address`
+ `-fsanitize=leak` 只能使用`Leak Sanitize`,检测内存泄漏问题.
+ `-fno-omit-frame-pointer`: 检测到内存错误时打印函数调用栈



### AddressSanitizer基本介绍

运行时库替换了malloc和free函数。多分配区域（红色区域）周围的内存中毒。释放的内存将被并中毒。编译器以下列方式转换程序中的每个内存访问：
将

```c++
*address = ...;  // or: ... = *address;
```

转换为:

```c++
if (IsPoisoned(address)) {
  ReportError(address, kAccessSize, kIsWrite);
}
*address = ...;  // or: ... = *address;
```

核心就是实现`IsPoisoned`

#### 内存映射和检测

虚拟地址空间分为2个不相交的类：

+ Main application memory（Mem）：常规应用程序代码使用此内存
+ Shadow memory (Shadow)：此内存包含影子值（或meta）。影子和主应用程序内存之间存在对应关系。将主存储器中的一个字节中毒意味着将一些特殊值写入相应的影子存储器。

这两类存储器的组织方式应使影子存储器（MemToShadow）的计算速度更快

```c++
shadow_address = MemToShadow(address);
if (ShadowIsPoisoned(shadow_address)) {
  ReportError(address, kAccessSize, kIsWrite);
}
```

#### 映射

`AddressSanitizer` 用 1 byte 的影子内存，记录主内存中 8 bytes 的数据。
**因为malloc分配内存是按照 8 bytes 对齐。**

这样，8 bytes 的主内存，共构成 9 种不同情况：

+ 8 bytes 的数据可读写，影子内存中的value值为 0
+ 8 bytes 的数据不可读写，影子内存中的value值为 负数
+ 前 k bytes 可读写，后 (8 - k) bytes 不可读写，影子内存中的value值为 k 。

整个判断流程可以记为如下:

```c++
byte *shadow_address = MemToShadow(address);
byte shadow_value = *shadow_address;
if (shadow_value) {
  if (SlowPathCheck(shadow_value, address, kAccessSize)) {
    ReportError(address, kAccessSize, kIsWrite);
  }
}
```

其中判断函数`SlowPathCheck`的函数如下:

```c++
// Check the cases where we access first k bytes of the qword
// and these k bytes are unpoisoned.
bool SlowPathCheck(shadow_value, address, kAccessSize) {
  last_accessed_byte = (address & 7) + kAccessSize - 1;
  return (last_accessed_byte >= shadow_value);
}
```

MemToShadow（ShadowAddr）属于无法寻址的ShadowGap区域。因此，如果程序尝试直接访问阴影区域中的内存位置，它将崩溃。

#### MemToShadow的映射方式

64-bit:

```c++
Shadow = (Mem >> 3) + 0x7fff8000;
```

+ HighMem [0x10007fff8000, 0x7fffffffffff]
+ HighShadow [0x02008fff7000, 0x10007fff7fff]
+ ShadowGap [0x00008fff7000, 0x02008fff6fff]
+ LowShadow [0x00007fff8000, 0x00008fff6fff]
+ LowMem [0x000000000000, 0x00007fff7fff]

32-bit:

```c++
Shadow = (Mem >> 3) + 0x20000000;
```

+ HighMem [0x40000000, 0xffffffff]
+ HighShadow [0x28000000, 0x3fffffff]
+ ShadowGap [0x24000000, 0x27ffffff]
+ LowShadow [0x20000000, 0x23ffffff]
+ LowMem [0x00000000, 0x1fffffff]

#### stack

为了捕获堆栈缓冲区溢出，AddressSanitizer对代码进行如下检测：

```c++
void foo() {
  char a[8];
  ...
  return;
}
```

之后编译器通过插入代码:

```c++
void foo() {
  char redzone1[32];  // 32-byte aligned
  char a[8];          // 32-byte aligned
  char redzone2[24];
  char redzone3[32];  // 32-byte aligned
  int  *shadow_base = MemToShadow(redzone1);
  shadow_base[0] = 0xffffffff;  // poison redzone1
  shadow_base[1] = 0xffffff00;  // poison redzone2, unpoison 'a'
  shadow_base[2] = 0xffffffff;  // poison redzone3
  ...
  shadow_base[0] = shadow_base[1] = shadow_base[2] = 0; // unpoison all
  return;
}
```

## Sanitizer

ASAN最早可以追溯到 LLVM 的 sanitizers项目（https://github.com/google/sanitizers），这个项目包含了

+ `AddressSanitizer`
+ `MemorySanitizer`
+ `ThreadSanitizer`
+ `LeakSanitizer`

其中`AddressSanitizer`可以用作如下情况的检测

+ Use after free (dangling pointer dereference)
+ Heap buffer overflow
```c++
int *a = (int*)malloc(sizeof(int) * 100);
a[100] = 1;
```
+ Stack buffer overflow
```c++
int a[100];
a[100] = 1;
```
+ Global buffer overflow: 全局的stack溢出
+ Use after return
+ Use after scope
+ Initialization order bugs
+ Memory leaks

一般来说为了达到合理的性能使用`-O1`以上的优化.  

参考
---------
https://zhuanlan.zhihu.com/p/37515148
https://github.com/google/sanitizers/wiki/AddressSanitizerAlgorithm
https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/gdb.html#gdb
https://github.com/google/sanitizers