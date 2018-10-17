from tensorflow.python.platform import gfile
import tensorflow as tf

model = 'tf_files/optimized_dog_graph_inception_v3.pb'
graph = tf.get_default_graph()
graph_def = graph.as_graph_def()
graph_def.ParseFromString(gfile.FastGFile(model, 'rb').read())
tf.import_graph_def(graph_def, name='graph')
summaryWriter = tf.summary.FileWriter('log/', graph)

