import numpy as np


def enrich_scene(objects_list, enrichment_model, objects_encoder, objects_decoder):
	num_objects = len(objects_encoder)

	scene_vector = np.zeros(num_objects)

	for obj in objects_list: # Create a vector representation of the scene from the list of its objects
		obj_code = objects_encoder.get(obj, None)

		if obj_code:
			scene_vector[obj_code] += 1

	to_predict = np.array([scene_vector])
	predict_output = enrichment_model.predict(to_predict)[0] # Enrich the scene

	for obj_code in range(num_objects): # Merge the initial scene objects frequencies with predicted ones
		obj_freq = round(predict_output[obj_code])

		if obj_freq > 0:
			scene_vector[obj_code] += obj_freq

	scene_vector = scene_vector.astype(np.int64) # Convert object frequencies from 'float' to 'integer'

	new_objects_list = list()

	for obj_code in range(num_objects): # Convert the scene's vector representation into a list of objects
		obj_freq = scene_vector[obj_code]

		if obj_freq > 0:
			temps_objects = objects_decoder[str(obj_code)]
			temps_objects = [temps_objects] * obj_freq
			new_objects_list.extend(temps_objects)

	return new_objects_list
