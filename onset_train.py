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

from scipy import signal
from scipy.signal import find_peaks
from statistics import median

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class Note:
    def __init__(self, frame, frame_pitch, onset_time, offset_time, onset_idx):
        self.frame_pitch = frame_pitch
        self.frame = frame
        self.onset_time = onset_time
        self.offset_time = offset_time
        self.onset_idx = onset_idx
        self.pitch = 0
        self.offset_idx = 0


def get_onset(feature, h, p, d):
    time = feature['time']
    spectral_flux = np.array(feature['spectral_flux'])
    energy_entp = np.array(feature['energy_entropy'])

    if d == 0:
        peaks, _ = find_peaks(-energy_entp, height=h, prominence=p) 
    else:
        peaks, _ = find_peaks(-energy_entp, height=h, prominence=p, distance=d) 

    onset_times = []
    onset_idxs = []
    for i in range(len(peaks)):
        onset_times.append(time[int(peaks[i])])
        onset_idxs.append(int(peaks[i]))

    return onset_times, onset_idxs


def generate_notes(onset_times, onset_idxs, ep_frames):
    notes = []
    onset_num = 0
    cur_frame = []
    cur_pitch = []

    for time, pitch in ep_frames:

        if (onset_num+ 1) < len(onset_times) and time > (onset_times[onset_num+ 1]- 0.016):

            note= Note(frame= cur_frame, frame_pitch= cur_pitch, onset_time= onset_times[onset_num]
                , offset_time= onset_times[onset_num+ 1], onset_idx = onset_idxs[onset_num])
            notes.append(note)
            
            cur_frame= []
            cur_pitch= []
            onset_num= onset_num+ 1

        if time > (onset_times[onset_num]- 0.016):
            cur_frame.append(time)
            cur_pitch.append(pitch)

    if cur_frame != []:
        note= Note(frame= cur_frame, frame_pitch= cur_pitch, onset_time= onset_times[onset_num]
            , offset_time= cur_frame[-1], onset_idx = onset_idxs[onset_num])
        notes.append(note)
        
    return notes

def get_note_level_pitch(notes):
    for note in notes:
        voiced_note= 0
        total= 0

        # median method
        v_note = []

        for i in range(len(note.frame_pitch)):
            if note.frame_pitch[i] > 0:
                voiced_note= voiced_note+ 1
                # total= total+ note.frame_pitch[i]

                v_note.append(note.frame_pitch[i])

        if voiced_note == 0:
            note.pitch= 0
        else:
            # note.pitch= round( total / float(voiced_note) ) #comment this to use median method

            note.pitch = round(median(v_note))

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

def main(ep_path, feature_path, h, p, d):
    
    ep_frames = json.load(open(ep_path))
    feature = json.load(open(feature_path))

    onset_times, onset_idxs = get_onset(feature, h, p, d)

    notes = generate_notes(onset_times, onset_idxs, ep_frames)
    notes = get_note_level_pitch(notes)
    notes = get_offset(notes, feature)
    # notes = get_pitch_after_offset(notes)

    est_interval = []
    est_pitch = []
    for note in notes:
        if note.pitch > 0 and note.onset_time != note.offset_time:
            est_interval.append([note.onset_time, note.offset_time])
            est_pitch.append(note.pitch)

    return np.array(est_interval), np.array(est_pitch)


if __name__ == '__main__':

    best = [0, 0, 0]
    best_score = 0

    for _h in range(20, 40):
        for _p in range(15):
            for d in range(10):
                h = -(_h/10)
                p = _p/10
                total_score = 0
                for i in range(1, 501):
                    ep_path = "MIR-ST500/" + str(i) + "/" + str(i) + "_vocal.json" 
                    feature_path = "MIR-ST500/" + str(i) + "/" + str(i) + "_feature.json" 
                    est_intervals, est_pitches = main(ep_path, feature_path, h, p, d)

                    ref_intervals, ref_pitches = mir.io.load_valued_intervals("MIR-ST500/" + str(i) + "/" + str(i) + "_groundtruth.txt")
                    scores = mir.transcription.evaluate(ref_intervals, ref_pitches, est_intervals, est_pitches)

                    s = scores['Onset_F-measure']*0.2 + scores['F-measure_no_offset']*0.6 + scores['F-measure']*0.2
                    print(i, s)
                    if s > best_score:
                        best_score = s
                        best = [h, p, d]

    print("Best: " + str(best))


                        
