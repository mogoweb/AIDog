#!/usr/bin/env python

import argparse
import requests
import json
import tensorflow as tf
import numpy as np
import base64


def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label


if __name__ == "__main__":
  file_name = "n02085620_199.png"
  label_file = "dog_labels_inception_v3.txt"
  model_name = "default"
  model_version = 2
  enable_ssl = False

  parser = argparse.ArgumentParser()
  parser.add_argument("--image", help="image to be processed")
  parser.add_argument("--labels", help="name of file containing labels")
  parser.add_argument("--model_name", help="name of predict model")
  parser.add_argument("--model_version", type=int, help="version of predict model")
  parser.add_argument("--enable_ssl", type=bool, help="if use https")
  args = parser.parse_args()

  if args.image:
    file_name = args.image
  if args.labels:
    label_file = args.labels
  if args.model_name:
    model_name = args.model_name
  if args.enable_ssl:
    enable_ssl = args.enable_ssl

  with open(file_name, "rb") as image_file:
    encoded_string = str(base64.urlsafe_b64encode(image_file.read()), "utf-8")

  if enable_ssl :
    endpoint = "https://127.0.0.1:8500"
  else:
    endpoint = "http://127.0.0.1:8500"

  json_data = {"model_name": model_name,
               "model_version": model_version,
               "data": {"image": encoded_string}
              }
  result = requests.post(endpoint, json=json_data)
  res = np.array(json.loads(result.text)["prediction"][0])
  print(res)
  indexes = np.argsort(-res)
  labels = load_labels(label_file)
  top_k = 3
  for i in range(top_k):
    idx = indexes[i]
    print(labels[idx], res[idx])
