import tensorflow as tf

model = 'tf_files/optimized_dog_graph_inception_v3.pb'
with tf.Session() as sess:
    with open(model, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        print(graph_def)

