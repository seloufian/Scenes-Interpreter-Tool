import collections
import inflect as ift


class Graph:
	def __init__(self):
		self.nodes = []
		self.edges = []

	def add_node(self, o):
		# Check if nodes contains 'o'
		for node in self.nodes:
			if node.get_id() == o:
				return

		self.nodes.append(Node(o))

	def add_node_feature(self, o, feature):
		for i in range(len(self.nodes)):
			if self.nodes[i].get_id() == o:
				self.nodes[i].add_feature(feature)
				break

	def set_nodes(self, nodes):
		self.nodes = nodes

	def add_edge(self, o1, o2, rel):
		nodes = [node for node in self.nodes if node.get_id() == o1]

		if len(nodes) == 0:
			# The node doesn't exist yet
			# Add it to the nodes list
			self.add_node(o1)
			node1 = [node for node in self.nodes if node.get_id() == o1][0]
		else:
			node1 = nodes[0]

		nodes = [node for node in self.nodes if node.get_id() == o2]

		if len(nodes) == 0:
			# The node doesn't exist yet
			# Add it to the nodes list
			self.add_node(o2)
			node2 = [node for node in self.nodes if node.get_id() == o2][0]
		else:
			node2 = nodes[0]

		self.edges.append(Relation(node1, node2, rel))

	def set_edges(self, edges):
		self.edges = edges

	def get_nodes(self):
		return self.nodes

	def get_edges(self):
		return self.edges

	def get_sub_graphs(self):
		''' Returns a list of graphs '''

		sub_graphs = []
		nodes = self.nodes
		edges = self.edges

		while len(nodes) > 0:
			sub_graph_nodes = [nodes[0]]
			sub_graph_edges = []
			not_viewed_yet = [nodes[0]]

			while len(not_viewed_yet) > 0:
				node = not_viewed_yet[0]
				i = 0

				while i < len(edges):
					edge = edges[i]

					if edge.get_o1() == node:
						not_viewed_yet.append(edge.get_o2())
						sub_graph_nodes.append(edge.get_o2())
						sub_graph_edges.append(edge)
						del edges[i]
					else:
						i += 1

				del not_viewed_yet[0]

			sub_graph = Graph()
			sub_graph.set_nodes(sub_graph_nodes)
			sub_graph.set_edges(sub_graph_edges)

			sub_graphs.append(sub_graph)
			i = 0

			while i < len(nodes):
				if nodes[i] in sub_graph_nodes:
					del nodes[i]
				else:
					i += 1

		return sub_graphs



class Node:
	def __init__(self, id):
		self.name = id.split('_')[0]
		self.id = id
		self.features = []

	def get_name(self):
		return self.name

	def get_id(self):
		return self.id

	def get_features(self):
		return self.features

	def add_feature(self, feature):
		self.features.append(feature)



class Relation:
	def __init__(self, o1, o2, name):
		self.o1 = o1
		self.o2 = o2
		self.name = name

	def get_name(self):
		return self.name

	def get_o1(self):
		return self.o1

	def get_o2(self):
		return self.o2



''' Necessary functions to make rules '''

def edge2phrase(edge):
	node1 = edge.get_o1()
	rel = edge.get_name()
	node2 = edge.get_o2()

	return combine_feature_with_object(node1) + ' ' + rel + ' ' + combine_feature_with_object(node2)


def join_items(items):
	if len(items) == 0:
		return ''

	elif len(items) == 1:
		return items[0]

	elif len(items) == 2:
		return items[0] + ' and ' + items[1]

	res = ''
	i = 0

	while i < len(items)-2:
		res += items[i] + ', '
		i += 1

	res += items[i] + ' and ' + items[i+1]

	return res


def put_a_an(word):
	if word[0] in ['a', 'e', 'i', 'o', 'u']:
		a = 'an '
	else:
		a = 'a '
	return a + word


def plural(word):
	p = ift.engine()
	return p.plural(word)


def combine_feature_with_object(node):
	if len(node.get_features()) == 0:
		return put_a_an(node.get_name())
	else:
		return put_a_an(node.get_features()[0]) + ' ' + node.get_name()


