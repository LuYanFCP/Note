## 亮点

+ 使用不需要标注的数据(降低了成本)

## 核心

+ 关注feature-map而不是weight, 降低量化后的`restruct error`.
+ 使用类似`Deep Compression`中的codebooks方式进行量化存储.
+ 