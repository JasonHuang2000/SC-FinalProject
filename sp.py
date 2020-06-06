import argparse
import os
import sys
import librosa
import mido
import json
import numpy as np
from scipy import stats
import time

from scipy import signal
from scipy.signal import find_peaks
from statistics import median

class Note:
    def __init__(self, frame, frame_pitch, onset_time, offset_time):
        self.frame_pitch = frame_pitch
        self.frame = frame
        self.onset_time = onset_time
        self.offset_time = offset_time
        self.pitch = 0

def get_onset(feature_path):
    feature = json.load(open(feature_path))
    spectral_flux = feature['spectral_flux']
    time = feature['time']

    # value for prominence
    p = 0.016 #high score : 0.245 w/ 0.02425

    # values for height
    h = 0.02288 #high score : 0.266 w/ 0.02288
    low = spectral_flux[int(len(spectral_flux)*0.13)] #high score : 0.261
    
    # high score : 0.269 w/ p = 0.016 and h = 0.02288

    # print(p)
    # print(h)
    # print(low)

    peaks, _ = find_peaks(spectral_flux, height = h, prominence = p) #use prominence= or height= or both

    onset_times = []
    for i in range(len(peaks)):
        onset_times.append(time[peaks[i]])

    return onset_times


def generate_notes(onset_times, ep_frames):
    notes = []
    onset_num = 0
    cur_frame = []
    cur_pitch = []

    for time, pitch in ep_frames:

        if (onset_num+ 1) < len(onset_times) and time > (onset_times[onset_num+ 1]- 0.016):

            note= Note(frame= cur_frame, frame_pitch= cur_pitch, onset_time= onset_times[onset_num]
                , offset_time= onset_times[onset_num+ 1])
            notes.append(note)
            
            cur_frame= []
            cur_pitch= []
            onset_num= onset_num+ 1

        if time > (onset_times[onset_num]- 0.016):
            cur_frame.append(time)
            cur_pitch.append(pitch)

    if cur_frame != []:
        note= Note(frame= cur_frame, frame_pitch= cur_pitch, onset_time= onset_times[onset_num]
            , offset_time= cur_frame[-1])
        notes.append(note)
        
    return notes

def get_note_level_pitch(notes):
    for note in notes:
        voiced_note= 0
        total= 0

        # median method
        # v_note = []

        for i in range(len(note.frame_pitch)):
            if note.frame_pitch[i] > 0:
                voiced_note= voiced_note+ 1
                total= total+ note.frame_pitch[i]

                # v_note.append(note.frame_pitch[i])

        if voiced_note == 0:
            note.pitch= 0
        else:
            note.pitch= round( total / float(voiced_note) ) #comment this to use median method

            # note.pitch = round(median(v_note))

    return notes

def get_offset(notes):

    for note in notes:
        if note.pitch != 0:
            offset= 0
            for i in range(len(note.frame_pitch)):
                if note.frame_pitch[i] > 0:
                    offset= i
            
            if offset > 2:
                note.offset_time= note.frame[offset]

    return notes


def main(ep_path, feature_path):
    
    ep_frames = json.load(open(ep_path))

    onset_times = get_onset(feature_path)

    notes = generate_notes(onset_times, ep_frames)
    notes = get_note_level_pitch(notes)
    notes = get_offset(notes)

    answer = []
    for note in notes:
        if note.pitch > 5 and note.onset_time != note.offset_time:
            print(note.onset_time, note.offset_time, note.pitch, sep=' ')


if __name__ == '__main__':

    ep_path= sys.argv[1]
    feature_path= sys.argv[2]
    main(ep_path=ep_path, feature_path=feature_path)