def conjugate(word):
	# Verify if this word is a verb
	verbs_list = ['in', 'on', 'back', 'behind', 'inside', 'on left side of',
					'above', 'on open', 'on side of', 'before', 'on middle', 'in street holding',
					'on some', 'to', 'to right of', 'full of', 'under', 'outside of',
					'next to', 'on right side of', 'next to', 'in back of', 'inside of', 'on a dining room',
					'near', 'in', 'about to cut', 'front', 'on top of', 'in', 'of',
					'close to', 'on bike in front of a', 'against', 'on bus', 'typing on', 'in front of',
					'with a', 'up on', 'of water on', 'with half', 'outside', 'filled with',
					'placed in', 'in a', 'underneath', 'for a', 'from', 'on a',
					'over a', 'by a', 'to left to', 'off', 'bedside of', 'between',
					'to board', 'with more', 'atop', 'into', 'in a suit using a gray', 'over',
					'near', 'beside', 'grouped with', 'on side of a', 'with h', 'within',
					'adjusting', 'at', 'on its', 'using', 'across', 'of a',
					'on small', 'on tilted', 'on front of', 'besides', 'below', 'with',
					'no longer on', 'through', 'around', 'on back of', 'on top of a']

	if word in verbs_list:
		return 'is ' + word
	else:
		return word


def isplural(word):
	p = ift.engine()

	if word in ['two', 'more']:
		return True

	singular_noun = p.singular_noun(word)

	if singular_noun == False:
		return singular_noun

	return True



