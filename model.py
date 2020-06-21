import os
import sys
import librosa
import json
import numpy as np
from scipy import stats
import time

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

def isEmptyNote(peaks, v_pitch, idx):
    for i in range(-5, 6):
        if (idx + i) >= 0 and (idx + i) < len(v_pitch) and v_pitch[idx+i] < 1:
            return False
    return True

def isNoteEnding(peaks, vp_delta2, idx):
    for i in range(-5, 6):
        if (idx + i) >= 0 and (idx + i) < len(vp_delta2) and vp_delta2[idx+i] < -30:
            return True
    return False

def get_onset(feature):
    time = feature['time']
    spectral_flux = np.array(feature['spectral_flux'])
    energy_entp = np.array(feature['energy_entropy'])
    v_pitch = feature['vocal_pitch']

    # # vp-method

    # vp_delta1 = []
    # vp_delta2 = []
    # for i in range(len(v_pitch)-1):
    #     vp_delta2.append(v_pitch[i+1] - v_pitch[i])
    #     if ( v_pitch[i+1] - v_pitch[i] ) > -30:
    #         vp_delta1.append(abs(v_pitch[i]-v_pitch[i+1]))
    #     else:
    #         vp_delta1.append(0)

    # peaks, _ = find_peaks(vp_delta1, height=0.5, distance=4)
    # vp_peaks = vp_peaks + 1


    # ee-method
    # peaks, _ = find_peaks(-energy_entp, height=-3.2, prominence=0.2) Test-set best
    peaks, _ = find_peaks(-energy_entp, height=-3.2, prominence=0.18, distance=3) 


    # sf-method
    # value for prominence
    p = 0.016 #high score : 0.245 w/ 0.02425

    # values for height
    h = 0.02288 #high score : 0.266 w/ 0.02288
    # low = spectral_flux[int(len(spectral_flux)*0.13)] #high score : 0.261
    
    # high score : 0.269 w/ p = 0.016 and h = 0.02288
    # sf_peaks, _ = find_peaks(spectral_flux, height=0.015, prominence=0.01, distance=3) #use prominence= or height= or both
    # sf_peaks = sf_peaks - 1

   
    # epsilon = 15 # .1 sec
    # vpsf_peaks = []
    # vp_idx = 0
    # sf_idx = 0

    # while vp_idx < len(vp_peaks):
    #     flag = 0
    #     while sf_idx < len(sf_peaks) and sf_peaks[sf_idx] <= vp_peaks[vp_idx]+epsilon:
    #         if abs(sf_peaks[sf_idx] - vp_peaks[vp_idx]) <= epsilon:
    #             vpsf_peaks.append(vp_peaks[vp_idx])
    #             flag = 1
    #             sf_idx += 1
    #             break
    #         sf_idx += 1
    #     if flag == 0:
    #         vpsf_peaks.append(vp_peaks[vp_idx])
    #     vp_idx += 1

    # while vp_idx < len(vp_peaks):
    #     while sf_idx < len(sf_peaks) and sf_peaks[sf_idx] <= vp_peaks[vp_idx]+epsilon:
    #         if abs(sf_peaks[sf_idx] - vp_peaks[vp_idx]) > epsilon:
    #             vpsf_peaks.append(sf_peaks[sf_idx])
    #         sf_idx += 1
    #     vpsf_peaks.append(vp_peaks[vp_idx])
    #     vp_idx += 1

    # peaks = []
    # ee_idx = 0
    # vpsf_idx = 0

    # while ee_idx < len(ee_peaks):
    #     flag = 0
    #     while vpsf_idx < len(vpsf_peaks) and vpsf_peaks[vpsf_idx] <= ee_peaks[ee_idx]+epsilon:
    #         if abs(vpsf_peaks[vpsf_idx] - ee_peaks[ee_idx]) <= epsilon:
    #             peaks.append(ee_peaks[ee_idx])
    #             flag = 1
    #             vpsf_idx += 1
    #             break
    #         vpsf_idx += 1
    #     if flag == 0:
    #         peaks.append(ee_peaks[ee_idx])
    #     ee_idx += 1

    # while ee_idx < len(ee_peaks):
    #     while vpsf_idx < len(vpsf_peaks) and vpsf_peaks[vpsf_idx] <= ee_peaks[ee_idx]+epsilon:
    #         if abs(vpsf_peaks[vpsf_idx] - ee_peaks[ee_idx]) > epsilon:
    #             peaks.append(vpsf_peaks[vpsf_idx])
    #         vpsf_idx += 1
    #     peaks.append(ee_peaks[ee_idx])
    #     ee_idx += 1

    onset_times = []
    onset_idxs = []
    # delta = 2 # test-set best
    delta = 1

    # for i in range(len(peaks)):
    #     if isEmptyNote(peaks, v_pitch, i) == False:
    #         if int(peaks[i])+delta >= 0 and int(peaks[i])+delta < len(time):
    #             onset_times.append(time[int(peaks[i])+delta])
    #             onset_idxs.append(int(peaks[i]+delta))
    #         else:
    #             onset_times.append(time[int(peaks[i])])
    #             onset_idxs.append(int(peaks[i]))

    for i in range(len(peaks)):
        if int(peaks[i])+delta >= 0 and int(peaks[i])+delta < len(time):
            onset_times.append(time[int(peaks[i])+delta])
            onset_idxs.append(int(peaks[i]+delta))
        else:
            onset_times.append(time[int(peaks[i])])
            onset_idxs.append(int(peaks[i]))

    # for i in range(len(ee_peaks)):
    #     # if isNoteEnding(ee_peaks, vp_delta2, i) == False:
    #     onset_times.append(time[int(ee_peaks[i])])
    #     onset_idxs.append(int(ee_peaks[i]))

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

        # for i in range(5, len(note.frame_pitch)-4):
        for i in range(len(note.frame_pitch)):
            if note.frame_pitch[i] > 5:
                voiced_note= voiced_note+ 1
                # total= total+ note.frame_pitch[i]

                # v_note.append(note.frame_pitch[i])
                v_note.append(int(note.frame_pitch[i]))

        if voiced_note == 0:
            note.pitch= 0
        else:
            # note.pitch= round( total / float(voiced_note) ) #comment this to use median method

            # note.pitch = round(median(v_note))

            note.pitch = int(stats.mode(v_note)[0][0]) + 1

    return notes

