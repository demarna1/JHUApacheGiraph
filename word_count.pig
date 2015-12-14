rawtext = load '/project/rawtext' using PigStorage('\n', '-tagFile') as (filename:chararray, line:chararray);
words = foreach rawtext generate flatten(TOKENIZE(line)) as word, filename;
wordgroups = group words by word;
wordcount = foreach wordgroups generate COUNT(b), group;
store wordcount into '/project/wordcount/';
