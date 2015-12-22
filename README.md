# JHUApacheGiraph
Final project source for an Apache Giraph project in Big Data Processing with Hadoop.

## Goal
The goal of this project is to use several Hadoop tools and subprojects in order to gather useful gene information from a very large collection of research publications. Specifically this project accomplishes the following:
 - Convert articles from PDF to raw text using Apache Tika
 - Perform intermediate data processing using Apache Pig
 - Perform graph processing using Apache Giraph

## Fetching the Data
I pulled all sample data from the [PubMed Central FTP Service](http://www.ncbi.nlm.nih.gov/pmc/tools/ftp/), which permits data mining. The service has a file list index that maps the URLs of 100,000+ articles. I used grep to filter that file list to include articles that have the latest genomics data. I chose to download all articles from the Genome Biology journal in 2015 with the assumption that they would more frequently mention gene names. I then used wget to fetch the sample of 271 PDF files. The filtered file containing the PDF URLs used in the sample is located here: [genome_biol_2015.pdf_urls.txt](meta/genome_biol_2015.pdf_urls.txt).

The other piece of data I collected was gene information from the [NIH Gene Database](http://www.ncbi.nlm.nih.gov/gene). Specifically I downloaded the list of about 60,000 known human genes located on their FTP service. A Pig script will later cross-reference the gene names in this file with the words in the articles in order to identify genes. The cleaned up list of human genes is located here (NOTE: this is a large 1MB file): [Human_Gene_List.txt](https://github.com/demarna1/JHUApacheGiraph/blob/master/meta/Human_Gene_List.txt).

## Converting PDFs to Raw Text
I used Apache Tika to convert the 271 PDF sample size into raw text format. Apache Tika can be built into a Java project or MapReduce project or it can be run from the command line. I decided to use the command line to operate on the sample and then I copied the raw article text into HDFS.

```
java -jar tika-app-1.11.jar --text-main --inputDir pubmed/pdf/ --outputDir pubmed/data/
hadoop fs -copyFromLocal Documents/Project/pubmed/data/* /project/rawtext
```

I cleaned up the gene information file to only consist of their names and their IDs and then copied it into HDFS.

```
hadoop fs -copyFromLocal Documents/Project/pubmed/genes/Human_Gene_List.txt /project
```

## Creating the Graph
The following 4 steps create a large graph of genes and articles and put it into a format that Apache Giraph can read.

### Step 1 - Pig Script
At this point, all of the data to be processed is in HDFS at these locations:

```
/project/rawtext/ #Contains 271 raw text articles
/project/Human_Gene_List.txt #Gene database
```

The next step is to run a Pig script that will process the data into graph format. The data flow of the Pig script is described below in Figure 1.

![Figure 1](images/pig_data_flow.png)

The Pig script source is located here: [gene_graph.pig](gene_graph.pig). The script parses the raw text of all input files and finds all genes according to the provided gene database. It then groups all genes together and maintains a list of articles that each gene appears in.

The generated Pig output graph is located here: [1-gene-graph-output.txt](graphs/1-gene-graph-output.txt).

### Step 2 - Reformat the Graph
The output file format needs to be transformed so that Apache Giraph can process it. The following sed script transforms Pig output into JSONArray format.

```
sed 's/^/[/g; s/\t/,0,/g; s/.txt/.txt,1/g; s/[{(]/[/g; s/[})]/]/g; s/$/]/g' 1-gene-graph-output.txt > 2-gene-giraph-directed.txt
```

I also cleaned up the file by removing all two-letter genes. The two letter genes (such as ‘AN’) were sometimes misrepresented in the text. The cleaned-up formatted graph is located here: [2-gene-giraph-directed.txt](graphs/2-gene-giraph-directed.txt).

### Step 3 - Create Inverse Graph
Apache Giraph only accepts directed graphs as input. The graph I have generated to this point only has the edges from gene -> article. I wrote a Python script to create the inverse graph which has edges from article -> gene. Steps 2 and 3 would ideally be done as part of the above Pig script since it would be processing a much larger graph then my sample graph.

The Python script that creates the inverse directed graph in JSONArray format is located here: [inverse_graph.py](inverse_graph.py).

The output of the Python script is located here: [3-gene-giraph-inverse.txt](graphs/3-gene-giraph-inverse.txt)

### Step 4 - Combine Original and Inverse Graphs
The inverse graph is then concatenated with the graph from step 2 to create the full bidirectional input graph that will be passed to Apache Giraph. It can be found here: [4-gene-giraph-input.txt](graphs/4-gene-giraph-input.txt). 

## Apache Giraph
[Apache Giraph](http://giraph.apache.org/intro.html) is designed to operate on very large graphs. The framework utilizes a vertex-centric approach with message passing that occurs along the edges during each superstep.

![Figure 2](images/sample_subgraph.png)

The graph that I generated in my project is essentially a very large bipartite graph; a small sample is shown above in Figure 2. My goal for using Giraph is to find all of the nearest neighbors of a user-provided input gene. In the example above, if the user wants information on the gene “RASSF8”, Giraph will return “CTXP” as the primary neighbor (2 edges away) and “HULIS5” and “ABT” as secondary neighbors (4 edges away). It will also return the articles that connect them (1 and 3 edges away).

My solution uses a shortest path algorithm to find all of the nearest neighbors. The example output is illustrated below in Figure 3.

![Figure 3](images/graph_illustration.png)

In order to run Apache Giraph with my input graph, I needed a custom input format. I created a new JSON input format that uses Strings for the vertex IDs. It is based on the built-in format JsonLongDoubleFloatDoubleVertexInputFormat, which uses Longs for vertex IDs. The input format source code is located here: [JsonStringDoubleFloatDoubleVertexInputFormat.java] (apache-giraph/JsonStringDoubleFloatDoubleVertexInputFormat.java)

I also needed to modify the built-in SimpleShortestPathsComputation algorithm to support String vertex IDs. The new custom class is located here: [SimpleShortestPathsTextComputation.java] (apache-giraph/SimpleShortestPathsTextComputation.java)

The following command executes the Apache Giraph job, which runs the modified ShortestPaths algorithm on the input graph I created in step 4. The job is configured to find the nearest neighbors of the “RASSF8” gene.

```
hadoop jar /usr/local/hadoop/giraph/giraph-examples/target/giraph-examples-1.2.0-SNAPSHOT-for-hadoop-1.2.1-jar-with-dependencies.jar \
    org.apache.giraph.GiraphRunner \
    org.apache.giraph.examples.SimpleShortestPathsTextComputation \
    -vif org.apache.giraph.io.formats.JsonStringDoubleFloatDoubleVertexInputFormat \
    -vip /giraph-input/4-gene-giraph-input.txt \
    -vof org.apache.giraph.io.formats.IdWithValueTextOutputFormat \
    -op /giraph-output -w 1
```

The output result is located here (NOTE: the vertices are not sorted by shortest path): [giraph-output.txt](giraph-output.txt)
