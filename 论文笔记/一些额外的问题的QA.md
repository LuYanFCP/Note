# 一些论文中读到问题的探究

## Q：为什么要使用activation quantization

1. 如果只量化weight，而不量化activation会出现很多问题，比如计算效率比较低（原因是中最中最重要的就是activation与activation的点积， 低比特与fp32的点积效率很低）
2. 在推断里面使用量化的quantitied activation会加速运算。（低比特运算更快）

## Q：gradient mismatch是什么

# 基础性问题

## Q：为什么使用BN之后就不再需要`bias`

BN ： $z = \frac{x - \mu_{B}}{\sqrt{\sigma^2_{B} + \epsilon }}$

BN之后使用$\mu_{B}$直接归一化了，导致`bias`失效了。
