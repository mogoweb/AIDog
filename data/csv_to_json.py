#!/usr/bin/env python

import argparse
import csv
import json
import tensorflow as tf
import sys

# 读csv文件
def read_csv(file):
  csv_rows = []
  with open(file) as csvfile:
    reader = csv.DictReader(csvfile)
    title = reader.fieldnames
    for row in reader:
      csv_rows.extend([{title[i]: row[title[i]] for i in range(len(title))}])
    return csv_rows


# 写json文件
def write_json(data, json_file, format=None):
  with open(json_file, "w") as f:
    if format == "good":
      f.write(json.dumps(data, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False))
    else:
      f.write(json.dumps(data))


def main(_):
  write_json(read_csv(FLAGS.csv_file), FLAGS.json_file, 'good')


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--csv_file',
    type=str,
    default='dogs.csv',
    help='The cvs file that you want to convert to json.'
  )
  parser.add_argument(
    '--json_file',
    type=str,
    default='dogs.json',
    help='The json file that convert to.'
  )
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)