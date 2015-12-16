import sys
import re

def parse_edge(edges, vertex, item):
	if item.startswith("[") and item.endswith("]"):
		edge = item[1:-1].split(',')[0]
		if edge not in edges:
			edges[edge] = []
		edges[edge].append(vertex)
	else:
		raise ValueError("edge doesn't start and end with brackets")

def parse_edge_list(edges, vertex, the_list):
	if the_list.startswith("[") and the_list.endswith("]"):
		the_list = the_list[1:-1]
		for item in re.findall("[^,]+,[^,]+", the_list):
			parse_edge(edges, vertex, item)
	else:
		raise ValueError("edge list doesn't start and end with brackets")

def parse_record(edges, record):
	if record.startswith("[") and record.endswith("]\n"):
		fields = record[1:-2].split(',')
		parse_edge_list(edges, fields[0], ",".join(fields[2:]))
	else:
		raise ValueError("record doesn't start and end with brackets")

def print_graph(graph):
	for vertex, edges in graph.iteritems():
		record = "[" + str(vertex) + ",0,["
		for edge in edges:
			record += "[" + str(edge) + ",1],"
		record = record[:-1] + "]]"
		print record

with open(sys.argv[1]) as f:
	inverted_graph = {}
	for line in f:
		parse_record(inverted_graph, line)
	print_graph(inverted_graph)

