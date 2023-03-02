#!/usr/bin/env python

# JACK'S IMPORTS * * * * * * * * * * * * * * * *
import igraph
import os
import optparse
import sys
# * * * * * * * * * * * * * * * * * * * * * * *

from glue.ligolw import ligolw
from glue.ligolw import lsctables
from glue.ligolw import utils as ligolw_utils
from lalinspiral.sbank.bank import Bank
import lal
import lalsimulation as lalsim
import numpy as np
from lalinspiral.sbank.psds import get_neighborhood_ASD, get_neighborhood_PSD, get_PSD, get_neighborhood_df_fmax
from lalinspiral.sbank.psds import noise_models, read_psd, get_PSD
from scipy.interpolate import UnivariateSpline
from lalinspiral.sbank.waveforms import waveforms
import lalinspiral.sbank.waveforms as wf
from lalinspiral import CreateSBankWorkspaceCache
from lalinspiral import InspiralSBankComputeMatch
from lal import CreateCOMPLEX8FrequencySeries

class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
    pass


lsctables.use_in(LIGOLWContentHandler)

xmldoc = ligolw_utils.load_filename("H1-TMPLTBANK-966393725-2048.xml", contenthandler=LIGOLWContentHandler)
template_bank = lsctables.SnglInspiralTable.get_table(xmldoc)


# We may want to sort the waveforms by duration before and then feed them
# in to this algorithm after that, so that we can just take the first 100,
# etc...

# PARSER OPTIONS * * * * * * * * * * * * * * * * * *
parser = optparse.OptionParser()
parser.add_option("-n", "--number", dest="numNodes", type=int,
                  help="assign number of waveforms to generate and inspect to NUM", metavar="NUM")

parser.add_option("-b", "--bins", dest="numBins", type=int,
                  help="assign number of bins to use in bin_by_duration.py to NUM", metavar="NUM")

(options, args) = parser.parse_args()
# print options.__dict__['numWF']
# * * * * * * * * * * * * * * * * * * * * * * * * * 



if options.__dict__['numNodes'] != None:
    # Enter the number of vertices that the graph has here
    # AKA the number of templates to be clustered
    numNodes = options.__dict__['numNodes']
    selectTop = options.__dict__['numBins']
else:
    sys.exit("Please specify an option -n NUM with number of waveforms to expect.")

g = igraph.Graph.Read_Ncol("./waveform_complete_graphs/%s_waveform_complete_graph.ncol" % (str(numNodes)))

weights1 = g.es['weight']
weights1 = np.around(weights1, 3)

# Converts it to undirected graph
g.to_undirected(combine_edges="first")

# 'graph2.to_undirected()' strips the graph of its weights
# so we restore them to the "weight" attribute after
g.es["weight"] = weights1
g.es['label'] = g.es['weight']

# g.es['weight'] = [0] * len(g.es)
# g.es['label'] = [0] * len(g.es)
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

# Vars for duration calculation
fmin = 20.0
chi = 0

durArr = []
countArr = []

# Creates duration index
for t in range(numNodes):
    # Duration calculation
    chi = lalsim.SimIMRPhenomBComputeChi(
        template_bank[t].mass1,  # Mass 1
        template_bank[t].mass2,  # Mass 2
        template_bank[t].spin1z,  # Spin 1 Z
        template_bank[t].spin2z  # Sping 2 Z
    )
    dur = 1.1 * lalsim.SimIMRSEOBNRv2ChirpTimeSingleSpin(template_bank[t].mass1 * lal.MSUN_SI,
                                                         template_bank[t].mass2 * lal.MSUN_SI, chi, fmin)
    durArr.append(dur)
    countArr.append(t)
# Sort countArr using values from durArr
index = [x for (y, x) in sorted(zip(durArr, countArr))]  # FIXME: This is an index

print "Generating duration list..."
print "Waveform 0 is shortest, with ascending order..."

for m in range(len(index)):
    print "For waveform # %s, (originally # %s)" % (str(m), str(index[m])), " , the duration is %s" % str(
        durArr[index[m]])

neighborObjArr = []
weightNumArr = []
count = 0
neighborEdge = []
aBin = []
bins = []
for counter in range(numNodes):
    # Clears the list of neighbors to the old vertex
    to_bin = []
    neighborList = []
    weightNumArr = []
    neighborEdge = []
    neighborObjArr = []
    vertexObjArr = []
    vertexObjArr = []
    # Sets the new vertex of interest
    # if primaryVertex doesn't exist, we skip the iteration
    try:
        primaryVertex = g.vs.find(label='%s' % str(index[counter]))
    except:
        continue

    # This is a list of neighbors of 'node'
    neighborList = primaryVertex.neighbors()

    # Assigns the source vertex
    source = primaryVertex

    for counter1 in neighborList:
        # This finds the source and target nodes
        target = g.vs.find(label='%s' % str(int(counter1['label'])))

        # Appends the target to 'vertexObjArr'.
        vertexObjArr.append(target)

        # print 'from ', str(counter), ' to ', str(int(counter1['label']))
        # This step finds the neighboring veretx corresponding to 'counter1'
        try:
            neighborEdge = g.es.find(_source=source.index, _target=target.index)
        except ValueError:
            neighborEdge = g.es.find(_source=target.index, _target=source.index)

        # Appends the edge between source and target to 'neighborObjArr'
        neighborObjArr.append(neighborEdge)

        # This appends the weight of the edge to 'weightNumArr'
        weightNumArr.append(neighborEdge['weight'])

        # Sort neighborObjArr using values from weightNumArr
        sortedEdgeArr = [x for (y, x) in sorted(zip(weightNumArr, neighborObjArr))]

        # Sort vertexObjArr using values from weightNumArr
        sortedVertexArr = [x for (y, x) in sorted(zip(weightNumArr, vertexObjArr))]

    # Now 'sortedEdgeArr' is an array of edge objects sorted based on the
    # value of edge 'weight'.

    # Now 'sortedVertexArr' is an array of edge objects sorted based on the
    # value of edge 'weight' between source and target.

    # Now we select the top 'selectTop' elements of 'sortedVertexArr'
    to_bin = sortedVertexArr[0:selectTop - 1]

    # Now we finally add the source vertex to the beginning of the bin.
    to_bin.insert(0, source)

    # We collect all the templates labels to go to a single bin into an array
    for x in range(len(to_bin)):
        aBin.append(to_bin[x]['label'])

    # We append the array to a 2D array of bins
    bins.append(aBin)

    # Local clean up
    aBin = []
    g.delete_vertices(to_bin)
    to_bin = []

# Global clean up...
# bins[-1].append(g.vs['label'][0])

# Print results of the binning...
print bins

for x in range(len(bins)):
    print '[%s]' % str(x), ':',
    for y in range(len(bins[x])):
        print bins[x][y], ',',
    print '\n'
