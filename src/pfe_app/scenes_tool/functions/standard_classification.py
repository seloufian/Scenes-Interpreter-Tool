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


standard_classification = dict()

mitindoor_new = dict()

mitindoor_new['corresp_from_coco'] = load_json_file(paths['standard_classification']['mitindoor_new']['corresp_from_coco'])
mitindoor_new['categories_decoder'] = load_json_file(paths['standard_classification']['mitindoor_new']['categories_decoder'])
mitindoor_new['objects_encoder'] = load_json_file(paths['standard_classification']['mitindoor_new']['objects_encoder'])
mitindoor_new['objects_decoder'] = load_json_file(paths['standard_classification']['mitindoor_new']['objects_decoder'])
mitindoor_new['weights'] = load_json_file(paths['standard_classification']['mitindoor_new']['weights'])

mitindoor_new['model'] = tf.keras.models.load_model(paths['standard_classification']['mitindoor_new']['model'], compile=False)
mitindoor_new['enrichment_model'] = tf.keras.models.load_model(paths['standard_classification']['mitindoor_new']['enrichment_model'], compile=False)

sun2012 = dict()

sun2012['corresp_from_coco'] = load_json_file(paths['standard_classification']['sun2012']['corresp_from_coco'])
sun2012['categories_decoder'] = load_json_file(paths['standard_classification']['sun2012']['categories_decoder'])
sun2012['objects_encoder'] = load_json_file(paths['standard_classification']['sun2012']['objects_encoder'])
sun2012['weights'] = load_json_file(paths['standard_classification']['sun2012']['weights'])

sun2012['model'] = tf.keras.models.load_model(paths['standard_classification']['sun2012']['model'], compile=False)

standard_classification['mitindoor_new'] = mitindoor_new
standard_classification['sun2012'] = sun2012


def predict_standard_class(objects_list, dataset, apply_enrichment=False):
	beta, n = None, None

	# The classifier trained on "MIT-Indoor-New" is selected. Define the best values of the parameters obtained for this dataset.
	if dataset == 'mitindoor_new':
		beta = 1.5
		n = 27
	# The classifier trained on "Sun2012" is selected. Define the best values of the parameters obtained for this dataset.
	elif dataset == 'sun2012':
		beta = 0.0
		n = 37
	else:
		return # The selected dataset is not recognized. The classification is impossible.

	corresp_objects_list = list()

	for obj_coco in objects_list:
		obj_dataset = standard_classification[dataset]['corresp_from_coco'].get(obj_coco, None)

		if obj_dataset:
			corresp_objects_list.append(obj_dataset)

	if dataset == 'mitindoor_new' and apply_enrichment: # The enrichment can be done only with the classifier trained on "MIT-Indoor-New"
		corresp_objects_list = enrich_scene(corresp_objects_list, mitindoor_new['enrichment_model'],
											mitindoor_new['objects_encoder'], mitindoor_new['objects_decoder'])

	objects_freq_dict = defaultdict(int)

	for obj in corresp_objects_list:
		objects_freq_dict[obj] += 1

	objects_weights_dict = dict()

	for obj, freq in objects_freq_dict.items():
		if obj in standard_classification[dataset]['weights']:
			importance = 1 + (beta ** 2)
			importance *= standard_classification[dataset]['weights'][obj] * freq
			importance /= (beta ** 2) * standard_classification[dataset]['weights'][obj] + freq

			objects_weights_dict[obj] = importance

	ordered_objects_list = sorted(objects_weights_dict.items(), key=lambda elem: elem[1], reverse=True)
	ordered_objects_list = [obj for obj, _ in ordered_objects_list]

	ordered_objects_list = [standard_classification[dataset]['objects_encoder'][obj] for obj in ordered_objects_list[:n]]

	input_tensor = tf.keras.preprocessing.sequence.pad_sequences([ordered_objects_list], maxlen=n)[0]
	to_predict = np.array([input_tensor])

	output = standard_classification[dataset]['model'].predict(to_predict)[0]

	categories_probas = dict()

	for idx in range(len(output)):
		curr_category = standard_classification[dataset]['categories_decoder'][str(idx)]
		curr_category = curr_category.replace('_', ' ').strip().lower()

		curr_proba = round(output[idx] * 100, 2) # Convert current probability to percentage

		categories_probas[curr_category] = curr_proba

	categories_probas = list(map(list, categories_probas.items()))

	# Sort the probabilities in descending order (the most probable is the first)
	categories_probas.sort(key=lambda elem: elem[1], reverse=True)

	return categories_probas
