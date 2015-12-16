import sys

def parse_article(articles, gene, item):
	pass

def parse_article_list(articles, gene, the_list):
	print the_list
	return
	if the_list.startswith("[") and the_list.endswith("]"):
		items = the_list[1:-1].split(',')
		for i in items:
			parse_article(articles, gene, i)
	else:
		raise ValueError("article list doesn't start and end with brackets")

def parse_record(articles, record):
	if record.startswith("[") and record.endswith("]\n"):
		fields = record[1:-2].split(',')
		parse_article_list(articles, fields[0], ",".join(fields[2:]))
	else:
		raise ValueError("record doesn't start and end with brackets")

with open(sys.argv[1]) as f:
	articles = {}
	for line in f:
		parse_record(articles, line)

