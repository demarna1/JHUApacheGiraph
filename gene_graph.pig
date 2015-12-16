-- Load the gene table and the raw article text
genes = load 'hdfs://localhost:9000/project/Human_Gene_List.txt'
    using PigStorage('\t') as (id:int, gene:chararray);
rawtext = load 'hdfs://localhost:9000/project/rawtext'
    using PigStorage('\n', '-tagFile') as (filename:chararray, line:chararray);

-- Parse raw text into words and their file source
words = foreach rawtext generate flatten(TOKENIZE(line)) as word, filename;
filteredWords = filter words by word matches '\\w+';

-- Filter out words not in the gene table
joinedGenes = join filteredWords by word, genes by gene;
joinedGenesRenamed = foreach joinedGenes generate genes::gene as gene,
    filteredWords::filename as filename;

-- Group genes together and create the gene graph
groupedGenes = group joinedGenesRenamed by gene;
geneGraph = foreach groupedGenes {
  unique_filenames = distinct joinedGenesRenamed.filename;
  generate group as gene, unique_filenames as filename;
};

-- Store the graph in HDFS
store geneGraph into 'hdfs://localhost:9000/project/genegraph';

