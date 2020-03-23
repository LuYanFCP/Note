# TX中Pytorch的编译与使用

## 编译

### 编译前置准备

#### 平台

试验环境与平台

+ 试验平台:TX2
+ jetpack3.3
+ ubuntu 16.04
+ pytorch 1.10
+ python 3.5

额外需要的环境变量

```bash
export CUDNN_INCLUDE_DIR=/usr/include
export CUDNN_LIB_DIR=/usr/lib/aarch64-linux-gnu
```

前置依赖-本地库

```bash
sudo apt-get install libopenblas-dev libatlas-dev checkinstall protobuf
```

前置依赖-python

```bash
pip3 install -r requirements.txt
```

### Pytorch源码的处理

首先介绍一些pytorch源码编译的基本结构
+ setup.py build
+ build_deps(setup.py)
  + build_caffe2(tools/build_pytorch_libs.py) 在这一步函数判断使用何种方式进行编译，比如使用cmake，或者ninja，一般采用cmake即可。（如果需要具体的编译过程，可以查看编译后产生的`build/CMakeCache.txt`的文件。
+ ext_modules
  + C
    + Tensor
    + autograd
    + cuda、cudnn
  + DL
  + THNN
  + THCNN
  
#### 克隆

```bash
export PYTORCH_VSION=v1.1.0
git clone --branch <version> --recursive https://github.com/pytorch/pytorch.git
cd pytorch
```

**注意：--recursive必须有，pytorch项目中有大量的子项目都需要递归的clone下来。**

#### 对源码的一些修改

**本节会根据报错，进行分析和对源码部分的修改**

##### 问题1：在编译caffe2的过程中会大量出现nvlink错误，错误信息为找不到NCCL的相关链接库
![](http://q52k1g9if.bkt.clouddn.com/images20200202185413.png)
类似如上的结果

出现问题的原因：NCCL是用于Pytorch分布式训练中使用的卡之间的通信程序。由于TX2上的Pytorch只作为推理进行使用，另外TX2也没办法/没有安装NCCL，因此需要将NCCL禁止。

通过对源码的追踪发现，所有关于NCCL的一些`Flag`的定义在源码`tools/setup_helpers/nccl.py`文件中，因此将起出现的`USE_NCCL`，`USE_SYSTEM_NCCL`，等参数全部设定为`False`即可。
可使用cmake生成make文件的输出信息加以确实其是否被关闭。

##### 问题2： 运行时错误 cuda runtime error (7) : too many resources requested for lanch a /xxxxx/pytorch/THCUNN/generic/SpatialUpSamplingBilinear.cu 67

这个错误主要是在于使用`SpatialUpSamplingBilinear`时线程数为1024（pytorch默认），而TX2中的cuda核心并没有那么多资源，因此出现了申请不到资源的情况。解决手段
1. `aten/src/THCUNN/generic/SpatialUpSamplingBilinear.cu` 文件中的62行和98行的位置做如下处理
```c++
// const int num_threads =
//      at::cuda::getCurrentDeviceProperties()->maxThreadsPerBlock;
const int num_threads = 512;
```
2. 重新编译即可

还有一种一次性结局的办法就是，将下述补丁打到应有的位置(https://github.com/pytorch/pytorch/issues/8103)

```diff
diff --git a/aten/src/ATen/cuda/CUDAContext.cpp b/aten/src/ATen/cuda/CUDAContext.cpp
index 70a7d05b6..48bf1173e 100644
--- a/aten/src/ATen/cuda/CUDAContext.cpp
+++ b/aten/src/ATen/cuda/CUDAContext.cpp
@@ -24,6 +24,8 @@ void initCUDAContextVectors() {
 void initDeviceProperty(DeviceIndex device_index) {
   cudaDeviceProp device_prop;
   AT_CUDA_CHECK(cudaGetDeviceProperties(&device_prop, device_index));
+  // patch for "too many resources requested for launch"
+  device_prop.maxThreadsPerBlock = device_prop.maxThreadsPerBlock / 2;
   device_properties[device_index] = device_prop;
 }
 
diff --git a/aten/src/ATen/cuda/detail/KernelUtils.h b/aten/src/ATen/cuda/detail/KernelUtils.h
index e535f4d83..ac057c504 100644
--- a/aten/src/ATen/cuda/detail/KernelUtils.h
+++ b/aten/src/ATen/cuda/detail/KernelUtils.h
@@ -12,7 +12,10 @@ namespace at { namespace cuda { namespace detail {
   for (int i = blockIdx.x * blockDim.x + threadIdx.x; i < (n); i += blockDim.x * gridDim.x)
 
 // Use 1024 threads per block, which requires cuda sm_2x or above
-constexpr int CUDA_NUM_THREADS = 1024;
+//constexpr int CUDA_NUM_THREADS = 1024;
+
+// patch for "too many resources requested for launch"
+constexpr int CUDA_NUM_THREADS = 512;
 
 // CUDA: number of blocks for threads.
 inline int GET_BLOCKS(const int N)
diff --git a/aten/src/THCUNN/common.h b/aten/src/THCUNN/common.h
index 9e3ed7d85..08fcb4532 100644
--- a/aten/src/THCUNN/common.h
+++ b/aten/src/THCUNN/common.h
@@ -9,7 +9,10 @@
   "Some of weight/gradient/input tensors are located on different GPUs. Please move them to a single one.")
 
 // Use 1024 threads per block, which requires cuda sm_2x or above
-const int CUDA_NUM_THREADS = 1024;
+//const int CUDA_NUM_THREADS = 1024;
+
+// patch for "too many resources requested for launch"
+const int CUDA_NUM_THREADS = 512;
 
 // CUDA: number of blocks for threads.
 inline int GET_BLOCKS(const int N)
```

##### 问题3 在使用cuda做在GPU上做3维以上矩阵的一些求逆求、分解等工作是出现 找不到`MAGMA lib`

这个问题是由于高阶矩阵/张量在GPU上这些复杂操作是直接使用MAGMA库中的操作，因此在运行时动态链接会报错。

TX2上编译`MAGMA lib`还比较复杂，其本身对`arm`的支持也不清楚。我尝试编译了几版，也使用`GitHub`中的`pytorch-builder`进行配置，依旧无法使用。

因此**如果矩阵的不大的话推荐使用，cpu进行操作。**

### 编译

```bash
python3 setup.py build
python3 setup.py bdist_wheel # 生成wheel包
cd dist && pip3 install torch-1.1.0-cp35-cp35m-linux_aarch64.whl  
```

#### 编译后容易出现的问题

1. 找不到`torch._C`： 这个主要的问题是编译后，有些动态链接库的名字不规范，没有改到应有的格式。
进入`site-package/torch/` 目录下面把`_C.xxxxxx.so` 和`_dll.xxx.so` 改成 `_C.so` 和 `_dll.so`。（https://github.com/pytorch/pytorch/issues/574）

#### 已经编译好的包

我会陆续的将编译好的各个版本的`arm`平台`Pytorch`的`wheel`放到`GitLab`。 如果有什么问题请在下面评论或者在`GitLab`上发`issue`。