#!/usr/bin/env python

import optparse
import sys

import os
import igraph
import cairo
import numpy as np


# PARSER OPTIONS * * * * * * * * * * * * * * * * * *
parser = optparse.OptionParser()
parser.add_option("-n", "--number", dest="numTemplates", type=int,
                help="assign number of waveforms to generate and inspect to NUM", metavar="NUM")

parser.add_option("-b", "--bins", dest="numBins", type=int,
                help="assign number of bins to use in bin_by_duration.py to NUM", metavar="NUM")


(options, args) = parser.parse_args()
#print options.__dict__['numWF']
# * * * * * * * * * * * * * * * * * * * * * * * * *

if options.__dict__['numTemplates'] is not None:
        # Enter the number of vertices that the graph has here
        # AKA the number of templates to be clustered
        numNodes = options.__dict__['numTemplates']

        # Enter the number of clusters you want here
        n = options.__dict__['numBins']
else:
        sys.exit("Please specify an option -n NUM with number of waveforms to expect.")

# Chooses the directory to dump the plots and the .npy waveforms.
plots_directory = './waveform_graphs'

# If there isn't a folder in the directory, it creates one.
if not os.path.exists(plots_directory):
        os.makedirs(plots_directory)

g=igraph.Graph.Read_Ncol("./waveform_complete_graphs/%s/all.ncol" % (str(numNodes)))

weights1 = g.es['weight']
weights1 = np.around(weights1, 3)

# Converts it to undirected graph
g.to_undirected(combine_edges="first")

# 'graph2.to_undirected()' strips the graph of its weights
# so we restore them to the "weight" attribute after
g.es["weight"] = weights1
g.es['label'] = g.es['weight']

g.vs['label'] = [0] * len(g.vs)

a = []
edgeWeights = []
edgeLabels = []
neighborList = []

for r in range(len(g.vs)):
     a.append('%s' % str(r))
g.vs['label'] = a

for r in range(len(g.es['weight'])):
    edgeWeights.append(r)
    edgeLabels.append(r)

for r in range(len(g.vs)):
     a.append('%s' % str(r))
g.vs['label'] = a

color_list = ['red','blue','green',
              'cyan','pink','orange',
              'grey','yellow','white',
              'black','purple']

print '\n'

com3 = g.community_edge_betweenness(clusters=3, directed=False, weights='weight')
print 'Cluster by: Edge betweenness'
print(com3.as_clustering(n))
com3AsClustering = com3.as_clustering(n)
#toPlot = igraph.plot(com3.as_clustering(n), bbox=[2000,2000])
#toPlot.save('./waveform_graph_plots/plot_%s_edge_betweenness.jpg' % str(numNodes))

print '\n'

com5 = g.community_walktrap(weights='weight',steps=4)
print 'Cluster by: Walktrap'
print(com5.as_clustering(n))
com5AsClustering = com5.as_clustering(n)
#toPlot = igraph.plot(com5.as_clustering(n), bbox=[2000,2000], vertex_color=[color_list[x] for x in com5AsClustering.membership])
#toPlot.save('./waveform_graph_plots/plot_%s_walktrap.jpg' % str(numNodes))

print '\n'

com6 = g.community_fastgreedy(weights='weight')
print 'Cluster by: Fastgreedy'
print(com6.as_clustering(n))
#toPlot = igraph.plot(com6.as_clustering(n), bbox=[2000,2000])
#toPlot.save('./waveform_graph_plots/plot_%s_fastgreedy.jpg' % str(numNodes))

print '\n'

com7 = g.community_multilevel(weights='weight')
print 'Cluster by: Multilevel'
print(com7)
#toPlot = igraph.plot(com7, bbox=[2000,2000],vertex_color=[color_list[x] for x in com7.membership])
#toPlot.save('./waveform_graph_plots/plot_%s_multilevel.jpg' % str(numNodes))


