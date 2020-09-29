from icecube import icetray, dataio, dataclasses, simclasses, phys_services, recclasses
import os, sys
import numpy as np
import matplotlib as mpl
from matplotlib.colors import LogNorm, Normalize
import matplotlib.pyplot as plt
import timeit as time
import math
from datetime import datetime
import timeit

# Added by JP
# Define the directory of your files
files_dir = '/data/icecube/domeff_analysis/reco_sim_nominal/0000000-0000999'
# List the contents of the entire directory
file_list_aux = os.listdir(files_dir)
# Only keep those that are I3 files
file_list = [x for x in file_list_aux if '.i3.bz2' in x]
print('Total files', len(file_list))

nfiles = 1
frame_arr = []; mctree = []
track_list = []
for i in range(nfiles):
    # This is your code, but I changed the file name creation
    with dataio.I3File(os.path.join(files_dir, file_list[i])) as infile:
        for frame in infile:
            if infile.stream.id != 'P': continue
            frame_arr.append(frame)
            mctree.append(frame['I3MCTree']) 
            
            
            
volume_radius = 500. 
volume_top    = 500.


counter_single = 0
counter_multi_reject = 0

def counters(volume_radius, volume_top, counter_single, counter_multi_reject):
    muon_index = np.zeros(len(frame_arr),dtype=int)
    for index, frame in enumerate(frame_arr):
        mmc_tracks = frame['MMCTrackList']
    
        if len(mmc_tracks) == 1:
            muon_index[index] = 0
            counter_single += 1
        else:
        # If more than one muon in the event, I need to find out their decay point
        # And whether they entered the detector
            muons_in_volume = 0
            for itrack, one_track in enumerate(mmc_tracks):
            # Check if the closest approach of the muon to the origin is within the detector radius
                if (np.sqrt(one_track.xc**2 + one_track.yc**2) < volume_radius) and (-volume_top<one_track.zc<volume_top):
                # If I land here, this muon could have entered my volume. Let's find out where it decayed
                    if one_track.particle.shift_along_track(one_track.particle.length).z < volume_top:
                    # This muon decayed under 500m, so it entered the volume.              
                        muons_in_volume += 1
                        muon_index[index] = itrack
        # After looping, check how many muons in volume I counted. If more than one, this is a bad event!
            if muons_in_volume > 1:
                muon_index[index] = -1
                counter_multi_reject += 1
    return counter_single, counter_multi_reject, muon_index
    

    
def stochastic_losses(single, multi, volume_radius, volume_top, muon_index):

    e_stochastic = []



    for i, frame in enumerate(frame_arr):
        # JP: I changed this to run over single muons and fake bundles
        if muon_index[i] < 0:
        # It's a real bundle, don't go there
            continue
        
        mmc_tr = frame['MMCTrackList'][int(muon_index[i])]
        mctree = frame['I3MCTree']
 



    # This is necessary. First get all the daughters
        daughters=(mctree.get_daughters(mmc_tr.particle))

    # Then look for the daughters inside the volume. I added the volume definition in a new block of code
    # First loop over the daughters and start the energy loss counter
        e_stochastic.append(0)
        for d in daughters:
        # Check their position, only count if inside the volume
            if (d.pos.z <= volume_top) and (np.sqrt(d.pos.x**2 + d.pos.y**2)< volume_radius):
            # Sum the energy of the daughter to the last entry of the counter (index -1)
                e_stochastic[-1] += d.energy
    
            

    daughters = np.array(daughters)
    e_stochastic = np.array(e_stochastic)
     
    return e_stochastic    
