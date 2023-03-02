#!/usr/bin/env python

# Imports - FIXME: I don't think all these are needed!
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

# Read in template bank from sngl_inspiral table
class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
                            pass
lsctables.use_in(LIGOLWContentHandler)
xmldoc = ligolw_utils.load_filename("H1-TMPLTBANK-966393725-2048.xml", contenthandler = LIGOLWContentHandler)
template_bank = lsctables.SnglInspiralTable.get_table(xmldoc)

# Set some params
duration = 32. # Set duration
f_low = 20. # in Hz
f_high = 4096. # in Hz
amporder = 0
order = -1
approximant = 'EOBNRv2' # waveform

# Generate waveform
hplus,hcross = lalsim.SimInspiralFD(
                        0., # phase
                        1.0 / duration, # sampling interval
                        lal.MSUN_SI * template_bank[0].mass1, # mass1
                        lal.MSUN_SI * template_bank[0].mass2, # mass2
                        template_bank[0].spin1x, #spins
                        template_bank[0].spin1y,
                        template_bank[0].spin1z,
                        template_bank[0].spin2x,
                        template_bank[0].spin2y,
                        template_bank[0].spin2z,
                        f_low,
                        f_high,
                        0., #FIXME chosen until suitable default value for f_ref is defined
                        1.e6 * lal.PC_SI, # distance
                        0., # redshift
                        0., # inclination
                        0., # tidal deformability lambda 1
                        0., # tidal deformability lambda 2
                        None, # waveform flags
                        None, # Non GR params
                        amporder,
                        order,
                        lalsim.GetApproximantFromString(str(approximant))
                        )

# Read in PSD and make it usable
psd = read_psd('H1L1V1-REFERENCE_PSD-966386126-24805.xml.gz')['H1']
f_orig = psd.f0 + np.arange(len(psd.data)) * psd.deltaF
f_max_orig = max(f_orig)
interpolator = UnivariateSpline(f_orig, np.log(psd.data), s=0)
noise_model = lambda g: np.where(g < f_max_orig, np.exp(interpolator(g)), np.inf)
PSD = get_PSD(1./duration, f_low, f_high, noise_model)

# Create workspace for match calculation
workspace_cache = CreateSBankWorkspaceCache()

# Pack up waveform into something usable by match function
fs = hplus
new = CreateCOMPLEX8FrequencySeries(fs.name, fs.epoch, fs.f0, fs.deltaF, fs.sampleUnits, fs.data.length
)
new.data.data[:] = fs.data.data[:]

# Whiten waveform
ASD = np.sqrt(PSD)
new.data.data /= ASD

# Normalize waveform
sigmasq = float(np.vdot(new.data.data, new.data.data).real * 4 * 1./duration)
new.data.data /= sigmasq**0.5

# Calculate match of waveform with itself
print InspiralSBankComputeMatch(new,new,workspace_cache)

