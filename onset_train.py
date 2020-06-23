import argparse
import os
import sys
import librosa
import mido
import json
import numpy as np
from scipy import stats
import time
import mir_eval as mir
import math

from scipy import signal
from scipy.signal import find_peaks
from statistics import median

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class Note:
    def __init__(self, frame, frame_pitch, onset_time, offset_time, onset_idx, offset_idx):
        self.frame_pitch = frame_pitch
        self.frame = frame
        self.onset_time = onset_time
        self.offset_time = offset_time
        self.onset_idx = onset_idx
        self.pitch = 0
        self.offset_idx = offset_idx

def get_onset(feature):
    time = feature['time']
    energy_entp = np.array(feature['energy_entropy'])
    v_pitch = feature['vocal_pitch']

    vp_delta1 = []
    vp_delta2 = []
    for i in range(len(v_pitch)-1):
        vp_delta2.append(v_pitch[i+1] - v_pitch[i])
        if ( v_pitch[i+1] - v_pitch[i] ) > -30:
            vp_delta1.append(abs(v_pitch[i]-v_pitch[i+1]))
        else:
            vp_delta1.append(0)

    peaks, _ = find_peaks(-energy_entp, height=-3.2, prominence=0.18, distance=3) 
    # peaks, _ = find_peaks(-energy_entp, height=-3.2, prominence=0.2) 

    onset_times = []
    onset_idxs = []
    offset_times = []
    offset_idxs = []
    delta = 1
    # delta = 2

    for i in range(len(peaks)):
        if int(peaks[i])+delta >= 0 and int(peaks[i])+delta < len(time):
            onset_times.append(time[int(peaks[i])+delta])
            onset_idxs.append(int(peaks[i]+delta))
        else:
            onset_times.append(time[int(peaks[i])])
            onset_idxs.append(int(peaks[i]))

    vpd_idx = 0
    for i in range(len(onset_times) - 1):
        flag = 0
        while vpd_idx < len(vp_delta2) and time[vpd_idx] < onset_times[i]:
            vpd_idx += 1
        while vpd_idx < len(vp_delta2) and time[vpd_idx] < onset_times[i+1]:
            if vp_delta2[vpd_idx] <= -30:
                flag = 1
                break
            vpd_idx += 1
        # if flag == 1 and vpd_idx+50 < len(time) and time[vpd_idx+50] < onset_times[i+1] :
        #     offset_times.append(time[vpd_idx + 50])
        #     offset_idxs.append(vpd_idx + 50)
        # else:
        offset_times.append(time[vpd_idx])
        offset_idxs.append(vpd_idx)
    while vpd_idx < len(vp_delta2) and time[vpd_idx] < onset_times[-1]:
        vpd_idx += 1
    while vpd_idx < len(vp_delta2) and vp_delta2[vpd_idx] > -30:
        vpd_idx += 1
    offset_times.append(time[vpd_idx])
    offset_idxs.append(vpd_idx)

    return onset_times, onset_idxs, offset_times, offset_idxs


def generate_notes(onset_times, onset_idxs, offset_times, offset_idxs, ep_frames):
    notes = []
    onset_num = 0
    cur_frame = []
    cur_pitch = []

    for time, pitch in ep_frames:

        if (onset_num+ 1) < len(onset_times) and time > (offset_times[onset_num]- 0.016):

            note= Note(frame= cur_frame, frame_pitch= cur_pitch, onset_time= onset_times[onset_num]
                , offset_time= offset_times[onset_num], onset_idx = onset_idxs[onset_num], offset_idx= offset_idxs[onset_num])
            notes.append(note)
            
            cur_frame= []
            cur_pitch= []
            onset_num= onset_num+ 1

        if time > (onset_times[onset_num]- 0.016):
            cur_frame.append(time)
            cur_pitch.append(pitch)

    if cur_frame != []:
        note= Note(frame= cur_frame, frame_pitch= cur_pitch, onset_time= onset_times[onset_num]
            , offset_time= offset_times[onset_num], onset_idx = onset_idxs[onset_num], offset_idx= offset_idxs[onset_num])
        notes.append(note)
        
    return notes

def get_note_level_pitch(notes):
    for note in notes:
        voiced_note= 0
        total= 0

        # median method
        v_note = []

        # for i in range(5, len(note.frame_pitch)-4):
        for i in range(note.offset_idx - note.onset_idx):
            if note.frame_pitch[i] > 5:
                voiced_note= voiced_note+ 1

                # total= total+ note.frame_pitch[i]
                # v_note.append(note.frame_pitch[i])
                v_note.append(int(note.frame_pitch[i]))
                # v_note.append(round(note.frame_pitch[i]))
                # v_note.append(math.ceil(note.frame_pitch[i]))

        if voiced_note == 0:
            note.pitch= 0
        else:
            # note.pitch= round( total / float(voiced_note) ) #comment this to use median method
            # note.pitch = round(median(v_note))
            note.pitch = int(stats.mode(v_note)[0][0]) + 1

    return notes

def get_offset(notes, feature):

    # for note in notes:
        # if note.pitch != 0:

            # for i in range(len(note.frame_pitch)):
            #     if note.frame_pitch[i] > 0:
            #         offset= i
            
            # if offset > 2:
                # note.offset_time= note.frame[offset]

    # spectral_entropy offset-method
    s_etp = feature["spectral_entropy"]

    for note in notes:
        offset = 0
        for i in range(note.onset_idx, note.onset_idx+len(note.frame_pitch)-1):
            if i > 5 and s_etp[i] >= 0.65:
                break
            offset += 1

        if offset > 2:
            note.offset_time= note.frame[offset]
            note.offset_idx = offset

    return notes

def get_pitch_after_offset(notes):
    for note in notes:
        v_notes = [note.frame_pitch[i] for i in range(note.offset_idx)]
        if len(v_notes) > 0:
            note.pitch = round(median(v_notes)) 

    return notes

def main(ep_path, feature_path):
    
    ep_frames = json.load(open(ep_path))
    feature = json.load(open(feature_path))

    onset_times, onset_idxs, offset_times, offset_idxs = get_onset(feature)

    notes = generate_notes(onset_times, onset_idxs, offset_times, offset_idxs, ep_frames)
    notes = get_note_level_pitch(notes)
    # notes = get_offset(notes, feature)
    # notes = get_pitch_after_offset(notes)

    est_interval = []
    est_pitch = []
    for note in notes:
        if note.pitch > 0 and note.onset_time != note.offset_time:
            est_interval.append([note.onset_time, note.offset_time])
            est_pitch.append(note.pitch)

    return np.array(est_interval), np.array(est_pitch)


if __name__ == '__main__':

    total = 0
    for i in range(1, 501):
        ep_path = "MIR-ST500/" + str(i) + "/" + str(i) + "_vocal.json" 
        feature_path = "MIR-ST500/" + str(i) + "/" + str(i) + "_feature.json" 
        est_intervals, est_pitches = main(ep_path, feature_path)

        ref_intervals, ref_pitches = mir.io.load_valued_intervals("MIR-ST500/" + str(i) + "/" + str(i) + "_groundtruth.txt")
        scores = mir.transcription.evaluate(ref_intervals, ref_pitches, est_intervals, est_pitches)

        s = scores['Onset_F-measure']*0.2 + scores['F-measure_no_offset']*0.6 + scores['F-measure']*0.2
        total += s
        print(i, end='\r')

    print(total/500)


                        
