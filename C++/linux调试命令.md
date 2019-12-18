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
