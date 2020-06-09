import numpy as np
import os
import json
import matplotlib.pyplot as plt
import sys

def main(features):

    start = 2000
    end = 2100

    s_flux = features["spectral_flux"]
    s_entp = features["spectral_entropy"]
    v_pitch = features["vocal_pitch"]
    time = features["time"]

    fig, ax1 = plt.subplots(figsize=(12.5,6))

    color = 'tab:red'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('v_pitch', color=color)
    ax1.plot(time[start:end], v_pitch[start:end] , color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('s_entp', color=color)  # we already handled the x-label with ax1
    ax2.plot(time[start:end], s_entp[start:end], color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    # ax3 = ax1.twinx()
    # color = 'tab:green'
    # ax3.set_ylabel('s_flux', color=color)  # we already handled the x-label with ax1
    # ax3.plot(time[start:end], s_flux[start:end], color=color)
    # ax3.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    features = json.load(open(sys.argv[1]))
    main(features)
