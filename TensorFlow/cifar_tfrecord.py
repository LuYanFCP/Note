import tensorflow as tf
import os
import sys
import pickle
import numpy as np
import tensorflow as tf
import matplotlib.pylab as plt

_NUM_TRAIN_FILES = 5
_IMAGE_SIZE = 32
_CLASS_NAMES = [
    'airplane',
    'automobile',
    'bird',
    'cat',
    'deer',
    'dog',
    'frog',
    'horse',
    'ship',
    'truck'
]


def _get_output_filename(dataset_dir, split_name):
    """Creates the output filename.
    Args:
      dataset_dir: The dataset directory where the dataset is stored.
      split_name: The name of the train/test split.
    Returns:
      An absolute file path.
    """
    return '%s/cifar10_%s.tfrecord' % (dataset_dir, split_name)

def _add_to_tfrecord(filename, tfrecord_writer, offset=0):
    """Loads data from the cifar10 pickle files and writes files to a TFRecord.
    Args:
      filename: The filename of the cifar10 pickle file.
      tfrecord_writer: The TFRecord writer to use for writing.
      offset: An offset into the absolute number of images previously written.
    Returns:
      The new offset.
    """
    with tf.gfile.Open(filename, 'rb') as f:
        # 读取二进制的cifar
        data = pickle.load(f, encoding='bytes')
    images = data[b'data'] # 10000x3072->(32x32x3),rgb
    num_images = images.shape[0]
    # reshape -> 3x32x32
    images = images.reshape((num_images, 3, 32, 32))
    labels = data[b'labels']
    with tf.Graph().as_default():
        image_placeholder = tf.placeholder(tf.uint8)
        encoded_image = tf.image.encode_png(image_placeholder)
        with tf.Session() as sess:
            for j in range(num_images):
                sys.stdout.write('\r>> Reading file [%s] image %d/%d' % (filename, offset + j + 1, offset + num_images))
                sys.stdout.flush()
                # 转换为32x32x3
                image = np.squeeze(images[j]).transpose((1, 2, 0))
                label = labels[j]
                png_string = sess.run(encoded_image, feed_dict={image_placeholder: image})
                example = image_to_tfexample(png_string, b'png', _IMAGE_SIZE, _IMAGE_SIZE, label)
                # 序列化
                tfrecord_writer.write(example.SerializeToString())
    # print("-----------------完成-------------------")
    return offset + num_images


def image_to_tfexample(image_data, image_format, height, width, class_id):
    # 这个是如何做到的
    return tf.train.Example(features=tf.train.Features(feature={
        'image/encoded': tf.train.Feature(bytes_list=tf.train.BytesList(value=[image_data])),
        'image/format': tf.train.Feature(bytes_list=tf.train.BytesList(value=[image_format])),
        'image/class/label': tf.train.Feature(int64_list=tf.train.Int64List(value=[class_id])),
        'image/height': tf.train.Feature(int64_list=tf.train.Int64List(value=[height])),
        'image/width': tf.train.Feature(int64_list=tf.train.Int64List(value=[width])),
    }))







dataset_dir = 'data'
if not tf.gfile.Exists(dataset_dir):
    tf.gfile.MakeDirs(dataset_dir)
training_filename = _get_output_filename(dataset_dir, 'train')
testing_filename = _get_output_filename(dataset_dir, 'test')

# 训练的数据集
with tf.python_io.TFRecordWriter(training_filename) as tfrecord_writer:
    offset = 0
    for i in range(_NUM_TRAIN_FILES):
        filename = os.path.join('cifar/cifar-10-batches-py', 'data_batch_%d' % (i + 1))
        offset = _add_to_tfrecord(filename, tfrecord_writer, offset)

print(">>>>>>>>>>>>>训练数据完成变化>>>>>>>>>>>")

print(">>>>>>>>>>>>>测试数据开始>>>>>>>>>>>>>>")
# Next, process the testing data:
with tf.python_io.TFRecordWriter(testing_filename) as tfrecord_writer:
    filename = os.path.join('./cifar-10-batches-py', 'test_batch')
    _add_to_tfrecord(filename, tfrecord_writer)
print(">>>>>>>>>>>>>测试数据完成>>>>>>>>>>>>>>")


record_iterator = tf.python_io.tf_record_iterator(path='./data/cifar10_train.tfrecord')
string_iterator = next(record_iterator)
example = tf.train.Example()
example.ParseFromString(string_iterator)
height = example.features.feature['image/height'].int64_list.value[0]
width = example.features.feature['image/width'].int64_list.value[0]
png_string = example.features.feature['image/encoded'].bytes_list.value[0]
label = example.features.feature['image/class/label'].int64_list.value[0]

with tf.Session() as sess:
    image_placeholder = tf.placeholder(dtype=tf.string)
    decoded_img = tf.image.decode_png(image_placeholder, channels=3)
    reconstructed_img = sess.run(decoded_img, feed_dict={image_placeholder: png_string})

plt.imshow(reconstructed_img)
plt.title(_CLASS_NAMES[label])
plt.show()


