
## 会话管理

+ tmux new -s [session name]
+ tmux ls
+ tmux a 连接上一个会话
+ tmux a -t [session name] 连接指定会话
+ tmux rename -t s1 s2 重命名会话s1为s2
+ tmux kill-session 关闭上一次的会话
+ tmux kill-session -t s1 关闭会话s1,如果加`-a`的话就是关闭出s1外的所有会话
+ tmux kill-server 关闭服务
  
prefix = ctrl + b

+ prefix + s 列出会话,可以切换
+ prefix $ 重新命名会话
+ prefix d 分离当前会话
+ prefix D 分离指定会话

## 窗口管理

+ prefix c 创建一个新窗口
+ prefix , 重命名当前窗口
+ prefix w 列出所有窗口
+ prefix n 进入下一个窗口
+ prefix p 进入上一个窗口
+ prefix l 进入之前操作的窗口
+ prefix 0-9 进入某个编号的窗口
+ prefix . 修改当前窗口的索引编号
+ prefix ' 切换指定编号的窗口可以大于9
+ prefix f 按内容搜索窗口
+ prefix & 关闭当前窗口

## 窗格管理

+ prefix %
+ prefix "
+ prefix ↑↓←→ 切换窗口
+ prefix q 显示窗格编号
+ prefix o 顺时针切换窗格
+ prefix } 与下一个窗格交换顺序
+ prefix { 与上一个窗格交换顺序
+ prefix x 关闭当前窗格
+ prefix space 重新排列窗格
+ prefix ! 将窗格放置在新窗口
+ prefix t 在当前窗格显示时间
+ prefix z 放大当前窗格,(第二次按的时候返回)
+ prefix i 显示当前窗格的信息

## 其他

+ tmux list-key 列出所有绑定的键
+ tmux list-command 列出所有命令