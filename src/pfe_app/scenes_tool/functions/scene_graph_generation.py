from collections import defaultdict
from io import BytesIO

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from PIL import Image


def get_scene_graph(relations, no_relation_defined=False):

	# 'Matplotlib' display configuration
	plt.ioff()
	plt.figure(figsize=(8, 8))
	plt.axis('off')
	plt.margins(0.15)

	buf = BytesIO() # a 'buffer', to save scene graph figure

	G = nx.DiGraph() # Create an empty directed graph

	if no_relation_defined: # 'relations' is a list of objects (without index)
		nodes_indexes = defaultdict(int)

		for obj in relations:
			nodes_indexes[obj] += 1
			node_name = obj + '_' + str(nodes_indexes[obj]) # Add index to object name

			G.add_node(node_name)

		pos = nx.spring_layout(G)

		nx.draw(G, pos, arrowsize=20, node_size=6000, font_size=15, node_color='#D1D1D1',
				font_weight='bold', labels={node:node for node in G.nodes()})
	else:
		labels = dict()
		attributes = dict()

		for rel in relations:
			if len(rel) == 2: # Unary relationship
				obj_name, attribute = rel
				attributes[obj_name] = attribute
				G.add_node(obj_name)
			else: # Binary relationship
				obj_1_name, descriptor, obj_2_name = rel
				labels[(obj_1_name, obj_2_name)] = descriptor
				G.add_edge(obj_1_name, obj_2_name)

		pos = nx.spring_layout(G)

		nx.draw(G, pos, arrowsize=20, node_size=6000, font_size=15, node_color='#D1D1D1',
				font_weight='bold', labels={node:node for node in G.nodes()})

		nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='red', font_weight='bold')

		for obj_name, attribute in attributes.items():
			x, y = pos[obj_name]
			plt.text(x, y-0.12, s=attribute, bbox=dict(facecolor='red', alpha=0.5), 
					horizontalalignment='center', fontsize=14)

	plt.savefig(buf, format='png')

	buf.seek(0)

	return np.asarray(Image.open(buf))
