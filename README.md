### Introduction

Welcome to my Laser Interferometer Gravitational-Wave Observatory (LIGO) project! At one time in my career, I worked with LIGO to research ways to improve the sensitivity of their gravitational wave detection-instrument.

Here, I'll give an overview of my the project I worked on, providing details with little `code snippets`. However, I can't guarantee that the provided snippets will work today, since LIGO's `GstLAL` Python libraries have probably changed a lot since I did my work.

### LIGO

At the time I did my research, LIGO had already made their first direct observation of a gravitational wave, which happened on the 14th of September in 2015.

### The Detections

The LIGO instruments detected gravitational waves emanating out from merging binary black hole systems, confirming Einstein's theory of relativity in new ways.

There are three distinct stages of a black hole merger.

- **Inspiral:** For black holes with masses similar to those of the black holes detected by LIGO, the inspiral phase can last for millions or even billions of years. This is because the gravitational waves emitted during the inspiral phase are very weak, and it takes a long time for the black holes to lose enough energy and angular momentum to come into close enough proximity to merge.

- **Merger:** This is the phase during which the black holes actually collide and merge into a single black hole, is much shorter than the inspiral phase. This phase, in sharp contrast to the inspiral phase, lasts on the order of a few milliseconds to a few seconds.

	The merger phase is characterized by a rapid increase in the amplitude of the gravitational waves emitted by the system, as the black holes come into close proximity and collide. 

- **Ringdown:** But even after the black holes in the binary system merge, they still aren't finished emitting gravitational waves.
	
	The black hole merger is super-chaotic, and represents an enormous perturbation to the system. Any perturbed system will naturally resonate at its normal mode; black holes are no different. When the binaries come together, the resulting black hole "rings" at it's "quasinormal modes" through a stage we call the ringdown.

They all come together to make a gravitational wave signature that looks like this.

wave-signature.jpg

The parameters of different binary black hole systems, as you can imagine, result in wildly different binary black hole signatures.

There were lots of

### My Job

<!-- Maybe you can pepper code snippets into the introcution for more interest, variation, and dramatic effect. -->

My job was to analyze and categorize different kinds of (purely theoretical) gravitational waveforms using raw characteristics identified by the `GSTlal` Python library. My ultimate goal was to figure out if I could group these waveforms in a way that would make the instrument even more sensitive to real-life detections.

What does that all mean? If you're confused, read on. I will explain everything—from theory to implementation—in great detail.

There are a lot of moving parts at LIGO, so in this project, we will focus on my work on gravitational waveform "classification," or "binning"!

But what is binning with respect to gravitational wave detection?


<!-- Les's email -->
When you do a search in gstlal, you estimate the background (i.e. the characteristics of the noise) by binning the search’s template bank and calculating the background of the entire bin and applying it to each template in the bin. (The background should really be done individually for each template, but the statistics are not large enough, thus the need for binning.) The binning was done in different ways at the time and on physical parameters, like mass/spin or duration, but I thought we could come up with a better strategy that optimized the likeness of templates within each bin. My thinking was that this would improve sensitivity.  However, our initial findings were actually quite surprising. We found that a random binning actually improves the sensitivity the most.  I still think we discovered a flaw in the group’s thinking about template binning, which is that you should bin to optimize sensitivity.  I think instead we need to recognize that the background estimate assumes templates within a given bin are similar, and if they are not, then you can end up with artificially boosted sensitivities.

Also, I think we found that walktrap "worked" best

---

# Background

LIGO is a large physics experiment that detects, and conducts research on, gravitational waves. These waves are ripples in the fabric of space-time that are caused by the acceleration of massive objects, such as merging black holes or neutron stars. During my research, I focused on detecting gravitational wave signatures from "intermediate mass black holes," which are a certain mass-class of black hole that emit waves for a specific duration, and at specific evolving frequency ranges.

LIGO consists of two detectors located in Hanford, Washington and Livingston, Louisiana. These detectors use lasers and mirrors to measure the extremely small changes in distance that result from the passage of a gravitational wave.

Increasing the sensitivity of LIGO's detectors is critical because it allows scientists to detect gravitational waves from increasingly distant sources. This, in turn, allows them to study a wider range of celestial objects and phenomena, including some that may be too far away or too faint to be observed in other ways.

Because the scales involved are so extreme, scientists and engineers at LIGO are constantly trying to find new ways to increase the sensitivity of the instrument.

# Instrument Sensitivity

At these simultaneously extreme microscopic and microscopic scales, instrument sensitivity depends a lot on the precision and quality of your hardware and your software. A lot can chan

# The Software

`GstLAL` **(Generalized s-transform Time-domain LIGO Algorithm Library)** is a software package developed by the LIGO Scientific Collaboration (LSC) used to analyze data from LIGO's gravitational wave detectors.

One of the main uses of `GstLAL` is to compare the data off the detector to how we'd expect gravitational waveforms to show up on the detector, and looking for matches or correlations between the two.

`GstLAL` includes a number of tools and algorithms that are specifically designed to optimize the search for gravitational waves. For example, it includes tools for generating theoretical templates, for filtering and conditioning the data, and for calculating statistical significance.

# Binning

Waveform binning is a technique that is used to group gravitational waveforms into categories or bins based on certain characteristics or features. This can be useful for a number of purposes, such as improving the efficiency of gravitational wave searches, or for classifying gravitational waves based on their source or other properties.

In the context of `GstLAL`, waveform binning is used to improve the sensitivity of gravitational wave searches by allowing analysts to focus on specific regions of the parameter space where gravitational waves are more likely to be found. By binning the waveforms by certain features, analysts can reduce the number of templates that need to be searched and thereby increase the speed and efficiency of the analysis.

Waveform binning can be performed using a variety of methods, such as clustering algorithms or machine learning techniques. The specific method used will depend on the goals of the analysis and the characteristics of the data.

Overall, waveform binning is a useful tool for improving the efficiency and effectiveness of gravitational wave searches, and it is an important part of the analysis process in `GstLAL`.

# Outline

- Parameter space overview
- How enormous parameter space is, even for a small sliver of gravitational wave sources
- Ways to use binning to increase the efficiency of the parameter space search
- Sensitivity-efficiency tradeoffs involved in binning
- Minimizing sensitivity loss

In the context of LIGO and `GstLAL`, the parameter space refers to the vast multidimensional space that represents the possible values of the parameters that describe a gravitational wave signal. These parameters may include the masses and spins of the objects that generated the wave, the distance to the source, and the orientation of the wave relative to the detector.

The parameter space for gravitational wave sources is very large, even for a small sliver of the total possibilities of black holes. You have to consider .... ...

One way to increase the efficiency of the search through parameter space is to use binning to group waveforms into like categories based on their characteristics. Approaching it this way has many benefits, as it..
- ... can allow analysts to focus their search on specific regions of the parameter space where gravitational waves are more likely to be found, rather than having to search the entire space. This can increase sensitivity
- ... can create


However, there are sensitivity-efficiency tradeoffs involved in binning, as it can potentially reduce the sensitivity of the detection if it leads to the loss of important information or the neglect of certain regions of the parameter space. To minimize this sensitivity loss, it is important to choose a binning method and parameters that are appropriate for the specific goals of the analysis and the characteristics of the data.

There are several ways to minimize sensitivity loss when using binning, such as choosing a binning method that preserves as much information as possible, or using multiple rounds of binning with progressively finer bin sizes. It is also important to carefully consider the tradeoffs between sensitivity and efficiency and to choose a binning strategy that strikes a good balance between the two.

The way we reduce sensitivity loss is though the algorithm that we choose to bin.

# Critical files

