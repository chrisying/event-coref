# Parses the documents in events/ and adds it to the graph, then links
# the entities to YAGO entities
import json
import logging

import networkx as nx

from node import Node
from constants import *

# Parse single line from event tagger file
def parse_ee_line(line):
    tokens = line.strip().split('\t')
    locs = tuple(map(int, tokens[1].split(',')))

    if tokens[2] == 'EVENT':
        return tokens[0], locs, tokens[4]
    else:
        return tokens[0], locs, tokens[3]

# Adds entities from file to list
# Will modify entities list
# THIS IS SUPER INEFFICIENT BECAUSE THE SORTING ORDER FOR EVENTS IS NOT THE SAME AS THAT OF THE ENTITIES
def process_entities(curDoc, entities):
    found = False
    with open(ENTITIES) as f:
        for line in f.xreadlines():
            entityDoc, entityLoc, entity = parse_ee_line(line)
            if entityDoc != curDoc:
                if found:
                    break
                else:
                    continue
            found = True
            entities.append((entityLoc, entity))

# Put doc, events, entities into graph with edges
def process_doc(graph, doc, events, entities):
    if not doc:
        return
    logging.debug('Processing document %s' % doc)

    docNode = Node(DOC, doc)
    graph.add_node(docNode)

    eventsBySentence = {}
    for event in events:
        sentNum = event[0][0]
        if sentNum not in eventsBySentence:
            eventsBySentence[sentNum] = []
        eventsBySentence[sentNum].append(Node(EVENT, (doc, event)))

    entitiesBySentence = {}
    for entity in entities:
        sentNum = entity[0][0]
        if sentNum not in entitiesBySentence:
            entitiesBySentence[sentNum] = []
        entitiesBySentence[sentNum].append(Node(ENTITY, (doc, entity)))

    mapping = loadYAGO(doc)  # load appropriate YAGO AIDA file
    for sentNum in eventsBySentence:
        for event in eventsBySentence[sentNum]:
            graph.add_node(event)
            graph.add_edge(docNode, event)
            if sentNum in entitiesBySentence:
                for entity in entitiesBySentence[sentNum]:
                    graph.add_node(entity)
                    graph.add_edge(event, entity)
                    connectToYAGO(mapping, graph, entity)

# Reads the data in the appropriate file once and returns a dict of
# (sentence num, token num) -> YAGO entity
def loadYAGO(doc):
    logging.debug('Loading %s into JSON' % doc)
    with open(ECB_YAGO + doc + '.txt.json', 'r') as f:
        data = json.loads(f.readline())
        # Pretty-print the data
        # print json.dumps(data, indent=4, separators=(',', ': '))

        # \n does NOT count as a character
        sentences = data["originalText"].split("\n")
        slens = map(len, sentences)

        # space DOES count as a character
        tokens = map(lambda s:s.split(), sentences)
        tlens = map(lambda ts:map(lambda t:len(t), ts), tokens)

        mapping = {}
        mentions = data["mentions"]
        for mention in mentions:
            if "bestEntity" not in mention:
                continue

            offset = mention["offset"]
            s = 0
            while slens[s] < offset:
                offset -= slens[s]
                offset -= 1
                s += 1

            t = 0
            while offset >= 1:
                offset -= tlens[s][t]
                offset -= 1  # Accounting for space
                t += 1

            mapping[(s, t)] = mention["bestEntity"]["kbIdentifier"]
            # print "Mapped (%d, %d) to %s" % (s, t, mapping[(s,t)])

        return mapping

# Link the entity to a YAGO entity and put it into the graph
def connectToYAGO(mapping, graph, entityNode):
    key = (entityNode.nodeValue[1][0][0], entityNode.nodeValue[1][0][1])
    if key in mapping:
        ynode = Node(YAGO_ENTITY, mapping[key])
        graph.add_node(ynode)
        graph.add_edge(entityNode, ynode)
        #print "Linked %s to %s" % (str(entityNode.nodeValue), mapping[key])

# Main function that will be called to run all the code here
def process_events(graph):
    logging.debug('Starting processing events and entities from AIDA')
    curDoc = ''
    events = []
    entities = []

    with open(EVENTS) as fevents, open(ENTITIES) as fentities:
        while True:
            line = fevents.readline()
            if not line:
                break

            eventDoc, eventLoc, anchor = parse_ee_line(line)
            if eventDoc != curDoc:
                process_entities(curDoc, entities)
                process_doc(graph, curDoc, events, entities)
                curDoc = eventDoc
                events = []
                entities = []

            events.append((eventLoc, anchor))

        process_entities(curDoc, entities)
        process_doc(graph, curDoc, events, entities)
