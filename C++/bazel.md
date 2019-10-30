
# Bazel 编译入门

## workspace 
使用bazel构建和编译的时候首先创建一个`WORKSPACE`。`WORKSPACE`一般用来放置项目的source和Bazek的输出
一般来说存放`WORKSPACE`的文件，该目录将目录及其内容标识为Bazel工作区，并位于项目目录结构的根目录中。
项目里面一般有多个`BUILD`文件，在根文件中的`BUILD`

## build

### build文件

`BUILD`文件中最重要的是`build rule`，它告诉`Bazel`文件中其外的输出，例如一个可执行文件和lib。
`BUILD`文件中构建规则中的每一个实例都称为一个目标，并指向一组依赖的源文件和依赖项，也可以指向其他目标

```

cc_binary (
    name = "hello-world",
    srcs = ["hello-world.cpp"]
)
```

其中`cc_binary`指的是将cpp编译目标为二进制。
name 这个属性是必须要有，其他的东西可以是待选项， 例如`srcs`是指源文件，`deps`是指代的依赖文件， `hdrs`是头文件位置。

`cc_library`是编译库使用的


还有一个`visibility`参数，可以提供一些跨文件的库的交互。例如如果`lib`文件中编译了很多库，需要在`main`文件中编译时被链接，因此就可以在`lib`下的`BUILD`文件中的某个`cc_library`中去添加`visibility = ["//main:__pkg__"]`这样就可以直接使用`//lib:yyy`去访问到库了。
这是因为默认情况下，目标仅对同一`BUILD`文件中的其他目标可见。 （Bazel使用目标可见性来防止诸如包含实现详细信息的库之类的问题泄漏到公共API中。）

### build一个项目

使用`BUILD`文件进行build，指令`bazel build //xxx:yyy` 其中`//`表示工作目录，也就是`WORKSPACE`，xxx指代的是文件结构。:后面的`yyy`就是`BUILD`文件中具体的指令。

### 查看项目依赖

构建完成的后，可以将所有依赖显示出来。Bazel使用这些语句来创建项目的依赖关系图，从而实现准确的增量构建。

`linux`平台:
首先先安装 `graphviz`和`xdot`，这两个工具可以帮助实现`build`可视化

```shell
sudo apt update && sudo apt install graphviz xdot
```

然后使用 `query`指令产生的 `graphviz`的图使用`xdot`进行可视化

``` shell 
xdot <(bazel query --notool_deps --noimplicit_deps 'deps(//main:hello-world)' \
  --output graph)
```