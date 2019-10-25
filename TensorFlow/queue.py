import tensorflow as tf
import matplotlib.pyplot as plt

# 文件名队列
filename = tf.train.string_input_producer(['./data/cifar10_train.tfrecord'])

# 使用TFRecordReader去读取
reader = tf.TFRecordReader()
_, serialized_example = reader.read(filename)

# 解析
features = tf.parse_single_example(serialized_example, features={
    'image/encoded': tf.FixedLenFeature((), tf.string, default_value=''),
    'image/format': tf.FixedLenFeature((), tf.string, default_value='png'),
    'image/height': tf.FixedLenFeature((), tf.int64),
    'image/width': tf.FixedLenFeature((), tf.int64),
    'image/class/label': tf.FixedLenFeature([], tf.int64, default_value=tf.zeros([], dtype=tf.int64))
})

image = tf.image.decode_png(features['image/encoded'], channels=3)
image = tf.image.resize_image_with_crop_or_pad(image, 32, 32)
label = features['image/class/label']
init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())

with tf.Session() as sess:
    sess.run(init_op)
    tf.train.start_queue_runners()

    image_val_1, label_val_1 = sess.run([image, label])
    print(image_val_1, label_val_1)
    # 然后运行第二次
    image_val_2, label_val_2 = sess.run([image, label])
    print(image_val_2, label_val_2)

    plt.imshow(image_val_1)
    plt.title(label_val_1)
    plt.show()
