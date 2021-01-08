# This file defines paths used in functions (in current directory) imported in '../models.py'

# Paths dict main structure:
# .
# ├── object_detector.
# │
# ├── standard_classification.
# │   ├── mitindoor_new.
# │   └── sun2012.
# │
# ├── additional_categories.
# │
# ├── rels_identifier.
# │
# └── rels_definers.
#     ├── unary_rels.
#     └── binary_rels.


from os import listdir
import pathlib


paths = dict()

current_script_dir = str(pathlib.Path(__file__).parent.absolute()).replace('\\', '/') + '/'
scenes_tool_data_path = current_script_dir + 'scenes_tool_data/'


# COCO object detector paths.
object_detector = dict()

object_detector['object_detection_path'] = scenes_tool_data_path + 'object_detection/tf_model/'
object_detector['model_dir'] = scenes_tool_data_path + 'object_detection/saved_model'
object_detector['labels_path'] = object_detector['object_detection_path'] + 'object_detection/data/mscoco_label_map.pbtxt'

paths['object_detector'] = object_detector


# Standard classification paths.
paths['standard_classification'] = dict()

standard_classification_path = scenes_tool_data_path + 'standard_classifiers/'

## MIT-Indoor-New (containing all scenes) paths.
mitindoor_new_path = standard_classification_path + 'mitindoor_new/'

mitindoor_new = dict()

mitindoor_new['corresp_from_coco'] = mitindoor_new_path + 'corresp_coco_mitindoor_new_unique.json'
mitindoor_new['categories_decoder'] = mitindoor_new_path + 'mitindoor_new_categories_decoder.json'
mitindoor_new['model'] = mitindoor_new_path + 'mitindoor_new_model.h5'
mitindoor_new['enrichment_model'] = mitindoor_new_path + 'mitindoor_new_enrichment_model.h5'
mitindoor_new['objects_encoder'] = mitindoor_new_path + 'mitindoor_new_objects_encoder.json'
mitindoor_new['objects_decoder'] = mitindoor_new_path + 'mitindoor_new_objects_decoder.json'
mitindoor_new['weights'] = mitindoor_new_path + 'weights_mitindoor_new.json'

paths['standard_classification']['mitindoor_new'] = mitindoor_new

## Sun2012 paths.
sun2012_path = standard_classification_path + 'sun2012/'

sun2012 = dict()

sun2012['corresp_from_coco'] = sun2012_path + 'corresp_coco_sun2012_unique.json'
sun2012['categories_decoder'] = sun2012_path + 'sun2012_categories_decoder.json'
sun2012['model'] = sun2012_path + 'sun2012_model.h5'
sun2012['objects_encoder'] = sun2012_path + 'sun2012_objects_encoder.json'
sun2012['weights'] = sun2012_path + 'weights_sun2012.json'

paths['standard_classification']['sun2012'] = sun2012


# Additional categories classification paths.
additional_categories_path = scenes_tool_data_path + 'additional_categories/'

additional_categories = dict()

additional_categories['enrichment_model'] = additional_categories_path + 'mitindoor_enrichment_model.h5'
additional_categories['corresp_from_coco'] = additional_categories_path + 'corresp_coco_mitindoor_unique.json'
additional_categories['objects_encoder'] = additional_categories_path + 'mitindoor_objects_encoder.json'
additional_categories['objects_decoder'] = additional_categories_path + 'mitindoor_objects_decoder.json'
additional_categories['weights'] = additional_categories_path + 'weights_mitindoor.json'

category_1 = dict()
category_1['categories'] = additional_categories_path + 'category_1/category_1_categories.json'
category_1['model'] = additional_categories_path + 'category_1/category_1_model.h5'

category_2 = dict()
category_2['categories'] = additional_categories_path + 'category_2/category_2_categories.json'
category_2['model'] = additional_categories_path + 'category_2/category_2_model.h5'

category_3 = dict()
category_3['categories'] = additional_categories_path + 'category_3/category_3_categories.json'
category_3['model'] = additional_categories_path + 'category_3/category_3_model.h5'

additional_categories['category_1'] = category_1
additional_categories['category_2'] = category_2
additional_categories['category_3'] = category_3

paths['additional_categories'] = additional_categories


# Relationships identificator paths.
rels_identifier_path = scenes_tool_data_path + 'rels_identifier/'

rels_identifier = dict()

rels_identifier['weights'] = rels_identifier_path + 'weights_coco.json'
rels_identifier['objects_encoder'] = rels_identifier_path + 'coco_rel_idf_objects_encoder.json'
rels_identifier['output_decoder'] = rels_identifier_path + 'coco_rel_idf_output_decoder.json'
rels_identifier['model'] = rels_identifier_path + 'rels_identifier_model.h5'

paths['rels_identifier'] = rels_identifier


# Relationships definition paths.
rels_definers_path = scenes_tool_data_path + 'rels_definers/'

paths['rels_definers'] = dict()

# Unary relationships (attributes).
unary_rels = dict()

unary_classifiers_dir_path = rels_definers_path + 'unary_rels/'

unary_classifiers_list = listdir(unary_classifiers_dir_path)

paths['rels_definers']['unary_rels'] = [unary_classifiers_dir_path+model for model in unary_classifiers_list if model[-3:] == '.h5']

# Binary relationships (prepositions).
binary_rels = dict()

binary_rels['binary_classifier_classes'] = rels_definers_path + 'binary_rels/binary_classifier_classes.json'
binary_rels['binary_rels_predicates'] = rels_definers_path + 'binary_rels/binary_rels_predicates.pkl'
binary_rels['model'] = rels_definers_path + 'binary_rels/binary_classifier_model.h5'

paths['rels_definers']['binary_rels'] = binary_rels
