# windows文件系统的链接

之前为了打比赛，需要将数据放入代码的文件夹，由于代码防止代码文件夹过于臃肿因此想找到如同linux 软链接的方式去链接文件。

找到windows中的链接指令

## mklink命令(CMD.exe)

语法

```cmd
mklink
MKLINK [[/D] | [/H] | [/J]] Link Target
        /D      创建目录符号链接。默认为文件
                符号链接。
        /H      创建硬链接而非符号链接。
        /J      创建目录联接。
        Link    指定新的符号链接名称。
        Target  指定新链接引用的路径
                (相对或绝对)。
```

### 默认

默认情况下是对文件的链接：产生链接文件的类型为.symlink，图标是快捷方式的图标。

### /D

文件夹软连接，产生的文件类型为文件夹，图标是快捷方式的图标。

```cmd
> mklink /D bbb aaa
为 bbb <<===>> aaa 创建的符号链接
```

![](https://img2020.cnblogs.com/blog/1112216/202004/1112216-20200401135350453-1447853803.png)

查看文件的属性

```
ps> ls
Directory:
D:\test                                                                                        Mode                LastWriteTime         Length Name  ----                -------------         ------ ----  d-----          2020/4/1    13:49                aaa   d----l          2020/4/1    13:50                bbb 
cmd> dir
2020/04/01  13:50    <DIR>          .            2020/04/01  13:50    <DIR>          ..           2020/04/01  13:49    <DIR>          aaa          2020/04/01  13:50    <SYMLINKD>     bbb [aaa]                   0 个文件              0 字节                     4 个目录 382,272,180,224 可用字节
```

### /H

产生硬链接，如果删除了硬链接源文件也会被删除。

### /J

产生目录链接，产生的文件类型为JUNCTION


### Powshell中SybolicLink指令与mklink的映射

来自windows的docs

| mklink syntax         |                 Powershell equivalent                     |
|-----------------------|-----------------------------------------------------------|
| mklink Link Target    | New-Item -ItemType SymbolicLink -Name Link -Target Target |
| mklink /D Link Target | New-Item -ItemType SymbolicLink -Name Link -Target Target |
| mklink /H Link Target | New-Item -ItemType HardLink -Name Link -Target Target     |
| mklink /J Link Target | New-Item -ItemType Junction -Name Link -Target Target     |


