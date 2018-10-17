
import tensorflow as tf
import argparse
import sys
from tensorflow.python.tools import saved_model_utils
from tensorflow.python.framework import graph_util
from tensorflow.python.saved_model import tag_constants


def add_png_decoding(input_width, input_height, input_depth):
  """Adds operations that perform PNG decoding and resizing to the graph..

  Args:
    input_width: The image width.
    input_height: The image height.
    input_depth: The image channels.

  Returns:
    Tensors for the node to feed PNG data into, and the output of the
      preprocessing steps.
  """
  base64_str = tf.placeholder(tf.string, name='input_string')
  input_str = tf.decode_base64(base64_str)
  decoded_image = tf.image.decode_png(input_str, channels=input_depth)
  # Convert from full range of uint8 to range [0,1] of float32.
  decoded_image_as_float = tf.image.convert_image_dtype(decoded_image,
                                                        tf.float32)
  decoded_image_4d = tf.expand_dims(decoded_image_as_float, 0)
  resize_shape = tf.stack([input_height, input_width])
  resize_shape_as_int = tf.cast(resize_shape, dtype=tf.int32)
  resized_image = tf.image.resize_bilinear(decoded_image_4d,
                                           resize_shape_as_int)
  tf.identity(resized_image, name="DecodePNGOutput")
  return input_str, resized_image


def main(_):
  # Needed to make sure the logging output is visible.
  # See https://github.com/tensorflow/tensorflow/issues/3047
  tf.logging.set_verbosity(tf.logging.INFO)

  if not FLAGS.origin_model_dir:
    tf.logging.error('Must set flag --origin_model_dir.')
    return -1

  if not FLAGS.model_dir:
    tf.logging.error('Must set flag --model_dir.')
    return -1

  with tf.Graph().as_default() as g1:
    _, _ = add_png_decoding(299, 299, 3)

  g1def = g1.as_graph_def()

  with tf.Graph().as_default() as g2:
    with tf.Session(graph=g2) as sess:
      input_graph_def = saved_model_utils.get_meta_graph_def(
          FLAGS.origin_model_dir, tag_constants.SERVING).graph_def

      tf.saved_model.loader.load(sess, [tag_constants.SERVING], FLAGS.origin_model_dir)

      g2def = graph_util.convert_variables_to_constants(
          sess,
          input_graph_def,
          ["final_result"],
          variable_names_whitelist=None,
          variable_names_blacklist=None)
      # for n in g2def.node:
      #   print(n.name)

  with tf.Graph().as_default() as g_combined:
    with tf.Session(graph=g_combined) as sess:
      x = tf.placeholder(tf.string, name="base64_string")
      y, = tf.import_graph_def(g1def, input_map={"input_string:0": x}, return_elements=["DecodePNGOutput:0"])
      z, = tf.import_graph_def(g2def, input_map={"Placeholder:0": y}, return_elements=["final_result:0"])

      tf.identity(z, "myOutput")

      tf.saved_model.simple_save(sess,
                                 FLAGS.model_dir,
                                 inputs={"image": x},
                                 outputs={"prediction": z})


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--model_dir',
      type=str,
      default='',
      help='Where to save the exported graph.'
  )
  parser.add_argument(
      '--origin_model_dir',
      type=str,
      default='',
      help='Folder that contains the original SavedModel.'
  )

  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
