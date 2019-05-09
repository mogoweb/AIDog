from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf
from tensorflow import keras
import pathlib
import random
import matplotlib.pyplot as plt
import argparse
import sys
import absl
import os

FLAGS = None
AUTOTUNE = tf.data.experimental.AUTOTUNE

IMG_SHAPE = (128, 128, 3)
BATCH_SIZE = 32


def preprocess_image(image):
  image = tf.image.decode_jpeg(image, channels=3)
  image = tf.image.resize(image, [128, 128])
  image /= 255.0  # normalize to [0,1] range

  return image


def load_and_preprocess_image(path):
  image = tf.io.read_file(path)
  return preprocess_image(image)


def build_model(num_classes):
  # Create the base model from the pre-trained model Inception V3
  base_model = keras.applications.InceptionV3(input_shape=IMG_SHAPE,
                                              # We cannot use the top classification layer of the pre-trained model as it contains 1000 classes.
                                              # It also restricts our input dimensions to that which this model is trained on (default: 299x299)
                                              include_top=False,
                                              weights='imagenet')
  # Using Sequential API to stack up the layers
  model = keras.Sequential([
    base_model,
    keras.layers.GlobalAveragePooling2D(),
    keras.layers.Dense(num_classes,
                       activation='softmax')
  ])

  # Compile the model to configure training parameters
  model.compile(optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])
  return model


def main(_):
  if not FLAGS.image_dir:
    absl.logging.error('Must set flag --image_dir.')
    return -1

  images_root = pathlib.Path(FLAGS.image_dir)
  print(images_root)

  if FLAGS.debug_output:
    for item in images_root.iterdir():
      print(item)

  all_image_paths = list(images_root.glob("*/*"))
  all_image_paths = [str(path) for path in all_image_paths]
  random.shuffle(all_image_paths)

  images_count = len(all_image_paths)
  print(images_count)

  split_1 = int(0.8 * images_count)
  split_2 = int(0.9 * images_count)
  train_images = all_image_paths[:split_1]
  validate_images = all_image_paths[split_1:split_2]
  test_images = all_image_paths[split_2:]

  label_names = sorted(item.name for item in images_root.glob("*/") if item.is_dir())
  if FLAGS.debug_output:
    print(label_names)

  label_to_index = dict((name, index) for index, name in enumerate(label_names))
  if FLAGS.debug_output:
    print(label_to_index)

  train_image_labels = [label_to_index[pathlib.Path(path).parent.name] for path in train_images]
  validate_image_labels = [label_to_index[pathlib.Path(path).parent.name] for path in validate_images]
  test_image_labels = [label_to_index[pathlib.Path(path).parent.name] for path in test_images]
  if FLAGS.debug_output:
    print(train_image_labels)

  if FLAGS.debug_output:
    image_path = train_images[0]
    label = train_image_labels[0]

    plt.imshow(load_and_preprocess_image(image_path))
    plt.grid(False)
    plt.title(label_names[label].title())
    plt.show()
    print()

  train_path_ds = tf.data.Dataset.from_tensor_slices(train_images)
  train_image_ds = train_path_ds.map(load_and_preprocess_image, num_parallel_calls=AUTOTUNE)

  if FLAGS.debug_output:
    plt.figure(figsize=(8, 8))
    for n, image in enumerate(train_image_ds.take(4)):
      plt.subplot(2, 2, n+1)
      plt.imshow(image)
      plt.grid(False)
      plt.xticks([])
      plt.yticks([])

    plt.show()

  train_label_ds = tf.data.Dataset.from_tensor_slices(tf.cast(train_image_labels, tf.int64))
  if FLAGS.debug_output:
    for label in train_label_ds.take(10):
      print(label_names[label.numpy()])

  train_image_label_ds = tf.data.Dataset.zip((train_image_ds, train_label_ds))

  validate_path_ds = tf.data.Dataset.from_tensor_slices(validate_images)
  validate_image_ds = validate_path_ds.map(load_and_preprocess_image, num_parallel_calls=AUTOTUNE)
  validate_label_ds = tf.data.Dataset.from_tensor_slices(tf.cast(validate_image_labels, tf.int64))
  validate_image_label_ds = tf.data.Dataset.zip((validate_image_ds, validate_label_ds))

  test_path_ds = tf.data.Dataset.from_tensor_slices(test_images)
  test_image_ds = test_path_ds.map(load_and_preprocess_image, num_parallel_calls=AUTOTUNE)
  test_label_ds = tf.data.Dataset.from_tensor_slices(tf.cast(test_image_labels, tf.int64))
  test_image_label_ds = tf.data.Dataset.zip((test_image_ds, test_label_ds))

  inception_model = build_model(len(label_names))
  num_train = split_1
  num_val = split_2 - split_1
  steps_per_epoch = round(num_train) // BATCH_SIZE
  validation_steps = round(num_val) // BATCH_SIZE

  # Creating Keras callbacks
  tensorboard_callback = keras.callbacks.TensorBoard(log_dir='./log_dir', histogram_freq=1)
  model_checkpoint_callback = keras.callbacks.ModelCheckpoint(
        'training_checkpoints/weights.{epoch:02d}-{val_loss:.2f}.hdf5', period=5)
  os.makedirs('training_checkpoints/', exist_ok=True)
  # early_stopping_checkpoint = keras.callbacks.EarlyStopping(patience=5)

  # Setting a shuffle buffer size as large as the dataset ensures that the data is
  # completely shuffled.
  ds = train_image_label_ds.shuffle(buffer_size=num_train)
  ds = ds.repeat()
  ds = ds.batch(BATCH_SIZE)
  # `prefetch` lets the dataset fetch batches, in the background while the model is training.
  ds = ds.prefetch(buffer_size=AUTOTUNE)

  inception_model.fit(ds,
                      epochs=FLAGS.epochs,
                      steps_per_epoch=steps_per_epoch,
                      validation_data=validate_image_label_ds.repeat().batch(BATCH_SIZE),
                      validation_steps=validation_steps,
                      callbacks=[tensorboard_callback,
                                 model_checkpoint_callback])

  predictions = inception_model.predict(test_image_label_ds.batch(BATCH_SIZE))
  print(predictions)

  # Export the model to a SavedModel
  model_path = "{}/{}/".format(FLAGS.saved_model_dir, FLAGS.model_version)
  keras.experimental.export_saved_model(inception_model, model_path)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--image_dir',
      type=str,
      default='',
      help='Path to folders of labeled images.'
  )
  parser.add_argument(
      '--debug_output',
      default=False,
      help='If display datasets for debug purpose',
      action='store_true'
  )
  parser.add_argument(
      '--epochs',
      type=int,
      default=20,
      help='epochs for training',
  )
  parser.add_argument(
      '--saved_model_dir',
      type=str,
      default='./models/inception',
      help='Where to save the exported graph.')
  parser.add_argument(
    '--model_version',
    type=int,
    default=3,
    help="""Version number of the model.""")

  FLAGS, unparsed = parser.parse_known_args()
  absl.app.run(main=main, argv=[sys.argv[0]] + unparsed)