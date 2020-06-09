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

def main(features, gt_onset, gt_offset, gt_pitch):

    start = int(int(sys.argv[2])/0.032)
    end = start + 150

    fig, ax1 = plt.subplots(figsize=(12.5,6))

    v_pitch = features["vocal_pitch"]
    time = features["time"]
    color = 'tab:red'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('v_pitch', color=color)
    ax1.plot(time[start:end], v_pitch[start:end] , color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    if sys.argv[3] == '0':
        s_entp = features["spectral_entropy"]
        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel('s_entp', color=color)  # we already handled the x-label with ax1
        ax2.plot(time[start:end], s_entp[start:end], color=color)
        ax2.tick_params(axis='y', labelcolor=color)

    if sys.argv[3] == '1':
        s_flux = features["spectral_flux"]
        ax3 = ax1.twinx()
        color = 'tab:blue'
        ax3.set_ylabel('s_flux', color=color)  # we already handled the x-label with ax1
        ax3.plot(time[start:end], s_flux[start:end], color=color)
        ax3.tick_params(axis='y', labelcolor=color)

    if sys.argv[3] == '2':
        s_rolloff = features["spectral_rolloff"]
        ax5 = ax1.twinx()
        color = 'tab:blue'
        ax5.set_ylabel('s_rolloff', color=color)  # we already handled the x-label with ax1
        ax5.plot(time[start:end], s_rolloff[start:end], color=color)
        ax5.tick_params(axis='y', labelcolor=color)

    if sys.argv[3] == '3':
        zcr = features["zcr"]
        ax4 = ax1.twinx()
        color = 'tab:blue'
        ax4.set_ylabel('zcr', color=color)  # we already handled the x-label with ax1
        ax4.plot(time[start:end], zcr[start:end], color=color)
        ax4.tick_params(axis='y', labelcolor=color)

    if sys.argv[3] == '4':
        energy = features["energy"]
        ax5 = ax1.twinx()
        color = 'tab:blue'
        ax5.set_ylabel('energy', color=color)  # we already handled the x-label with ax1
        ax5.plot(time[start:end], energy[start:end], color=color)
        ax5.tick_params(axis='y', labelcolor=color)

    if sys.argv[3] == '5':
        energy_entp = features["energy_entropy"]
        ax5 = ax1.twinx()
        color = 'tab:blue'
        ax5.set_ylabel('energy_entp', color=color)  # we already handled the x-label with ax1
        ax5.plot(time[start:end], energy_entp[start:end], color=color)
        ax5.tick_params(axis='y', labelcolor=color)

    onset = ax1.twinx()
    for t in gt_onset:
        if t >= time[end]:
            break
        if t > time[start]:
            onset.vlines(t, 0, 1, linestyles='dashed')

    onset.set_yticklabels([])

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    # train-set
    features = json.load(open("MIR-ST500/" + sys.argv[1] + "/" + sys.argv[1] + "_feature.json"))
    gt_fp = open("MIR-ST500/" + sys.argv[1] + "/" + sys.argv[1] + "_groundtruth.txt")
    gt_onset, gt_offset, gt_pitch = readgt(gt_fp)
    # test set
    # features = json.load(open("AIcup_testset_ok/" + sys.argv[1] + "/" + sys.argv[1] + "_feature.json"))
    # gt_onset = []
    # gt_offset = []
    # gt_pitch = []
    main(features, gt_onset, gt_offset, gt_pitch)
