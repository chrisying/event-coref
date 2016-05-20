# Constants

EVENTS = 'events/full_event'
NUM_EVENTS = 7286
TRAIN_PAIRS = 'events/train_event_mentionpairs.txt'
TEST_PAIRS = 'events/test_event_mentionpairs.txt'
ENTITIES = 'events/full_entity'
ECB_YAGO = 'ecb/json/'
GRAPH_OUTPUT = 'output/data_graph_depth_2'
YAGO_DBPEDIA = 'dbpedia/yago_links.nt'
DBPEDIA = 'dbpedia/mappingbased-properties_en.nt'
DBPEDIA_PREFIX = 'http://dbpedia.org'
ANNOTATION_DIR = 'ecb/annotations/'

# Feature matrix outputs
BOW_MATRIX = 'output/bow_matrix'
YAGO_MATRICES = 'output/yagomats/'
DB_MATRICES = 'output/dbmats/'

# Cluster outputs
BOW_CLUSTERS = 'output/b_clusters/'
BOW_YAGO_CLUSTERS = 'output/by_clusters/'
BOW_YAGO_DB_CLUSTERS = 'output/byd_clusters/'

# Node type enums
DOC = 1
EVENT = 2
ENTITY = 3
YAGO_ENTITY = 4
DB_ENTITY = 5

# DBpedia depth
DEPTH = 2

# Backoff constants
BOW_CST = 0.25
YAGO_CST = 0.5
DB_CST = 0.25
