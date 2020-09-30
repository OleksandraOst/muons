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

muon_index = counters(volume_radius, volume_top, counter_single, counter_multi_reject)[2] 




def func(frame,frame_arr, counter_single,counter_multi_reject,  volume_radius, volume_top, muon_index):
    
    corrected_charge = []
    distance = []
    charge = []
    times = []
    value = []
    mydom = []
    min_time_ar = []
    
    for i, frame in enumerate(frame_arr):
       
        #if muon_index[i] < 0:
        
         #   continue
        
        mmc_tr = frame['MMCTrackList'][int(muon_index[i])]
        mctree = frame['I3MCTree']
        pulses = frame['SRTInIcePulsesDOMeff'].apply(frame)
        one_dom = pulses.items()
    

    
        gcd_file = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_IC86_Merged.i3.gz'
        gfile = dataio.I3File(gcd_file)
        gframe = gfile.pop_frame()
        geometry = gframe['I3Geometry']
        
        for i in range(len(one_dom)):
            Omkey= one_dom[i][0]
            and_time = one_dom[i][1]
        

        
        char = 0
        for pulse in one_dom[i][1]:
            time_pulse = 0
            time_pulse += pulse.time
            char += pulse.charge
            
            value.append(time_pulse)
        
        charge.append(char)
        times.append(time_pulse)

        
        for i in range(len(one_dom)):
            dom = geometry.omgeo[one_dom[i][0]]
        mydom.append(dom)
        

        mmctracks = frame['MMCTrackList']
        track = mmctracks[0].particle
        x_f = y_f = z_f = 0
        x_e = y_e = z_e = 0
        for i in range(len(mydom)):
            if times[i] == max(times):
                x_f = mydom[i].position.x
                y_f = mydom[i].position.y
                z_f = mydom[i].position.z
            
        for i in range(len(mydom)):
            if times[i] == min(times):
                x_e = mydom[i].position.x
                y_e = mydom[i].position.y
                z_e = mydom[i].position.z
   
        distance_between = np.sqrt((x_f - x_e)**2 + (y_f - y_e)**2 + (z_f - z_e)**2)
        
        
        for i in range(len(mydom)):
            d = phys_services.I3Calculator.cherenkov_distance(track, mydom[i].position)
        distance.append(d)
        
        
        
        corrected = 0
        
        for i in range(len(distance)):
            att_length = 50. 
            if distance[i] <= 200.0:corrected = charge[i]*distance[i]
        corrected_charge.append(corrected)
    
    corrected_charge = np.array(corrected_charge)
    distance = np.array(distance)
    times = np.array(times)
    value = np.array(value)

    return corrected_charge, distance_between