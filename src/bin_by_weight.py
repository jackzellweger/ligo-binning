#!/usr/bin/env python

# Project Imports * * * * * * * * * * * * * * * *
import sys
import os
import copy
import csv
import numpy as np
import itertools
import igraph
import optparse
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


class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
        pass

lsctables.use_in(LIGOLWContentHandler)

xmldoc = ligolw_utils.load_filename("H1-TMPLTBANK-966393725-2048.xml", contenthandler=LIGOLWContentHandler)
template_bank = lsctables.SnglInspiralTable.get_table(xmldoc)

# PARSER OPTIONS * * * * * * * * * * * * * * * * * *
print "Reading options..."
parser = optparse.OptionParser()
parser.add_option("-n", "--number", dest="numTemplates", type=int,
                                  help="assign number of waveforms to generate and inspect to NUM", metavar="NUM")

parser.add_option("-b", "--bins", dest="numBins", type=int,
                                  help="assign number of bins to use in bin_by_duration.py to NUM", metavar="NUM")

parser.add_option("-t", "--touse", dest="toUse", type=int,
                                  help="Assigns the number of the clustering alg. to use to NUM", metavar="NUM")

(options, args) = parser.parse_args()
# * * * * * * * * * * * * * * * * * * * * * * * * *

toUse = options.__dict__['toUse']

if options.__dict__['numTemplates'] is not None:
        # Enter the number of vertices that the graph has here
        # AKA the number of templates to be clustered
        numNodes = options.__dict__['numTemplates']

        # Enter the number of clusters you want here
        n = options.__dict__['numBins']
else:
        sys.exit("Please specify an option -n NUM with number of waveforms to expect.")

# Chooses the directory to dump the plots
plots_directory = './bin_plots'

# If there isn't a folder in the directory, it creates one.
print "Checking for direcotry path..."
if not os.path.exists(plots_directory):
        os.makedirs(plots_directory)

print "Importing graph..."
g = igraph.Graph.Read_Ncol("./waveform_complete_graphs/all_%s/all.txt" % (str(numNodes)), directed=False)
# NOW 'g' is an UNDIRECTED graph

a = []
edgeWeights = []
edgeLabels = []
neighborList = []

color_list = ['red', 'blue', 'green',
                          'cyan', 'pink', 'orange',
                          'grey', 'yellow', 'white',
                          'black', 'purple']


# THE WALK TRAP ALGORITHM
com5 = g.community_walktrap(weights='weight', steps=4)
print 'Cluster by: Walktrap'
print(com5.as_clustering(n))

com5AsClustering = com5.as_clustering(n)
toPlot = igraph.plot(com5.as_clustering(n), bbox=[2000,2000], vertex_color=[color_list[x] for x in com5AsClustering.membership])
toPlot.save(plots_directory + '/walktrap_bin_by_weight_%s_graph.png' % str(len(list(com5AsClustering))))

# Plotting...
corM1 = copy.deepcopy(list(com5AsClustering))
corM2 = copy.deepcopy(list(com5AsClustering))
for x in range(len(com5AsClustering)):
        for y in range(len(com5AsClustering[x])):
                corM1[x][y] = template_bank[int(com5AsClustering[x][y])].mass1
                print "corM1:", corM1[x][y]
                print "template_bank M1:", template_bank[int(com5AsClustering[x][y])].mass1
                print " "

                corM2[x][y] = template_bank[int(com5AsClustering[x][y])].mass2
                print "corM2:", corM2[x][y]
                print "template_bank M2:", template_bank[int(com5AsClustering[x][y])].mass2
                print " "

number = len(com5AsClustering)
cmap = plt.get_cmap('gnuplot')
colors = [cmap(i) for i in np.linspace(0, 1, number)]

for i, color in enumerate(colors, start=1):
        plt.plot(corM1[i - 1], corM2[i - 1], "o", markersize=3, markeredgewidth=0.0, color=color,
                         label='Bin {i}'.format(i=i))
        # print i
plt.legend(loc='best')

plt.savefig(plots_directory + '/walktrap_bin_by_weight_%s_plot.png' % str(len(list(com5AsClustering))), dpi=1000)

plt.close()