def get_offset(notes, feature):

    # for note in notes:
    #     if note.pitch != 0:
    #         for i in range(len(note.frame_pitch)):
    #             if note.frame_pitch[i] > 0:
    #                 offset= i
    #         if offset > 2:
    #             note.offset_time= note.frame[offset]

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

    onset_times, onset_idxs = get_onset(feature)

    notes = generate_notes(onset_times, onset_idxs, ep_frames)
    notes = get_note_level_pitch(notes)
    notes = get_offset(notes, feature)
    # notes = get_pitch_after_offset(notes)

    answer = []
    for note in notes:
        if note.pitch > 0 and note.onset_time != note.offset_time:
            answer.append([note.onset_time, note.offset_time, note.pitch])

    return answer


if __name__ == '__main__':

    # for testing

    # ep_path= "MIR-ST500/" + sys.argv[1] + "/" + sys.argv[1] + "_vocal.json"
    # feature_path= "MIR-ST500/" + sys.argv[1] + "/" + sys.argv[1] + "_feature.json"
    # answer = main(ep_path=ep_path, feature_path=feature_path)
    # for note in answer:
    #     print(note[0], note[1], note[2], sep=' ')
    
    # for generate answer

    AnswerDict = {}
    for i in range(1, 1501):
        ep_path = "AIcup_testset_ok/" + str(i) + "/" + str(i) + "_vocal.json"
        feature_path = "AIcup_testset_ok/" + str(i) + "/" + str(i) + "_feature.json"
        ans = main(ep_path=ep_path, feature_path=feature_path)
        AnswerDict[str(i)] = ans
    print(json.dumps(AnswerDict))
    AnswerDict.clear()

