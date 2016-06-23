#!/usr/bin/env python

'''
This is a script to import some LIGO XML Template Bank and outputs
a complete weighted graph in NCOL format.
- Each node corresponds to a template
- Each (undirected) edge corresponds to a comparison done between templates
- Each edge weight corresponds to the value returned by InspiralSBankComputeMatch()
for a comparison between two neighboring templates (nodes)

In the XML that this file accesses, all the spins are 0.
The masses are the only things that matter in this particular template bank # FIXME: Fact check this claim.
'''


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

# PARSER OPTIONS * * * * * * * * * * * * * * * * * *
parser = optparse.OptionParser()
parser.add_option("-n", "--number", dest="numTemplates", type=int,
                  help="assign number of waveforms to generate and inspect to NUM", metavar="NUM", default=10)

parser.add_option("-f", "--from", dest="generateFrom", type=int,
                  help="Start generating at the Nth waveform (inclusive)", metavar="N")

parser.add_option("-t", "--to", dest="generateTo", type=int,
                  help="Stop generating at the Nth waveform (exclusive)", metavar="N")

generateFrom = options.__dict__['generateFrom']
generateTo = options.__dict__['generateTo']

(options, args) = parser.parse_args()


# print options.__dict__['numWF']
# * * * * * * * * * * * * * * * * * * * * * * * * * 

class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
    pass


lsctables.use_in(LIGOLWContentHandler)

xmldoc = ligolw_utils.load_filename("H1-TMPLTBANK-966393725-2048.xml", contenthandler=LIGOLWContentHandler)
template_bank = lsctables.SnglInspiralTable.get_table(xmldoc)

# Set the number of templates here.
if options.__dict__['numTemplates'] != None:
    numTemplates = options.__dict__['numTemplates']
else:
    sys.exit("Please specify an option -n NUM with number of waveforms to generate and inspect.")

# 'duration' sets the duration of the waveform
duration = 32.

# 'f_low' is in Hz
f_low = 20.

# 'f_high' is in Hz
f_high = 4096.

# 'amorder' is...
amporder = 0

# 'order' is... 
order = -1

# 'approximant' is the waveform ...
approximant = 'EOBNRv2'

# Chooses the directory to dump the plots and the .npy waveforms.
plots_directory = './plots'
waveform_directory = './waveforms'
edge_lists_directory = './edge_lists'
waveform_complete_graph_directory = './waveform_complete_graphs'

# If there isn't a folder in the directory, it creates one.
if not os.path.exists(plots_directory):
    os.makedirs(plots_directory)
if not os.path.exists(waveform_directory):
    os.makedirs(waveform_directory)
if not os.path.exists(edge_lists_directory):
    os.makedirs(edge_lists_directory)
if not os.path.exists(waveform_complete_graph_directory):
    os.makedirs(waveform_complete_graph_directory)

# Create list of edge relations
print "Creating graph edges..."
edge_list = igraph.Graph.Full(numTemplates)

print "Writing .ncol of graph edges..."
# This writes an edge list!
edge_list.write("./edge_lists/edge_list_%s.ncol" % str(numTemplates), format='ncol')

# This loads the edge list from the exported file
# of the form:
# [[0,1], [0, 2]... [2,3], [3,4]]
print "Loading edge list..."
edge_array = np.loadtxt("./edge_lists/edge_list_%s.ncol" % str(numTemplates))
edge_array = edge_array[generateFrom:generateTo]

# Read in PSD and make it usable
print "Reading PSD..."
psd = read_psd('H1L1V1-REFERENCE_PSD-966386126-24805.xml.gz')['H1']
print "Preparing PSD..."
f_orig = psd.f0 + np.arange(len(psd.data)) * psd.deltaF
f_max_orig = max(f_orig)
interpolator = UnivariateSpline(f_orig, np.log(psd.data), s=0)
noise_model = lambda g: np.where(g < f_max_orig, np.exp(interpolator(g)), np.inf)
PSD = get_PSD(1. / duration, f_low, f_high, noise_model)

# Generate ASD
print "Generating ASD"
ASD = np.sqrt(PSD)

print "Creating workspace..."
# Create workspace for match calculation
workspace_cache = CreateSBankWorkspaceCache()

# Declare the array we are going to be using in match calculation
fs = [0, 0]
sigmasq = [0, 0]
new = [0, 0]
hplus = [0, 0]
hcross = [0, 0]

