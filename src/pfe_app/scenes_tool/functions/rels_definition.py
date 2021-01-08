from collections import defaultdict
import itertools
import json
import pickle

import numpy as np
from PIL import Image
import tensorflow as tf

from .bounding_box_class import BoundingBox
from .config import paths


unary_rels = dict()

for un_cls in paths['rels_definers']['unary_rels']:
	model_name = un_cls.rsplit('/', 1)[1]
	model_name = model_name.replace('-', ' ').strip().lower()

	obj_name, classes = tuple(model_name.split('__'))
	classes = classes[:-3].split('_')

	unary_rels[obj_name] = dict()
	unary_rels[obj_name]['classes'] = classes

	unary_rels[obj_name]['model_path'] = un_cls

binary_rels = dict()

with open(paths['rels_definers']['binary_rels']['binary_classifier_classes'], encoding='utf-8') as infile:
	binary_rels['binary_classifier_classes'] = json.load(infile)

with open(paths['rels_definers']['binary_rels']['binary_rels_predicates'], 'rb') as infile:
	binary_rels['binary_rels_predicates'] = pickle.load(infile)

binary_rels['model'] = tf.keras.models.load_model(paths['rels_definers']['binary_rels']['model'])


def define_rels(objects_bboxes, objects_list, image, scene_identified_rels):

	def _define_unary_rel(temp_def_obj, defined_rels_scene): # Inner function (Unary relationships definition)
		obj = curr_objects_list[0]

		if (obj,) not in temp_def_obj:
			temp_def_obj.append((obj,))

			if obj in unary_rels:
				unary_rel_definer_model = tf.keras.models.load_model(unary_rels[obj]['model_path'])

				for idx in range(len(curr_objects_list)):
					curr_ann_obj = curr_objects_list[idx]
					curr_aan_bbox = objects_bboxes[idx]

					if curr_ann_obj == obj:
						obj_name = curr_ann_obj + '_' + str(idx)

						val_1 = curr_aan_bbox[0]
						val_2 = curr_aan_bbox[1]
						val_3 = curr_aan_bbox[0] + curr_aan_bbox[2]
						val_4 = curr_aan_bbox[1] + curr_aan_bbox[3]

						crop_rectangle = (val_1, val_2, val_3, val_4)

						cropped_image = image.crop(crop_rectangle)
						cropped_image = cropped_image.resize((80, 80))

						new_image = np.array(cropped_image)

						new_image = tf.cast(new_image, tf.float32)

						to_predict = np.array([new_image])
						result = unary_rel_definer_model.predict(to_predict)[0]

						unary_relation = unary_rels[curr_ann_obj]['classes'][np.argmax(result)]

						defined_rels_scene.append((obj_name, unary_relation))

		return temp_def_obj, defined_rels_scene


	def _define_binary_rels(temp_def_obj, defined_rels_scene): # Inner function (Binary relationships definition)
		for comb in itertools.combinations(curr_objects_list, 2):
			if comb not in temp_def_obj:
				temp_def_obj.append(comb)

				for idx_1 in range(len(objects_bboxes)):
					curr_ann_obj_1 = objects_list[idx_1]

					for idx_2 in range(len(objects_bboxes)):
						curr_ann_obj_2 = objects_list[idx_2]

						if (idx_1 != idx_2) and (curr_ann_obj_1 == comb[0]) and (curr_ann_obj_2 == comb[1]):
							curr_aan_bbox_1 = objects_bboxes[idx_1]
							curr_aan_bbox_2 = objects_bboxes[idx_2]

							xmin1 = curr_aan_bbox_1[0]
							ymin1 = curr_aan_bbox_1[1]
							xmax1 = curr_aan_bbox_1[0] + curr_aan_bbox_1[2]
							ymax1 = curr_aan_bbox_1[1] + curr_aan_bbox_1[3]

							xmin2 = curr_aan_bbox_2[0]
							ymin2 = curr_aan_bbox_2[1]
							xmax2 = curr_aan_bbox_2[0] + curr_aan_bbox_2[2]
							ymax2 = curr_aan_bbox_2[1] + curr_aan_bbox_2[3]

							curr_aan_bbox_1 = BoundingBox(xmin1, ymin1, xmax1, ymax1)
							curr_aan_bbox_2 = BoundingBox(xmin2, ymin2, xmax2, ymax2)
							image_dimensions = [width, height]

							features_array = curr_aan_bbox_1.get_features_array(curr_aan_bbox_2, image_dimensions)
							features_array = np.array(features_array)

							to_predict = np.array([features_array])
							result = binary_rels['model'].predict(to_predict)[0]

							ordered_args_result = np.argsort(- result)

							binary_relation = 'no_relation'
							for class_idx in ordered_args_result:
								class_value = binary_rels['binary_classifier_classes'][class_idx]

								if (curr_ann_obj_1, curr_ann_obj_2) in binary_rels['binary_rels_predicates']:
									if class_value in binary_rels['binary_rels_predicates'][(curr_ann_obj_1, curr_ann_obj_2)]:
										binary_relation = class_value
									break

							if binary_relation != 'no_relation':
								obj1_name = curr_ann_obj_1 + '_' + str(idx_1)
								obj2_name = curr_ann_obj_2 + '_' + str(idx_2)
								defined_rels_scene.append((obj1_name, binary_relation, obj2_name))

		return temp_def_obj, defined_rels_scene


	def _resolve_conflicts_rels_scene(defined_rels_scene): # Inner function.
		new_defined_rels = []
		binary_rels_list = []

		for rel in defined_rels_scene:
			if len(rel) == 2: # Unary relationship
				new_defined_rels.append(rel)

			else: # Binary relationship [len(rel) == 3]
				rel_members = set([rel[0], rel[2]])

				if rel_members not in binary_rels_list:
					binary_rels_list.append(rel_members)
					new_defined_rels.append(rel)

		return new_defined_rels


	curr_objects_list = list()

	defined_rels_scene = list()
	temp_def_obj = list()

	image = Image.fromarray(image)
	width, height = image.size

	for obj in scene_identified_rels:
		if obj != '#':
			curr_objects_list.append(obj)

		else:
			if len(curr_objects_list) == 0:
				continue

			elif len(curr_objects_list) == 1: # Unary relationship
				temp_def_obj, defined_rels_scene = _define_unary_rel(temp_def_obj, defined_rels_scene)
				curr_objects_list = []

			else: # Binary relationships
				temp_def_obj, defined_rels_scene = _define_binary_rels(temp_def_obj, defined_rels_scene)
				curr_objects_list = []

	if len(curr_objects_list) >= 2: # Binary relationships (remain - last)
		temp_def_obj, defined_rels_scene = _define_binary_rels(temp_def_obj, defined_rels_scene)

	defined_rels_scene = _resolve_conflicts_rels_scene(defined_rels_scene)

	return defined_rels_scene
