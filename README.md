# JHUApacheGiraph
Project source for Apache Giraph project in Big Data Processing.

Contents:
 - apache-giraph - contains custom Java source files
   - Custom input format using String vertex IDs
   - Custom shortest paths computation
 - graphs - contains the graphs at each stage of the data flow
   1. Graph 1 - output of gene_graph.pig
   2. Graph 2 - directed graph in JSONArray format
   3. Graph 3 - inverse directed graph in JSONArray format
   4. Graph 4 - concatenation of graphs 2 and 3
 - gene_graph.pig - parses the raw text of all input files and finds all genes according to a provdided gene database; it then groups all genes together and lists which files they appear in
 - inverse_graph.py - creates the inverse directed graph
 - giraph-output.txt - the output of Apache Giraph
