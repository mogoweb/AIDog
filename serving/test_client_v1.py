#!/usr/bin/env python

import argparse
import requests
import json
import tensorflow as tf
import numpy as np


def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(
        file_reader, channels=3, name="png_reader")
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(
        tf.image.decode_gif(file_reader, name="gif_reader"))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
  else:
    image_reader = tf.image.decode_jpeg(
        file_reader, channels=3, name="jpeg_reader")
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0)
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result


def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label


if __name__ == "__main__":
  file_name = "../TestImages/n02085620-Chihuahua/n02085620_11140.jpg"
  label_file = "dog_labels_inception_v3.txt"
  input_height = 299
  input_width = 299
  input_mean = 0
  input_std = 255
  model_name = "default"
  enable_ssl = False

  parser = argparse.ArgumentParser()
  parser.add_argument("--image", help="image to be processed")
  parser.add_argument("--labels", help="name of file containing labels")
  parser.add_argument("--input_height", type=int, help="input height")
  parser.add_argument("--input_width", type=int, help="input width")
  parser.add_argument("--input_mean", type=int, help="input mean")
  parser.add_argument("--input_std", type=int, help="input std")
  parser.add_argument("--model_name", help="name of predict model")
  parser.add_argument("--enable_ssl", type=bool, help="if use https")
  args = parser.parse_args()

  if args.image:
    file_name = args.image
  if args.labels:
    label_file = args.labels
  if args.input_height:
    input_height = args.input_height
  if args.input_width:
    input_width = args.input_width
  if args.input_mean:
    input_mean = args.input_mean
  if args.input_std:
    input_std = args.input_std
  if args.model_name:
    model_name = args.model_name
  if args.enable_ssl:
    enable_ssl = args.enable_ssl

  t = read_tensor_from_image_file(
    file_name,
    input_height=input_height,
    input_width=input_width,
    input_mean=input_mean,
    input_std=input_std)

  if enable_ssl :
    endpoint = "https://ilego.club:8500"
  else:
    endpoint = "http://ilego.club:8500"

  print(t.shape)
  json_data = {"model_name": model_name, "data": {"image": t.tolist()}}
  result = requests.post(endpoint, json=json_data)
  res = np.array(json.loads(result.text)["prediction"][0])
  print(res)
  indexes = np.argsort(-res)
  labels = load_labels(label_file)
  top_k = 3
  for i in range(top_k):
    idx = indexes[i]
    print(labels[idx], res[idx])
