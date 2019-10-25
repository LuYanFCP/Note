import tensorflow as tf

queue = tf.FIFOQueue(100, 'float')

enqueue_op = queue.enqueue([tf.random_normal([1])])

# 使用tf.train.Queue来创建多个线程运行队列的入队操作。
# 五个同操作的进程

qr = tf.train.QueueRunner(queue, [enqueue_op] * 5)

# 将定义过的QueueRunner 加入TensorFlow计算图上的集合

tf.train.add_queue_runner(qr)

out_tensor = queue.dequeue()

with tf.Session() as sess:
    coord = tf.train.Coordinator()

    threads = tf.train.start_queue_runners(sess=sess, coord=coord)
    # 获取队列中的取值
    for _ in range(3):
        print(sess.run(out_tensor))
    
    coord.request_stop()
    coord.join(threads)

