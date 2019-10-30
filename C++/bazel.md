# Bazel 编译入门

## workspace 
使用bazel构建和编译的时候首先创建一个`WORKSPACE`。`WORKSPACE`一般用来放置项目的source和Bazek的输出
一般来说存放`WORKSPACE`的文件，该目录将目录及其内容标识为Bazel工作区，并位于项目目录结构的根目录中。
项目里面一般有多个`BUILD`文件，在根文件中的`BUILD`

## build

`BUILD`文件中最重要的是`build rule`，它告诉`Bazel`文件中其外的输出，例如一个可执行文件和lib。
`BUILD`文件中构建规则中的每一个实例都称为一个目标，并指向一组依赖的源文件和依赖项，也可以指向其他目标

```
cc_bin (
    name = "hello-world",
    srcs = ["hello-world.cpp"]
)
```
name 这个属性是必须要有，其他的东西可以是待选项。

### build一个项目


### 查看项目依赖

构建完成的后，可以将所有依赖显示出来。Bazel使用这些语句来创建项目的依赖关系图，从而实现准确的增量构建。




`visibility`参数，这是因为默认情况下，目标仅对同一BUILD文件中的其他目标可见。 （Bazel使用目标可见性来防止诸如包含实现详细信息的库之类的问题泄漏到公共API中。）