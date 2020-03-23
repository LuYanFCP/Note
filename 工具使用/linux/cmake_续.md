# 链接库

## add_library


> add_library(<name> [STATIC | SHARED | MODULE] [EXCLUDE_FROM_ALL] source1 [source2 ...])

+ STATIC， 代表静态链接库
+ SHARED，代表动态链接库
+ MODULE，是一些插件，运行时候使用dlopen-like的功能进行动态加载

+ EXCLUDE_FROM_ALL 会在目标文件上设置相应的属性（执行默认make的时候，这个目标文件会被排除在外，不被编译）

## target_include_directories

> target_include_directories(<target>[SYSTEM] [BEFORE] <INTERFACE|PUBLIC|PRIVATE> [items1...] [<INTERFACE|PUBLIC|PRIVATE> [items2...] ...])

增加include