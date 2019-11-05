
MNIST二进制格式:

1. image
   + 第一个int(32)写的是是一个标记 为 2051
   + 后三个int32分别是图片个数、图片的高、图片的宽
   + 之后的就是一张一张的照片数据（行优先）
2. label
   + 第一个int存着标记 2049
   + 之后应该int是一个label的数目

首先根据这两个写解析程序

```python
def load_mnist_data(filepath):
    with open(filepath, 'rb') as f:
        raw_buf = np.fromstring(f.read(), np,uint8)
    assert raw_buf[0:4].view('>i4')[0] == 2051  # 验证数据是否有错
    num_images = raw_buf[4:8].view('>4i')[0]
    image_h = raw_buf[8:12].view('>4i')[0]
    image_w = raw_buf[8:12].view('>4i')[0]
    return np.ascontiguousarray(255 - raw_buf[16:].reshape(num_images, image_h, image_w))

def load_mnist_label(filepath):
    with open(filepath, 'rb') as f:
        raw_buf = np.fromstring(f.read(), np,uint8)
    assert raw_buf[0:4].view('>i4')[0] == 2049  # 验证数据是否有错
    num_labels = raw_buf[4:8].view('>4i')[0]
    return list(raw_buf[8:].astype(np.int32).reshape(num_labels))
```

主程序
```python
def main():
    parser.add_argument("-d", "--dataset", help="Path to the MNIST training, testing or validation dataset, e.g. train-images-idx3-ubyte, t10k-images-idx3-ubyte, etc.", default=os.path.abspath("train-images.idx3-ubyte"))
    parser.add_argument("-l", "--labels", help="Path to the MNIST training, testing or validation labels, e.g. train-labels-idx1-ubyte, t10k-labels-idx1-ubyte, etc.", 
    default=os.path.abspath("train-labels.idx1-ubyte"))
    parser.add_argument("-o", "--output", help="Path to the output directory.", default=os.getcwd())

    args, _ = parser.parse_known_args()

    data = load_mnist_data(args.dataset)
    labels = load_mnist_labels(args.labels)
    output_dir = args.output

    # Find one image for each digit.
    for i in range(10):
        index = labels.index(i)
        image = Image.fromarray(data[index], mode="L")
        path = os.path.join(output_dir, "{:}.pgm".format(i)) # pgm是单色图
        image.save(path)
```