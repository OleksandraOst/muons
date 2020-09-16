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

muon_index = np.zeros(len(frame_arr),dtype=int)
counter_single = 0
counter_multi_reject = 0



gcd_file = '/cvmfs/icecube.opensciencegrid.org/data/GCD/GeoCalibDetectorStatus_IC86_Merged.i3.gz'
gfile = dataio.I3File(gcd_file)
gframe = gfile.pop_frame()

def dis(single, multi,  volume_radius, volume_top):
    charge = []
    times = []
    min_time_ar = []
    mydom = []
    distance = []
 

    for i, frame in enumerate(frame_arr):
        # JP: I changed this to run over single muons and fake bundles
        if muon_index[i] < 0:
        # It's a real bundle, don't go there
            continue            
            
        mmctracks = frame['MMCTrackList']
        mctree = frame['I3MCTree']
        pulses = frame['SRTInIcePulsesDOMeff'].apply(frame)
        one_dom = pulses.items()
        mmctracks = frame['MMCTrackList']
        geometry = gframe['I3Geometry']
        
    
    for i in range(len(one_dom)):
        Omkey= one_dom[i][0]
        and_time = one_dom[i][1]
        #print(Omkey,and_time)

        value = []
        char = 0
        for pulse in one_dom[i][1]:
            time_pulse = 0
            time_pulse += pulse.time
            value.append(time_pulse)
            times.append(time_pulse)
        
            char += pulse.charge
            if char > 0 :
                charge.append(char)
    

    min_time_ar.append(min(value))

 
    
    for i in range(len(value)-1):
        if times[len(times) - i - 1] != min_time_ar: del times[len(times) - i - 1]


    track = mmctracks[0].particle
     

    
   
    for i in range(len(one_dom)):
        dom = geometry.omgeo[one_dom[i][0]]    
        mydom.append(dom) 
        

 
    
    for i in range(len(mydom)):
        
        d = phys_services.I3Calculator.cherenkov_distance(track, mydom[i].position)
        distance.append(d)
        
    return distance, charge, mydom, times



#dis distance between last and first doms

def between(times, mydom):
    
    for i, frame in enumerate(frame_arr):
        # JP: I changed this to run over single muons and fake bundles
        if muon_index[i] < 0:
        # It's a real bundle, don't go there
            continue            
            
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
   
    dis = np.sqrt((x_f - x_e)**2 + (y_f - y_e)**2 + (z_f - z_e)**2)
    return dis



def charge(distance, charge):
    
    corrected_charge = []
    for i in range(len(distance)):
        att_length = 50. 
        if distance[i] <= 200.0:
            corrected = charge[i]*distance[i]
            corrected_charge.append(corrected)
        
    
    return corrected_charge   
