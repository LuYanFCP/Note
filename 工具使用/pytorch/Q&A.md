### Q:ReLU(inplace=True) inplace是什么意思

inplace = True表示直接在原Tensor上修改，不增加新的显存。

例如:
input->conv->y

如果inplace=False则

z = relu(y), z->input, 多创建了有个z变量

inplace=True: relu(y)->input

### imagenet输入一般是224


### Q: DataLoader中 sampler的作用
自定义一个取数据的方式，如果sample输入了，则shuffle要未false


### Q: Pytorch的钩子有什么用

三种

1. autograd.Variable.register_hook
2. Module.register_forward_hook
3. Module.register_backward_hook

#### autograd.Variable.register_hook

在计算grad的时候，对grad做额外的操作，比如说打印(Pytorch设计梯度反传的时候只保留在入度为0节点的梯度，可以用hook进行记录，hook(grad))

### register_forward_hook 与 register_backward_hook