target = open("./waveform_complete_graphs/%s_waveform_complete_graph.ncol" % str(int(numTemplates)), 'w')

#  FIXME: We might want to add this once we change the other files to read in the new name
# target = open("./waveform_complete_graphs/%s/waveform_complete_graph_from_%s_to_%s_.ncol" % (str(numTemplates), str(generateFrom), str(generateTo)), 'w')

# Vars for duration calculation
fmin = 20.0
chi = 0

# TIME EXECUTION * * * * * * * * * * * * * * * * * *
import time

start_time = time.time()
# * * * * * * * * * * * * * * * * * * * * * * * * * *
durArr = []
countArr = []

for t in range(numTemplates):
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
index = [x for (y, x) in sorted(zip(durArr, countArr))] # FIXME: This is an index

print "Generating duration list..."
print "Waveform 0 is shortest, with ascending order..."

for m in range(len(index)):
    print "For waveform # %s, (originally # %s)" % (str(m), str(index[m])), " , the duration is %s" % str(
        durArr[index[m]])

print "Generating comparisons..."
# For loop to compare all waveforms to one another
for current in range(len(edge_array)):
    before = int(edge_array[current][0])
    after = int(edge_array[current][0])

    if current != 0:
        before = int(edge_array[current - 1][0])

    if (before == after and current != 0):
        r = 1
    # print "Not generating another template 0"
    else:
        r = 0
    # print "Generating a new template 0"

    for q in range(r, 2):
        # Loads current waveform
        # old: fs[q] = np.load("./waveforms/%s.npy" % str(int(edge_array[current][q])))
        hplus, hcross = lalsim.SimInspiralFD(
            0.,  # Phase
            1.0 / duration,  # Sampling interval
            lal.MSUN_SI * template_bank[int(edge_array[current][q])].mass1,  # Mass 1
            lal.MSUN_SI * template_bank[int(edge_array[current][q])].mass2,  # Mass 2
            template_bank[int(edge_array[current][q])].spin1x,  # Spins
            template_bank[int(edge_array[current][q])].spin1y,
            template_bank[int(edge_array[current][q])].spin1z,
            template_bank[int(edge_array[current][q])].spin2x,
            template_bank[int(edge_array[current][q])].spin2y,
            template_bank[int(edge_array[current][q])].spin2z,
            f_low,
            f_high,
            0.,  # FIXME: chosen until suitable default value for f_ref is defined
            1.e6 * lal.PC_SI,  # distance
            0.,  # Redshift
            0.,  # Inclination
            0.,  # Tidal deformability lambda 1
            0.,  # Tidal deformability lambda 2
            None,  # Waveform flags
            None,  # Non GR params
            amporder,
            order,
            lalsim.GetApproximantFromString(str(approximant))
        )

        fs[q] = hplus

        # FS: Pack up waveform into something usable by match function
        new[q] = CreateCOMPLEX8FrequencySeries(fs[q].name, fs[q].epoch, fs[q].f0, fs[q].deltaF, fs[q].sampleUnits,
                                               fs[q].data.length)
        new[q].data.data[:] = fs[q].data.data[:]

        # FS: Whiten waveform
        new[q].data.data /= ASD

        # FS: Normalize waveform
        sigmasq[q] = float(np.vdot(new[q].data.data, new[q].data.data).real * 4 * 1. / duration)
        new[q].data.data /= sigmasq[q] ** 0.5

    # Calculate match of each waveform with one another
    print '%s <-> %s : %s ' % (str(index[int(edge_array[current][0])]), str(index[int(edge_array[current][1])]),
                               str(InspiralSBankComputeMatch(new[0], new[1], workspace_cache)))

    target.write('%s %s %s' % (str(index[int(edge_array[current][0])]), str(index[int(edge_array[current][1])]),
                               str(InspiralSBankComputeMatch(new[0], new[1], workspace_cache))))

    target.write("\n")

# This generates a plot of the 'current' waveform.
# z = hplus.data.data
# plt.plot(z)
# plt.xlabel('time')
# plt.ylabel('strain')
# plt.savefig("./plots/plot_%s.png" % str(current))
# plt.close()
# This just saves the array of data of the waveform.
# np.save("./waveforms/%s.npy" % str(current), z)

# Print out execution time:     
print("Execution Time: %s seconds" % (time.time() - start_time))
