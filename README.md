Code dump for event coreference research project
======
Note: this is a code *dump* for a reason. The code is quite hacky since the overwhelming majority of it deals with parsing ECB/AIDA/YAGO/DBpedia/etc... data. The code itself may not be extremely useful for this reason since I make a lot of assumptions about the input/output data.

To replicate the results, consider rewriting the code using snippets from my code but customized to your data and desired outputs.

## General pipeline:
1.  parse_data.py  
    Input: annotated events, ECB json, YAGO, DBpedia files  
    Output: Text-KB graph
2.  extract_subevent_features.py  
    Input: annotated events, Text-KB graph  
    Output: feature vectors for BOW/YAGO/DB
3.  cluster_subevent.py  
    Input: feature vectors  
    Output: events clustered within a topic

## Alternate pipeline (uses pairwise coreference instead):
1.  same step 1
2.  generate_vectors.py  
    Input: annotated events, Text-KB graph, pairwise training/test data  
    Output: feature vectors from training and test data
3.  Call external machine learning algorithm to train and evaluate data
4.  calculate_scores.py  
    Input: pairwise classify outputs  
    Output: different metrics for the classification

## Other files:
- cluster.py: clustering code (agglomerative clustering using min-link)
- combine_clusters.py: combines outputs from all topics
- constants.py: contains most of the file names and constants used in the other files, variables can be recognized by ALL_CAPS (note: this is in the gitignore since file paths are different)
- node.py: Text-KB graph node
- process_dbpedia.py: used by parse_data.py to parse DBpedia entries
- process_events.py: used by parse_data.py to parse annotated events
- remove_baseline.py: removes baseline features from pairwise classification
- remove_same_sent.py: removes same sentence pairs from data
- baseline.py: [OLD] baseline clustering with BOW
- baseline_graph_cluster.py: [OLD] baseline clustering with BOW/YAGO
- extract_features.py: [OLD] feature extraction for topics (ignores subevents)
- cluster_data.py: [OLD] clusters documents into topics

## Constants:
I kept all my constants in a file called constants.py. Much of the code depends on constants, which are defined in ALL_CAPS. A sample constants.py is included, though the exact file locations depend on where your data is. The constants.py is the file used for the "Alternate pipeline", which was used to  obtain the final results.

See individual files for specific documentation.
