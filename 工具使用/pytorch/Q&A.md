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
