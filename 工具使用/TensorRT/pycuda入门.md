## CUDA基础

CUDA模型中的概念

+ host: CPU + 内存
+ device: GPU + 显存
+ CUDA程序一般都是CPU+GPU的异构计算

执行流程：

1. 分配host内存，并完成数据初始化。
2. 分配device内存， 并从host将数据拷贝到device上。
3. 调用CUDA的和函数在device上完成指定的运算。
4. 将device上的结果拷贝回host上。
5. 释放device和host分配的内存。

上面流程中最重要的一个过程是调用CUDA的核函数来执行并行计算，kernel是CUDA中一个重要的概念，kernel是在device上线程中并行执行的函数，核函数用__global__符号声明，在调用时需要用<<<grid, block>>>来指定kernel要执行的线程数量，在CUDA中，每一个线程都要执行核函数，并且每个线程会分配一个唯一的线程号thread ID，这个ID值可以通过核函数的内置变量threadIdx来获得。

+ `__global__`：在device上执行，从host中调用（一些特定的GPU也可以从device上调用），返回类型必须是void，不支持可变参数参数，不能成为类成员函数。注意用__global__定义的kernel是异步的，这意味着host不会等待kernel执行完就执行下一步。
+ `__device__`：在device上执行，单仅可以从device中调用，不可以和__global__同时用。
+ `__host__`：在host上执行，仅可以从host上调用，一般省略不写，不可以和__global__同时用，但可和__device__，此时函数会在device和host都编译。

要深刻理解kernel，必须要对kernel的线程层次结构有一个清晰的认识。首先GPU上很多并行化的轻量级线程。kernel在device上执行时实际上是启动很多线程，一个kernel所启动的所有线程称为一个网格（grid），同一个网格上的线程共享相同的全局内存空间，grid是线程结构的第一层次，而网格又可以分为很多线程块（block），一个线程块里面包含很多线程，这是第二个层次。线程两层组织结构如下图所示，这是一个gird和block均为2-dim的线程组织。grid和block都是定义为dim3类型的变量，dim3可以看成是包含三个无符号整数（x，y，z）成员的结构体变量，在定义时，缺省值初始化为1。因此grid和block可以灵活地定义为1-dim，2-dim以及3-dim结构，对于图中结构（主要水平方向为x轴），定义的grid和block如下所示，kernel在调用时也必须通过执行配置<<<grid, block>>>来指定kernel所使用的线程数及结构。

### Memory Pools

`pycuda.driver.mem_alloc()`和`pycuda.driver.pagelocked_empty()`如果非常频繁地调用它们，则会消耗大量的处理时间。

### 待排序

`pagelocked_empty(shape, dtype, order='C', mem_flag=o)`

对CUDA架构而言，主机端的内存被分类两种，一种是可分页内存（pageable memory）和页锁定内存（page-lock和pinned）。可分页内存是操作系统API malloc分配，页锁定内存是由CUDA函数cudaHostAlloc在主机上内存上分配的，页锁定内存的重要属性是主机的操作系统不会对分页进行交换，确保该内存始终驻留在物理内存中。GPU知道也锁定内存的物理地址可以通过DMA直接进行与主机进行内存交换。由于每个页锁定内存都需要分配物理内存，并且这些内存不能交换到磁盘上，所以页锁定内存比使用标准malloc()分配的可分页内存更消耗内存空间。


> https://zhuanlan.zhihu.com/p/34587739
> https://blog.csdn.net/dcrmg/article/details/54975432