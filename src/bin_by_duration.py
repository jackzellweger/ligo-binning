#!/usr/bin/env python

# Project Imports * * * * * * * * * * * * * * * *
import copy
import igraph
import os
import optparse
import sys
import matplotlib
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt
# * * * * * * * * * * * * * * * * * * * * * * *

# LalSuite Imports * * * * * * * * * * * * * * * *
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
# * * * * * * * * * * * * * * * * * * * * * * *

# Template bank initialization * * * * * * * * * * * * * * * *
class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
    pass
lsctables.use_in(LIGOLWContentHandler)
xmldoc = ligolw_utils.load_filename("H1-TMPLTBANK-966393725-2048.xml", contenthandler=LIGOLWContentHandler)
template_bank = lsctables.SnglInspiralTable.get_table(xmldoc)
# * * * * * * * * * * * * * * * * * * * * * * *

# PARSER OPTIONS * * * * * * * * * * * * * * * * * *
parser = optparse.OptionParser()
parser.add_option("-n", "--number", dest="numNodes", type=int,
                  help="assign number of waveforms to generate and inspect to NUM", metavar="NUM")
parser.add_option("-b", "--bins", dest="numBins", type=int,
                  help="Select the size of the bins to use, assigns to NUM", metavar="NUM")
(options, args) = parser.parse_args()
# * * * * * * * * * * * * * * * * * * * * * * * * *

if options.__dict__['numNodes'] is not None:
    numNodes = options.__dict__['numNodes']
    selectTop = options.__dict__['numBins']
else:
    sys.exit("Please specify an option -n NUM with number of waveforms to expect.")

# Chooses the directory to dump the plots
plots_directory = './bin_plots'

# If there isn't a folder in the directory, it creates one.
if not os.path.exists(plots_directory):
    os.makedirs(plots_directory)

# Create an igraph graph object with 'g'
g = igraph.Graph.Read_Ncol("./waveform_complete_graphs/all_%u/all.txt" % numNodes)

# Initialize graph labels
# 'es' is the edge array
# 'vs' is the vertex array
g.es['label'] = g.es['weight']
g.vs['label'] = [0] * len(g.vs)

# Instantiate index and tracking lists
a = []
edgeWeights = []
edgeLabels = []
neighborList = []

# Create a unique id for each vertex
# with the first vertex = 1 and the
# last equal to len(g.vs)-1.
for r in range(len(g.vs)):
    a.append('%s' % str(r))

# Assign index values to label
# values in graph object
g.vs['label'] = a

# Declare vars for duration
# calculation
fmin = 20.0
chi = 0

# Declare arrays to handle duration
# calculations
durArr = []
countArr = []

# Create duration index
for t in range(numNodes):
    # Perform duration calculation
    chi = lalsim.SimIMRPhenomBComputeChi(
        template_bank[t].mass1,  # Mass 1
        template_bank[t].mass2,  # Mass 2
        template_bank[t].spin1z,  # Spin 1 Z
        template_bank[t].spin2z  # Sping 2 Z
    )
    dur = 1.1 * lalsim.SimIMRSEOBNRv2ChirpTimeSingleSpin(template_bank[t].mass1 * lal.MSUN_SI,
                                                         template_bank[t].mass2 * lal.MSUN_SI,
                                                         chi,
                                                         fmin)
    # Append the calculate duration to 'durArr'
    durArr.append(dur)

    # Create an array [0, 1, 2, 3 ..., len(numNodes)-1]
    countArr.append(t)

# Set the duration label of each
# vertex in graph object
g.vs['duration'] = durArr

# Sort countArr using values from durArr,
# and assign it to 'index' array.
# The he n'th value in 'index' corresponds to
# where the n'th shortest waveform is in 'durArr'
index = [x for (y, x) in sorted(zip(durArr, countArr))]

# Instantiate more index and tracking lists
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
    except ValueError:
        continue

    # This is a list of neighbors of 'node'
    neighborList = primaryVertex.neighbors()

    # Assigns the source vertex
    source = primaryVertex

    for counter1 in neighborList:

        # Finds the target node
        target = g.vs.find(label='%s' % counter1['label'])

        # Appends the target to 'vertexObjArr'.
        vertexObjArr.append(target)

        # Finds the edge between 'source' and 'target'
        try:
            neighborEdge = g.es.find(_source=source.index, _target=target.index)
        except ValueError:
            neighborEdge = g.es.find(_source=target.index, _target=source.index)

        # Appends the edge between source and target to 'neighborObjArr'
        neighborObjArr.append(neighborEdge)

        # Appends the weight of the edge to 'weightNumArr'
        weightNumArr.append(neighborEdge['weight'])

    # Sort neighborObjArr using values from weightNumArr
    sortedEdgeArr = [x for (y, x) in sorted(zip(weightNumArr, neighborObjArr))]

    # Sort vertexObjArr using values from weightNumArr
    sortedVertexArr = [x for (y, x) in sorted(zip(weightNumArr, vertexObjArr))]

    '''
    AT THIS POINT
    'sortedEdgeArr' is an array of edge objects sorted based on the
    value of edge 'weight'. 'sortedVertexArr' is an array of edge
    objects sorted based on the value of edge 'weight' between source and target.
    '''

    # Now we select the bottom 'selectTop' elements of 'sortedVertexArr'
    to_bin = sortedVertexArr[len(sortedVertexArr) - (selectTop - 1):]

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

# Print results of the binning
print bins

# Generate plots
corM1 = copy.deepcopy(bins)
corM2 = copy.deepcopy(bins)

for x in range(len(bins)):
    for y in range(len(bins[x])):
        corM1[x][y] = template_bank[int(bins[x][y])].mass1
        corM2[x][y] = template_bank[int(bins[x][y])].mass2

number = len(bins)
cmap = plt.get_cmap('gnuplot')
colors = [cmap(i) for i in np.linspace(0, 1, number)]

for i, color in enumerate(colors, start=1):
    plt.plot(corM1[i - 1], corM2[i - 1], "o", markersize=3, markeredgewidth=0.0, color=color,
             label='Bin %s: %s Members' % (i, len(corM2[i-1])))

plt.legend(loc='best')
plt.savefig('./bin_plots/%s_bin_plot.png' % str(len(bins)), dpi=1000)
plt.close()

