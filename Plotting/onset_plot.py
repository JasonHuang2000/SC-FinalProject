import numpy as np
import os
import json
import matplotlib.pyplot as plt
import sys

def readgt(gt_fp):
    onset = []
    offset = []
    pitch = []
    for line in gt_fp:
        sep = line.split(' ')
        onset.append(float(sep[0]))
        offset.append(float(sep[1]))
        pitch.append(float(sep[2]))
    return onset, offset, pitch

def main(features, gt_onset, gt_offset, gt_pitch, onset_peaks):

    time = features['time']
    vp = onset_peaks['vp']
    ee = onset_peaks['ee']
    sf = onset_peaks['sf']
    start = int(int(sys.argv[2])/0.032)
    end = start + 100

    fig, onset = plt.subplots(figsize=(12.5,3))

    onset.set_xlabel('time (s)')

    flag = 0
    for t in gt_onset:
        if t >= time[end]:
            break
        if t > time[start]:
            if flag == 0:
                onset.vlines(t, 0, 1, label='groundtruth')
                flag = 1
            else:
                onset.vlines(t, 0, 1)

    flag = 0
    # print(vp)
    for i in range(len(vp)):
        if vp[i] >= time[end]:
            break
        if vp[i] > time[start]:
            if flag == 0:
                onset.vlines(vp[i], 0, 1, colors='r', linestyles='dashed', label='vocal_pitch')
                flag = 1
            else:
                onset.vlines(vp[i], 0, 1, colors='r', linestyles='dashed')

    flag = 0
    for t in ee:
        if t >= time[end]:
            break
        if t > time[start]:
            if flag == 0:
                onset.vlines(t, 0, 1, colors='g', linestyles='dashdot', label='energy_entropy')
                flag = 1
            else:
                onset.vlines(t, 0, 1, colors='g', linestyles='dashdot')

    flag = 0
    for t in sf:
        if t >= time[end]:
            break
        if t > time[start]:
            if flag == 0:
                onset.vlines(t, 0, 1, colors='b', linestyles='dotted', label='spectral_entropy')
                flag = 1
            else:
                onset.vlines(t, 0, 1, colors='b', linestyles='dotted')

    onset.set_yticklabels([])
    fig.legend()

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":

    # train-set

    features = json.load(open("../MIR-ST500/" + sys.argv[1] + "/" + sys.argv[1] + "_feature.json"))
    onset_peaks = json.load(open("../MIR-ST500/" + sys.argv[1] + "/" + sys.argv[1] + ".onset_peaks"))
    gt_fp = open("../MIR-ST500/" + sys.argv[1] + "/" + sys.argv[1] + "_groundtruth.txt")
    gt_onset, gt_offset, gt_pitch = readgt(gt_fp)

    # test set

    # features = json.load(open("AIcup_testset_ok/" + sys.argv[1] + "/" + sys.argv[1] + "_feature.json"))
    # gt_onset = []
    # gt_offset = []
    # gt_pitch = []
    main(features, gt_onset, gt_offset, gt_pitch, onset_peaks)
