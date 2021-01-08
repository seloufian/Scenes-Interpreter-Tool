from django.shortcuts import render
from django.http import HttpResponse

import gc
import json

print('- [1/7]: Define image manipulation.')
from .functions.image_base64_manip import base64image_to_array, array_to_base64image
from .functions.scene_graph_generation import get_scene_graph

print('- [2/7]: Define object detection.')
from .functions.object_detection import model, run_inference_for_single_image

print('- [3/7]: Define standard classification.')
from .functions.standard_classification import predict_standard_class

print('- [4/7]: Define additional categories classification.')
from .functions.additional_categories_classification import predict_additional_categories

print('- [5/7]: Define relationships identification.')
from .functions.rels_identification import identify_rels

print('- [6/7]: Define relationships definition.')
from .functions.rels_definition import define_rels

print('- [7/7]: Define scenes description generation.\n')
from .functions.scenes_description_generation import generate_description


def index(request):
	send_data = dict()

	receive_data = request.body.decode('utf-8')
	receive_data = json.loads(receive_data)

	_, image = base64image_to_array(receive_data['image_in'])

	objects_bboxes, objects_list, image = run_inference_for_single_image(model, image)

	send_data['image'] = array_to_base64image(image)

	apply_enrichment = True if receive_data['param_enrichment'] == 'yes' else False

	if receive_data['task'] == 'classification':
		if receive_data['param_dataset'] == 'mit-indoor':
			send_data['categories_probas'] = predict_standard_class(objects_list, 'mitindoor_new', apply_enrichment)
		else:
			send_data['categories_probas'] = predict_standard_class(objects_list, 'sun2012')
	else:
		scene_identified_rels = identify_rels(objects_list)

		defined_rels_scene = define_rels(objects_bboxes, objects_list, image, scene_identified_rels)

		no_relation_defined = False # There is at least one, unary or binary, relation defined

		if not defined_rels_scene:
			# No relation is defined for this scene, return the object raw list of the scene
			defined_rels_scene = objects_list
			no_relation_defined = True

		scene_graph_array = get_scene_graph(defined_rels_scene, no_relation_defined)
		send_data['scene_graph'] = array_to_base64image(scene_graph_array)

		categories_probas = predict_standard_class(objects_list, 'mitindoor_new', apply_enrichment)
		standard_class_1 = tuple(categories_probas[0])
		standard_class_2 = tuple(categories_probas[1])

		predicted_categories = predict_additional_categories(objects_list, apply_enrichment)

		scene_desc = generate_description(defined_rels_scene,
										[standard_class_1, standard_class_2],
										predicted_categories[0],
										predicted_categories[1],
										predicted_categories[2],
										no_relation_defined)

		send_data['description'] = scene_desc

	send_data = json.dumps(send_data)

	gc.collect()

	return HttpResponse(send_data)
