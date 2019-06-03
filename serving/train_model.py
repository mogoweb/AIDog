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

IMG_SHAPE = (192, 192, 3)
BATCH_SIZE = 32


def preprocess_image(image):
  image = tf.image.decode_jpeg(image, channels=3)
  image = tf.image.resize(image, [192, 192])
  image /= 255.0  # normalize to [0,1] range
  # normalized to the[-1, 1] range
  image = 2 * image - 1

  return image


def load_and_preprocess_image(path):
  image = tf.io.read_file(path)
  return preprocess_image(image)


def build_model(num_classes):
  # Create the base model from the pre-trained model MobileNet V2
  base_model = keras.applications.MobileNetV2(input_shape=IMG_SHAPE, include_top=False)
  # Unfreeze all layers of MobileNetV2
  base_model.trainable = True

  # Refreeze layers until the layers we want to fine-tune
  for layer in base_model.layers[:100]:
    layer.trainable = False

  # Use a lower learning rate
  lr = 0.0001

  # Using Sequential API to stack up the layers
  model = keras.Sequential([
    base_model,
    keras.layers.GlobalAveragePooling2D(),
    keras.layers.Dense(num_classes,
                       activation='softmax')
  ])

  # Compile the model to configure training parameters
  model.compile(optimizer=tf.keras.optimizers.Adam(lr=lr),
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

  split = int(0.9 * images_count)
  train_images = all_image_paths[:split]
  validate_images = all_image_paths[split:]

  label_names = sorted(item.name for item in images_root.glob("*/") if item.is_dir())
  if FLAGS.debug_output:
    print(label_names)

  label_to_index = dict((name, index) for index, name in enumerate(label_names))
  if FLAGS.debug_output:
    print(label_to_index)

  train_image_labels = [label_to_index[pathlib.Path(path).parent.name] for path in train_images]
  validate_image_labels = [label_to_index[pathlib.Path(path).parent.name] for path in validate_images]
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

  model = build_model(len(label_names))
  num_train = len(train_images)
  num_val = len(validate_images)
  steps_per_epoch = round(num_train) // BATCH_SIZE
  validation_steps = round(num_val) // BATCH_SIZE

  # Creating Keras callbacks
  tensorboard_callback = keras.callbacks.TensorBoard(log_dir='./log_dir', histogram_freq=1)
  model_checkpoint_callback = keras.callbacks.ModelCheckpoint(
        'training_checkpoints/weights.{epoch:02d}-{val_loss:.2f}.hdf5', monitor='val_loss', mode='min')
  os.makedirs('training_checkpoints/', exist_ok=True)
  early_stopping_checkpoint = keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max', min_delta=1)

  ds = train_image_label_ds.repeat()
  ds = ds.batch(BATCH_SIZE)
  # `prefetch` lets the dataset fetch batches, in the background while the model is training.
  ds = ds.prefetch(buffer_size=AUTOTUNE)

  model.fit(ds,
            epochs=FLAGS.epochs,
            steps_per_epoch=steps_per_epoch,
            validation_data=validate_image_label_ds.repeat().batch(BATCH_SIZE),
            validation_steps=validation_steps,
            callbacks=[tensorboard_callback, model_checkpoint_callback, early_stopping_checkpoint])

  # Export the model to a SavedModel
  model_path = "{}/{}/".format(FLAGS.saved_model_dir, FLAGS.model_version)
  keras.experimental.export_saved_model(model, model_path)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--image_dir',
      type=str,
      default='./Images',
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
      default='./models/mobilenet',
      help='Where to save the exported graph.')
  parser.add_argument(
    '--model_version',
    type=int,
    default=1,
    help="""Version number of the model.""")

  FLAGS, unparsed = parser.parse_known_args()
  absl.app.run(main=main, argv=[sys.argv[0]] + unparsed)
