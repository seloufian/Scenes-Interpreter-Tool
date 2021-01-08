from collections import defaultdict
import json

import numpy as np
import tensorflow as tf

from .config import paths


def load_json_file(filename_path):
	with open(filename_path, encoding='utf-8') as infile:
		loaded_file = json.load(infile)

	return loaded_file


rels_identifier = dict()

rels_identifier['weights'] = load_json_file(paths['rels_identifier']['weights'])
rels_identifier['objects_encoder'] = load_json_file(paths['rels_identifier']['objects_encoder'])
rels_identifier['output_decoder'] = load_json_file(paths['rels_identifier']['output_decoder'])

rels_identifier['model'] = tf.keras.models.load_model(paths['rels_identifier']['model'], compile=False)


def identify_rels(objects_list):
	beta = 7.0
	n = 7

	objects_freq_dict = defaultdict(int)

	for obj in objects_list:
		objects_freq_dict[obj] += 1

	objects_weights_dict = dict()

	for obj, freq in objects_freq_dict.items():
		if obj in rels_identifier['weights']:
			importance = 1 + (beta ** 2)
			importance *= rels_identifier['weights'][obj] * freq
			importance /= (beta ** 2) * rels_identifier['weights'][obj] + freq

			objects_weights_dict[obj] = importance

	ordered_objects_list = sorted(objects_weights_dict.items(), key=lambda elem: elem[1], reverse=True)
	ordered_objects_list = [obj.replace(' ', '_') for obj, _ in ordered_objects_list]

	ordered_objects_list = [rels_identifier['objects_encoder'][obj] for obj in ordered_objects_list[:n]]

	input_tensor = tf.keras.preprocessing.sequence.pad_sequences([ordered_objects_list], maxlen=n)[0]
	to_predict = np.array([input_tensor])

	output = rels_identifier['model'].predict(to_predict)[0]

	scene_identified_rels = list()

	for encoded_word in output:
		decoded_word = rels_identifier['output_decoder'][str(np.argmax(encoded_word))]

		if decoded_word not in ['PAD', 'UNK']:
			scene_identified_rels.append(decoded_word)

	return scene_identified_rels
