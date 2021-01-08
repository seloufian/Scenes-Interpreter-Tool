import pathlib
import sys

import numpy as np
from PIL import Image
import tensorflow as tf

from .config import paths

sys.path.insert(1, paths['object_detector']['object_detection_path'])

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


utils_ops.tf = tf.compat.v1
tf.gfile = tf.io.gfile

model_dir = pathlib.Path(paths['object_detector']['model_dir'])
model = tf.saved_model.load(str(model_dir))

model = model.signatures['serving_default']

category_index = label_map_util.create_category_index_from_labelmap(paths['object_detector']['labels_path'], use_display_name=True)


def run_inference_for_single_image(model, image):
	image = np.asarray(image)
	# The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
	input_tensor = tf.convert_to_tensor(image)
	# The model expects a batch of images, so add an axis with `tf.newaxis`.
	input_tensor = input_tensor[tf.newaxis,...]

	# Run inference
	output_dict = model(input_tensor)

	# All outputs are batches tensors.
	# Convert to numpy arrays, and take index [0] to remove the batch dimension.
	# We're only interested in the first num_detections.
	num_detections = int(output_dict.pop('num_detections'))
	output_dict = {key:value[0, :num_detections].numpy()
				for key,value in output_dict.items()}
	output_dict['num_detections'] = num_detections

	# detection_classes should be ints.
	output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

	# Delete predicted objects with poor accuracy.
	del_objects_idx = []

	for idx in range(output_dict['num_detections']):
		obj_pred_score = output_dict['detection_scores'][idx]

		if obj_pred_score < 0.4:
			del_objects_idx.append(idx)

	output_dict['num_detections'] -= len(del_objects_idx)

	output_dict['detection_scores'] = np.delete(output_dict['detection_scores'], del_objects_idx)
	output_dict['detection_classes'] = np.delete(output_dict['detection_classes'], del_objects_idx)
	output_dict['detection_boxes'] = np.delete(output_dict['detection_boxes'], del_objects_idx, axis=0)

	# Get the bounding-box of each detected object.
	objects_bboxes = [list(bbox) for bbox in output_dict['detection_boxes']]

	# Get absolute bounding-boxes pixels coordinates: (xmin, ymin, xmax, ymax)
	# Absolute object coordinates origin point: image's bottom-left.
	#
	# Tensorflow's coordinates are normalized (between 0 and 1, relative to image's 'width' and 'height').
	# Tensorflow's object coordinates: (ymin, xmin, ymax, xmax). Origin point: image's top-left.
	im_width = image.shape[1] # Numpy array's columns (axis=1) represents image's width.
	im_height = image.shape[0] # Numpy array's lines (axis=0) represents image's height.

	absolute_objects_bboxes = []

	for object_bbox in objects_bboxes:
		xmin = round(object_bbox[1] * im_width)
		ymin = round(im_height - object_bbox[2] * im_height)
		xmax = round(object_bbox[3] * im_width)
		ymax = round(im_height - object_bbox[0] * im_height)

		absolute_objects_bboxes.append([xmin, ymin, xmax, ymax])

	# Get list of image detected object names.
	object_list = []
	for class_num in output_dict['detection_classes']:
		object_list.append(category_index[class_num]['name'].lower())

	# Visualization of the results of a detection.
	image = vis_util.visualize_boxes_and_labels_on_image_array(
			image,
			output_dict['detection_boxes'],
			output_dict['detection_classes'],
			output_dict['detection_scores'],
			category_index,
			instance_masks=None,
			use_normalized_coordinates=True,
			line_thickness=5)

	return absolute_objects_bboxes, object_list, image
