## 基本概念

跨平台，使用平台无关的文件`CMakeList.txt`，生成`Makefile`或者其他平台的工程配置文件。

使用思路：

1. 编写 `CMake`的配置文件`CMakeList.txt`
2. 执行命令`cmake <Path>` 或者 `ccmake <Path>`生成`Makefile`，其中`<Path>`是`CMakeList.txt`所在的目录
3. 生成工程配置文件，使用其编译

### 基本的参数

+ `cmake_minimum_required (VERSION <version>)`：cmake的版本控制
+ `Project (<projectName>)`:
+ `add_executable(<targetName>, <source list>)`: 产生可执行文件
+ `add_source_directory(<dir>, <variable>)` 将dir中所有源文件变量赋值给`variable`。

#### 多目录，多源文件编译

目录结构

```
./Demo3
    |
    +--- main.cc
    |
    +--- math/
          |
          +--- MathFunctions.cc
          |
          +--- MathFunctions.h
          |
          +--- CMakeLists.txt
    |
    +--- CMakeLists.txt
```

主目录的`CMakeLists.txt`的内容

```cmake
# CMake 最低版本号要求
cmake_minimum_required (VERSION 2.8)
# 项目信息
project (Demo3)
# 查找当前目录下的所有源文件
# 并将名称保存到 DIR_SRCS 变量
aux_source_directory(. DIR_SRCS)
# 添加 math 子目录
add_subdirectory(math)
# 指定生成目标
add_executable(Demo main.cc)
# 添加链接库
target_link_libraries(Demo MathFunctions)
```

math目录下的`CMakeLists.txt`内容

```cmake
# 查找当前目录下的所有源文件
# 并将名称保存到 DIR_LIB_SRCS 变量
aux_source_directory(. DIR_LIB_SRCS)
# 生成链接库
add_library (MathFunctions ${DIR_LIB_SRCS})
```

首先主目录的的`cmake`使用`add_subdirectory(<subdir>)`。在这一句的时候会自动执行子目录的`cmake`，根据子目录的`cmake`可知，子目录为生成一个动态链接库`.a`文件，然后通过主目录的`target_link_libraries`链接到主文件上。

## 自定义编译

CMake 允许为项目增加编译选项，从而可以根据用户的环境和需求选择最合适的编译方案。

例如，可以将 MathFunctions 库设为一个可选的库，如果该选项为 `ON` ，就使用该库定义的数学函数来进行运算。否则就调用标准库中的数学函数库。


### 安装与测试

首先先在 math/CMakeLists.txt 文件里添加下面两行：

```cmake
# 指定 MathFunctions 库的安装路径
install (TARGETS MathFunctions DESTINATION bin)
install (FILES MathFunctions.h DESTINATION include)
```

同样也可以在根目录指定
install (TARGETS Demo DESTINATION bin)
install (FILES "${PROJECT_BINARY_DIR}/config.h"
         DESTINATION include)

之后如果允许`make`的话，产生的文件会被放到`/usr/local/bin`和`/usr/local/include`里面。

#### 测试

可以使用cmake来生成测试文件，从而执行测试

```cmake
# 启用测试
enable_testing()
# 测试程序是否成功运行
add_test (test_run Demo 5 2)
# 测试帮助信息是否可以正常提示
add_test (test_usage Demo)
set_tests_properties (test_usage
  PROPERTIES PASS_REGULAR_EXPRESSION "Usage: .* base exponent") 
# 测试 5 的平方
add_test (test_5_2 Demo 5 2)
set_tests_properties (test_5_2
 PROPERTIES PASS_REGULAR_EXPRESSION "is 25")
# 测试 10 的 5 次方
add_test (test_10_5 Demo 10 5)
set_tests_properties (test_10_5
 PROPERTIES PASS_REGULAR_EXPRESSION "is 100000")
# 测试 2 的 10 次方
add_test (test_2_10 Demo 2 10)
set_tests_properties (test_2_10
 PROPERTIES PASS_REGULAR_EXPRESSION "is 1024")
```

其中: 
PROPERTIES(properties)
PASS_REGULAR_EXPRESSION(pass_regular_expression)
然后后面跟着表达式，具体参考`CTest`