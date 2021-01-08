from collections import defaultdict
import json

import numpy as np
import tensorflow as tf

from .config import paths
from .scenes_enrichment import enrich_scene

def load_json_file(filename_path):
	with open(filename_path, encoding='utf-8') as infile:
		loaded_file = json.load(infile)

	return loaded_file


additional_categories = dict()

additional_categories['corresp_from_coco'] = load_json_file(paths['additional_categories']['corresp_from_coco'])
additional_categories['objects_encoder'] = load_json_file(paths['additional_categories']['objects_encoder'])
additional_categories['objects_decoder'] = load_json_file(paths['additional_categories']['objects_decoder'])
additional_categories['weights'] = load_json_file(paths['additional_categories']['weights'])

additional_categories['enrichment_model'] = tf.keras.models.load_model(paths['additional_categories']['enrichment_model'], compile=False)

category_1 = dict()

category_1['categories'] = load_json_file(paths['additional_categories']['category_1']['categories'])
category_1['model'] = tf.keras.models.load_model(paths['additional_categories']['category_1']['model'], compile=False)

category_2 = dict()

category_2['categories'] = load_json_file(paths['additional_categories']['category_2']['categories'])
category_2['model'] = tf.keras.models.load_model(paths['additional_categories']['category_2']['model'], compile=False)

category_3 = dict()

category_3['categories'] = load_json_file(paths['additional_categories']['category_3']['categories'])
category_3['model'] = tf.keras.models.load_model(paths['additional_categories']['category_3']['model'], compile=False)

additional_categories['category_1'] = category_1
additional_categories['category_2'] = category_2
additional_categories['category_3'] = category_3


def predict_additional_categories(objects_list, apply_enrichment=False):

	def _get_best_predict_category_with_proba(to_predict, num_category): # Inner function
		num_category = str(num_category)

		output = additional_categories['category_'+num_category]['model'].predict(to_predict)[0]

		max_index = np.argmax(output)

		max_index_proba = output[max_index]
		max_index_category = additional_categories['category_'+num_category]['categories'][max_index]

		return (max_index_category, max_index_proba)

	beta = 0.6
	n = 16

	corresp_objects_list = list()

	for obj_coco in objects_list:
		obj_dataset = additional_categories['corresp_from_coco'].get(obj_coco, None)

		if obj_dataset:
			corresp_objects_list.append(obj_dataset)

	if apply_enrichment:
		corresp_objects_list = enrich_scene(corresp_objects_list, additional_categories['enrichment_model'],
											additional_categories['objects_encoder'], additional_categories['objects_decoder'])

	objects_freq_dict = defaultdict(int)

	for obj in corresp_objects_list:
		objects_freq_dict[obj] += 1

	objects_weights_dict = dict()

	for obj, freq in objects_freq_dict.items():
		if obj in additional_categories['weights']:
			importance = 1 + (beta ** 2)
			importance *= additional_categories['weights'][obj] * freq
			importance /= (beta ** 2) * additional_categories['weights'][obj] + freq

			objects_weights_dict[obj] = importance

	ordered_objects_list = sorted(objects_weights_dict.items(), key=lambda elem: elem[1], reverse=True)
	ordered_objects_list = [obj for obj, _ in ordered_objects_list]

	ordered_objects_list = [additional_categories['objects_encoder'][obj] for obj in ordered_objects_list[:n]]

	input_tensor = tf.keras.preprocessing.sequence.pad_sequences([ordered_objects_list], maxlen=n)[0]

	to_predict = np.array([input_tensor])

	predicted_categories = list()
	predicted_categories.append(_get_best_predict_category_with_proba(to_predict, 1))
	predicted_categories.append(_get_best_predict_category_with_proba(to_predict, 2))
	predicted_categories.append(_get_best_predict_category_with_proba(to_predict, 3))

	return predicted_categories