def generate_description(rels, standard_category, additional_category1, additional_category2, additional_category3, no_relation=False):

	'''
	Parameters:
		rels (list of tuples): List of relations [(o1, r, o2), ...].
		standard_category (list of two tuples): [(category1, probability1), (category2, probability2)].
		additional_category1 (tuple): (category, probability).
		additional_category2 (tuple): (category, probability).
		additional_category3 (tuple): (category, probability).
		no_relation (bool): Signal if this scene has at least one, unary or binary, relation defined.

	Returns:
		(str): Description.
	'''

	# Verify if rels is empty or not
	if len(rels) == 0:
		return ''

	# Check if there is a need to construct a graph or not
	if no_relation: # If 'no_relation' is 'True' then there is no need to construct a graph
		potential_phrases = [(rel, 1) for rel in rels if len(rel) == 2]
		tmp = [rel for rel in rels if len(rel) != 2]

		for rel in list(set(rels)):
			if len(rel) != 2:
				i, occ = 0, 0

				while i < len(tmp):
					if tmp[i] == rel:
						occ += 1
						del tmp[i]
					else:
						i += 1
				potential_phrases.append((rel, occ))

		phrases = []

		for potential_phrase in potential_phrases:
			if potential_phrase[1] == 1:
				phrases.append(put_a_an(potential_phrase[0][1]) + ' ' + potential_phrase[0][0])
			else:
				if potential_phrase[1] == 2:
					phrases.append('two ' + plural(potential_phrase[0]))
				else:
					phrases.append('more than two ' + plural(potential_phrase[0]))

	else: # Transform the rels to a graph
		graph = Graph()

		for rel in rels:
			try:
				o1, r, o2 = rel[0], rel[1], rel[2]
				graph.add_edge(o1, o2, r)
			except:
				o1, r = rel[0], rel[1]
				if r == 'on':
					r = 'operating'
				graph.add_node(o1)
				graph.add_node_feature(o1, r)

		# Extract the isolated subgraphs
		sub_graphs = graph.get_sub_graphs()

		sub_graphs_with_only_one_node = []
		sub_graphs_with_only_two_nodes = []
		sub_graphs_with_more_than_two_nodes = []

		while len(sub_graphs) > 0:
			if len(sub_graphs[0].get_nodes()) == 1:
				sub_graphs_with_only_one_node.append(sub_graphs[0])
			elif len(sub_graphs[0].get_nodes()) == 2:
				sub_graphs_with_only_two_nodes.append(sub_graphs[0])
			else:
				sub_graphs_with_more_than_two_nodes.append(sub_graphs[0])

			del sub_graphs[0]

		sub_graph_numberOfApparition = []
		sub_graph_numberOfApparition = [(sub_graph, 1) for sub_graph in sub_graphs_with_more_than_two_nodes]

		# Treat the case of sub graphs with only two nodes
		if len(sub_graphs_with_only_two_nodes) > 0:

			while len(sub_graphs_with_only_two_nodes) > 0:
				sub_graph = sub_graphs_with_only_two_nodes[0]
				del sub_graphs_with_only_two_nodes[0]
				count = 1
				j = 0
				while j < len(sub_graphs_with_only_two_nodes):
					if sub_graphs_with_only_two_nodes[j].get_nodes()[0].get_name() == sub_graph.get_nodes()[0].get_name() and sub_graphs_with_only_two_nodes[j].get_nodes()[1].get_name() == sub_graph.get_nodes()[1].get_name():
						count += 1
						del sub_graphs_with_only_two_nodes[j]
					elif sub_graphs_with_only_two_nodes[j].get_nodes()[0].get_name() == sub_graph.get_nodes()[1].get_name() and sub_graphs_with_only_two_nodes[j].get_nodes()[1].get_name() == sub_graph.get_nodes()[0].get_name():
						count += 1
						del sub_graphs_with_only_two_nodes[j]
					else:
						j += 1
				sub_graph_numberOfApparition.append((sub_graph, count))

		# Treat the case of sub graphs with only one node
		if len(sub_graphs_with_only_one_node) > 0:

			while len(sub_graphs_with_only_one_node) > 0:
				sub_graph = sub_graphs_with_only_one_node[0]
				del sub_graphs_with_only_one_node[0]
				count = 1
				j = 0
				while j < len(sub_graphs_with_only_one_node):
					if sub_graphs_with_only_one_node[j].get_nodes()[0].get_name() == sub_graph.get_nodes()[0].get_name() and sub_graphs_with_only_one_node[j].get_nodes()[0].get_features()[0] == sub_graph.get_nodes()[0].get_features()[0]:
						count += 1
						del sub_graphs_with_only_one_node[j]
					else:
						j += 1
				sub_graph_numberOfApparition.append((sub_graph, count))

		# Remove the sub graphs with two nodes if the edge exist in other sub-graphs with three nodes or more
		i = 0
		while i < len(sub_graph_numberOfApparition):
			sub_graph, _ = sub_graph_numberOfApparition[i]
			if len(sub_graph.get_nodes()) == 2:
				j = 0
				while j < len(sub_graph_numberOfApparition):
					if len(sub_graph_numberOfApparition[j][0].get_nodes()) >= 3:
						edges = sub_graph_numberOfApparition[j][0].get_edges()
						sub_graph_edge = sub_graph.get_edges()[0]
						br = False
						for edge in edges:
							if edge.get_name() == sub_graph_edge.get_name():

								if edge.get_o1().get_name() == sub_graph_edge.get_o1().get_name() and edge.get_o2().get_name() == sub_graph_edge.get_o2().get_name():
									del sub_graph_numberOfApparition[i]
									br = True
									break
								elif edge.get_o1().get_name() == sub_graph_edge.get_o2().get_name() and edge.get_o2().get_name() == sub_graph_edge.get_o1().get_name():
									del sub_graph_numberOfApparition[i]
									br = True
									break
						if br:
							break

					j += 1
				if j == len(sub_graph_numberOfApparition):
					i += 1
			else:
				i += 1

		# Remove the sub graphs with only one node if the node name exist in other sub-graphs with two or three nodes
		i = 0
		while i < len(sub_graph_numberOfApparition):
			sub_graph, _ = sub_graph_numberOfApparition[i]
			if len(sub_graph.get_nodes()) == 1:
				j = 0
				while j < len(sub_graph_numberOfApparition):
					if len(sub_graph_numberOfApparition[j][0].get_nodes()) == 2:
						node1 = sub_graph_numberOfApparition[j][0].get_nodes()[0]
						node2 = sub_graph_numberOfApparition[j][0].get_nodes()[1]
						node = sub_graph.get_nodes()[0]
						if node.get_name() in [node1.get_name(), node2.get_name()]:
							del sub_graph_numberOfApparition[i]
							break
					elif len(sub_graph_numberOfApparition[j][0].get_nodes()) == 3:
						edges = sub_graph_numberOfApparition[j][0].get_edges()
						node = sub_graph.get_nodes()[0]

						br = False
						for edge in edges:
							if node.get_name() in [edge.get_o1().get_name(), edge.get_o2().get_name()]:
								del sub_graph_numberOfApparition[i]
								br = True
								break
						if br:
							break

					j += 1
				if j == len(sub_graph_numberOfApparition):
					i += 1

			else:
				i += 1

		phrases = []
		for sub_graph, numberOfApparition in sub_graph_numberOfApparition:
			if len(sub_graph.get_nodes()) == 1:
				node = sub_graph.get_nodes()[0]
				if numberOfApparition == 1:
					phrase = put_a_an(node.get_features()[0]) + ' ' + node.get_name()
				elif numberOfApparition == 2:
					phrase = 'two ' + node.get_features()[0] + ' ' + plural(node.get_name())
				else:
					phrase = 'more than two ' + node.get_features()[0] + ' ' + plural(node.get_name())
			elif len(sub_graph.get_nodes()) == 2:
				edge = sub_graph.get_edges()[0]
				node1 = edge.get_o1()
				node2 = edge.get_o1()
				rel = edge.get_name()

				if numberOfApparition == 1:
					phrase = edge2phrase(edge)
				else:
					if node1.get_name() == node2.get_name():
						phrase = plural(node1.get_name()) + ' ' + rel + ' other ' + plural(node2.get_name())
					else:
						phrase = plural(node1.get_name()) + ' ' + rel + ' ' + plural(node2.get_name())
			elif len(sub_graph.get_nodes()) == 3:
				if len(sub_graph.get_edges()) == 2:
					# determine the node which is connected with the two others
					node_freq = collections.Counter()
					for edge in sub_graph.get_edges():
						node_freq[edge.get_o1()] += 1
						node_freq[edge.get_o2()] += 1

					node = list(node_freq.most_common())[0][0]
					edges = sub_graph.get_edges()

					if edges[0].get_o1() == node and edges[1].get_o1() == node:
						# case 1
						node1 = edges[0].get_o2()
						rel1 = edges[0].get_name()

						node2 = edges[1].get_o2()
						rel2 = edges[1].get_name()

						if node.get_name() != node1.get_name():
							phrase = combine_feature_with_object(node) + ' that ' + conjugate(rel1) + ' ' + combine_feature_with_object(node1) + ', ' + conjugate(rel2) + ' ' + combine_feature_with_object(node2)
						else:
							phrase = combine_feature_with_object(node) + ' that ' + conjugate(rel1) + ' another ' + node1.get_name() + ', ' + conjugate(rel2) + ' ' + combine_feature_with_object(node2)

					elif edges[0].get_o2() == node and edges[1].get_o2() == node:
						# case 2
						node1 = edges[0].get_o2()
						rel1 = edges[0].get_name()

						node2 = edges[1].get_o2()
						rel2 = edges[1].get_name()

						if rel1 == rel2:
							# case 1
							if node1.get_name() == node2.get_name():
								phrase = 'two ' + plural(node1.get_name()) + ' ' + rel1 + ' ' + combine_feature_with_object(node)
							else:
								phrase = combine_feature_with_object(node1) + ' and ' + combine_feature_with_object(node2) + ' ' + rel1 + ' ' + combine_feature_with_object(node)
						else:
							# case 2
							phrase = combine_feature_with_object(node1) + ' ' + rel1 + ' ' + combine_feature_with_object(node) + ' and ' + combine_feature_with_object(node2) + ' ' + rel2 + ' the same ' + node.get_name()

					else:
						# case 3
						if edges[0].get_o2() == node:
							node1 = edges[0].get_o1()
							rel1 = edges[0].get_name()

							node2 = edges[1].get_o2()
							rel2 = edges[1].get_name()

						else:
							node1 = edges[1].get_o1()
							rel1 = edges[1].get_name()

							node2 = edges[0].get_o2()
							rel2 = edges[0].get_name()

						if node.get_name() == node2.get_name():
							phrase = combine_feature_with_object(node1) + ' ' + rel1 + ' ' + combine_feature_with_object(node) + ' that ' + conjugate(rel2) + ' another one'
						else:
							phrase = combine_feature_with_object(node1) + ' ' + rel1 + ' ' + combine_feature_with_object(node) + ' that ' + conjugate(rel2) + ' ' + combine_feature_with_object(node2)

				else: # == 3
					phrase = join_items([edge2phrase(edge) for edge in sub_graph.get_edges()])

			else:
				phrase = join_items([edge2phrase(edge) for edge in sub_graph.get_edges()])

			phrases.append(phrase)

	if standard_category[0][1] >= 0.6:
		prec = 'In this ' + standard_category[0][0] + ' there '
	else:
		classes = []
		if additional_category1[1] >= 0.6 and additional_category1[0] not in ['either', 'Nothing', '7transport']:
			classes.append(additional_category1[0])
		if additional_category2[1] >= 0.6 and additional_category2[0] not in ['either', 'Nothing', '7transport']:
			classes.append(additional_category2[0])
		if additional_category3[1] >= 0.6 and additional_category3[0] not in ['either', 'Nothing', '7transport']:
			classes.append(additional_category3[0])
		if len(classes) > 0:
			prec = 'In this ' + join_items(classes) + ' place there '
		else:
			standard_classes = []
			additional_classes = []
			if standard_category[0][1] >= 0.4:
				standard_classes.append(standard_category[0][0])
				if standard_category[1][1] >= 0.4:
					standard_classes.append(standard_category[1][0])

			if additional_category1[1] >= 0.4 and additional_category1[0] not in ['either', 'Nothing', '7transport']:
				additional_classes.append(additional_category1[0])
			if additional_category2[1] >= 0.4 and additional_category2[0] not in ['either', 'Nothing', '7transport']:
				additional_classes.append(additional_category2[0])
			if additional_category3[1] >= 0.4 and additional_category3[0] not in ['either', 'Nothing', '7transport']:
				additional_classes.append(additional_category3[0])

			classes = standard_classes + additional_classes
			if len(classes) == 1:
				if len(standard_classes) == 1:
					prec = 'In this scene that represents probably ' + put_a_an(classes[0]) + ' there '
				else:
					prec = 'In this scene that represents probably ' + put_a_an(classes[0]) + ' place there '
			else:
				if len(standard_classes) > 0:
					prec = 'In this scene that represents probably ' + ' or '.join([put_a_an(cat) for cat in standard_classes]) + ' there '
				else:
					if len(additional_classes) > 0:
						prec = 'In this scene that represents probably ' + ' or '.join([put_a_an(cat) for cat in additional_classes]) + ' there '
					else:
						# There is no class that has a prob >= 40%
						# Get the classes (standard/additional) having prob >= 20%
						if standard_category[0][1] >= 0.2:
							standard_classes.append(standard_category[0][0])
							if standard_category[1][1] >= 0.2:
								standard_classes.append(standard_category[1][0])

						if additional_category1[1] >= 0.2 and additional_category1[0] not in ['either', 'Nothing', '7transport']:
							additional_classes.append(additional_category1[0])
						if additional_category2[1] >= 0.2 and additional_category2[0] not in ['either', 'Nothing', '7transport']:
							additional_classes.append(additional_category2[0])
						if additional_category3[1] >= 0.2 and additional_category3[0] not in ['either', 'Nothing', '7transport']:
							additional_classes.append(additional_category3[0])

						classes = standard_classes + additional_classes
						if len(classes) == 1:
							if len(standard_classes) == 1:
								prec = 'In this scene that represents perhaps ' + put_a_an(classes[0]) + ' there '
							else:
								prec = 'In this scene that represents perhaps ' + put_a_an(classes[0]) + ' place there '
						else:
							if len(standard_classes) > 0:
								prec = 'In this scene that represents perhaps ' + ' or '.join([put_a_an(cat) for cat in standard_classes]) + ' there '
							else:
								if len(additional_classes) > 0:
									prec = 'In this scene that represents perhaps ' + ' or '.join([put_a_an(cat) for cat in additional_classes]) + ' there '
								else:
									# there is 0 class
									prec = 'In this scene there '

	if len(phrases) > 1:
		prec += 'are '
	else:
		first_word = phrases[0].split()[0]
		if isplural(first_word):
			prec += 'are '
		else:
			prec += 'is '

	return prec + join_items(phrases) + '.'
