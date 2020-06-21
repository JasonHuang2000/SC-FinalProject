import sys
import numpy as np
import json
from scipy.signal import find_peaks

def main(feature_path):

    feature = json.load(open(feature_path))
    time = feature['time']
    spectral_flux = np.array(feature['spectral_flux'])
    energy_entp = np.array(feature['energy_entropy'])
    v_pitch = feature['vocal_pitch']

    # vp-method
    vp_delta1 = []
    for i in range(len(v_pitch)-1):
        # vp_delta1.append(abs(v_pitch[i]-v_pitch[i+2]))
        if ( v_pitch[i+1] - v_pitch[i] ) > -30:
            vp_delta1.append(abs(v_pitch[i]-v_pitch[i+1]))
        else:
            vp_delta1.append(0)

    vp_peaks, _ = find_peaks(vp_delta1, height=0.5, distance=4)

    # ee-method
    ee_peaks, _ = find_peaks(-energy_entp, height=-3.1, prominence=0.1, distance=3) 
    # ee_peaks = ee_peaks

    # sf-method
    sf_peaks, _ = find_peaks(spectral_flux, height=0.03, prominence=0.01, distance=3) #use prominence= or height= or both
    # sf_peaks = sf_peaks

    vp_onset = []
    ee_onset = []
    sf_onset = []
    for vp in vp_peaks:
        vp_onset.append(time[vp])
    for ee in ee_peaks:
        ee_onset.append(time[ee])
    for sf in sf_peaks:
        sf_onset.append(time[sf])

    answerDict = {} 
    answerDict['vp'] = vp_onset
    answerDict['ee'] = ee_onset
    answerDict['sf'] = sf_onset
    return answerDict


if __name__ == '__main__':

    for i in range(1, 501):

        feature_path= "../MIR-ST500/" + str(i) + "/" + str(i) + "_feature.json"
        answer = main(feature_path=feature_path)

        output_file_path = "../MIR-ST500/" + str(i) + "/" + str(i) + ".onset_peaks"
        with open(output_file_path, 'w') as output_file:
            json.dump(answer, output_file) 

        print(i, end='\r')

