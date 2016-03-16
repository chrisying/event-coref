
# Node that will be in the networkx graph
class Node:

    def __init__(self, nodeType, nodeValue):
        # Valid types enum'ed above
        self.nodeType = nodeType
        self.nodeValue = nodeValue

    # Required to make object hashable
    def __hash__(self):
        return hash((self.nodeType, self.nodeValue))

    # Required to make object hashable
    def __eq__(self, other):
        return (self.nodeType == other.nodeType and
                self.nodeValue == other.nodeValue)

    def __str__(self):
        return 'Node(%d, %s)' % (self.nodeType, str(self.nodeValue))

    def __repr__(self):
        return 'Node(%d, %s)' % (self.nodeType, repr(self.nodeValue))
